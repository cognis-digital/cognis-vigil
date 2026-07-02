"""Small / point-target detection for search-and-rescue and tiny-vessel ISR.

Finds targets only a pixel or two wide in a much larger, cluttered scene — a
swimmer lost at sea, a small craft, a hiker against terrain — using two classic,
dependency-free techniques:

- **CA-CFAR** (cell-averaging constant-false-alarm-rate): for each pixel, estimate
  the local background mean/std from a ring of training cells (a guard band
  excludes the target itself), then flag pixels whose contrast exceeds k sigma.
  This is how radar/IR pull point targets out of sea or ground clutter.
- **Temporal background subtraction**: across video frames, subtract the per-pixel
  temporal median (static clutter/waves) so a moving or bobbing target stands out,
  then run CFAR on the residual.

Detections are non-kinetic search leads. See docs/LIMITATIONS.md.

An image is a 2-D list of intensity values (rows x cols), e.g. an IR band or a
grayscale/contrast channel.
"""

from __future__ import annotations

import statistics


def ca_cfar(image, guard: int = 1, train: int = 4, k: float = 5.0) -> list:
    """Return [(row, col, snr)] for pixels exceeding k sigma over local background."""
    H = len(image)
    W = len(image[0]) if H else 0
    hits = []
    span = guard + train
    for r in range(H):
        for c in range(W):
            vals = []
            for dr in range(-span, span + 1):
                for dc in range(-span, span + 1):
                    if abs(dr) <= guard and abs(dc) <= guard:
                        continue  # skip cell-under-test + guard band
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < H and 0 <= cc < W:
                        vals.append(image[rr][cc])
            if len(vals) < 8:
                continue
            mean = sum(vals) / len(vals)
            std = statistics.pstdev(vals)
            if std <= 0:
                continue
            snr = (image[r][c] - mean) / std
            if snr >= k:
                hits.append((r, c, snr))
    return hits


def _cluster(hits) -> list:
    """8-connected clustering of hit pixels into blobs (centroid, size, peak SNR)."""
    snr_at = {(r, c): s for r, c, s in hits}
    seen = set()
    blobs = []
    for start in snr_at:
        if start in seen:
            continue
        stack = [start]
        comp = []
        while stack:
            p = stack.pop()
            if p in seen or p not in snr_at:
                continue
            seen.add(p)
            comp.append(p)
            pr, pc = p
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    q = (pr + dr, pc + dc)
                    if q in snr_at and q not in seen:
                        stack.append(q)
        rows = [p[0] for p in comp]
        cols = [p[1] for p in comp]
        blobs.append({"row": round(sum(rows) / len(rows), 2),
                      "col": round(sum(cols) / len(cols), 2),
                      "size": len(comp),
                      "peak_snr": round(max(snr_at[p] for p in comp), 2)})
    return blobs


def detect_small_targets(image, k: float = 5.0, guard: int = 1, train: int = 4,
                         max_size: int = 8) -> list:
    """Detect small/point targets. Returns candidate blobs sorted by confidence.
    Blobs larger than max_size pixels are treated as extended features, not
    point targets, and dropped."""
    blobs = [b for b in _cluster(ca_cfar(image, guard, train, k)) if b["size"] <= max_size]
    for b in blobs:
        # confidence rises with SNR, favors compact (few-pixel) detections
        b["confidence"] = round(min(0.99, (b["peak_snr"] / (k * 2)) * (1.0 / (1 + 0.15 * (b["size"] - 1)))), 4)
    blobs.sort(key=lambda b: -b["confidence"])
    return blobs


def temporal_residual(frames) -> list:
    """Per-pixel max deviation from the temporal median across frames — suppresses
    static clutter (waves, terrain) so moving/bobbing targets survive."""
    H = len(frames[0])
    W = len(frames[0][0])
    resid = [[0.0] * W for _ in range(H)]
    for r in range(H):
        for c in range(W):
            series = [f[r][c] for f in frames]
            med = statistics.median(series)
            resid[r][c] = max(abs(v - med) for v in series)
    return resid


def detect_in_video(frames, k: float = 5.0, **kw) -> list:
    """Detect small moving/persistent targets across a stack of frames."""
    return detect_small_targets(temporal_residual(frames), k=k, **kw)
