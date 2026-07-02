"""Small / point-target detection for search-and-rescue and tiny-vessel ISR.

Pulls a 1-2 pixel target — a swimmer lost at sea, a small craft, a hiker — out of
a large cluttered scene, dependency-free:

- **CA-CFAR** (cell-averaging constant-false-alarm-rate): per-pixel contrast over a
  ring of local training cells (a guard band excludes the target). The threshold is
  expressed in sigma, and can be derived from a target probability-of-false-alarm
  (`pfa_to_k`) so the operating point is chosen by required false-alarm rate.
- **Temporal background subtraction** (`detect_in_video`): suppress static clutter
  (waves, terrain) so a moving/bobbing target survives.
- **SNR frame-stacking** (`detect_with_stacking`): coherently average N registered
  frames to raise a faint static target ~sqrt(N) in SNR — recovering targets below
  single-frame detectability.

Detections are non-kinetic search leads. See docs/LIMITATIONS.md and docs/COMPLIANCE.md.
An image is a 2-D list of intensity values (rows x cols).
"""

from __future__ import annotations

import statistics
from statistics import NormalDist


def pfa_to_k(pfa: float) -> float:
    """Convert a target probability of false alarm to a CFAR threshold in sigma
    (one-sided Gaussian). e.g. Pfa 1e-4 -> ~3.72 sigma, 1e-6 -> ~4.75 sigma."""
    pfa = min(max(pfa, 1e-12), 0.5)
    return round(NormalDist().inv_cdf(1.0 - pfa), 4)


def snr_map(image, guard: int = 1, train: int = 4) -> list:
    """Dense per-pixel CA-CFAR SNR surface (sigma over local background)."""
    H = len(image)
    W = len(image[0]) if H else 0
    out = [[0.0] * W for _ in range(H)]
    span = guard + train
    for r in range(H):
        for c in range(W):
            vals = []
            for dr in range(-span, span + 1):
                for dc in range(-span, span + 1):
                    if abs(dr) <= guard and abs(dc) <= guard:
                        continue
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < H and 0 <= cc < W:
                        vals.append(image[rr][cc])
            if len(vals) < 8:
                continue
            mean = sum(vals) / len(vals)
            std = statistics.pstdev(vals)
            if std > 0:
                out[r][c] = (image[r][c] - mean) / std
    return out


def _cluster(snr, k, max_size):
    H = len(snr)
    W = len(snr[0]) if H else 0
    hit = {(r, c): snr[r][c] for r in range(H) for c in range(W) if snr[r][c] >= k}
    seen, blobs = set(), []
    for start in hit:
        if start in seen:
            continue
        stack, comp = [start], []
        while stack:
            p = stack.pop()
            if p in seen or p not in hit:
                continue
            seen.add(p)
            comp.append(p)
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    q = (p[0] + dr, p[1] + dc)
                    if q in hit and q not in seen:
                        stack.append(q)
        if len(comp) > max_size:
            continue
        rows = [p[0] for p in comp]
        cols = [p[1] for p in comp]
        peak = max(hit[p] for p in comp)
        blobs.append({"row": round(sum(rows) / len(rows), 2),
                      "col": round(sum(cols) / len(cols), 2),
                      "size": len(comp), "peak_snr": round(peak, 2),
                      "confidence": round(min(0.99, (peak / (k * 2)) *
                                              (1.0 / (1 + 0.15 * (len(comp) - 1)))), 4)})
    blobs.sort(key=lambda b: -b["confidence"])
    return blobs


def detect_small_targets(image, k: float = 5.0, guard: int = 1, train: int = 4,
                         max_size: int = 8, pfa: float = None) -> list:
    if not image or not image[0]:
        return []
    if pfa is not None:
        k = pfa_to_k(pfa)
    return _cluster(snr_map(image, guard, train), k, max_size)


def temporal_residual(frames) -> list:
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


def stack_frames(frames) -> list:
    """Coherent (registered) average of frames — raises a static target ~sqrt(N)
    in SNR by averaging down zero-mean clutter."""
    n = len(frames)
    H = len(frames[0])
    W = len(frames[0][0])
    return [[sum(frames[i][r][c] for i in range(n)) / n for c in range(W)] for r in range(H)]


def detect_with_stacking(frames, k: float = 5.0, **kw) -> list:
    """Detect a faint STATIC target by SNR-stacking frames before CFAR."""
    return detect_small_targets(stack_frames(frames), k=k, **kw)
