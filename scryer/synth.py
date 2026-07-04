"""Deterministic synthetic multi-sensor ISR scenario with planted ground truth.

Generates moving contacts observed by multiple sensors. Most maritime contacts
carry AIS (cooperative); a few are "dark" (radar/EO only) — the planted targets
the cross-cue must recover. Synthetic; measures fusion correctness, not fielded
accuracy.
"""

from __future__ import annotations

import random

from .model import Detection


def generate(seed: int = 20, n_maritime: int = 8, n_dark: int = 3, n_air: int = 4,
             fixes: int = 6, step_s: float = 300.0):
    rng = random.Random(seed)
    dets = []
    truth = {}          # detection_id -> true track id
    dark_truth = set()  # true track ids that are dark
    tid = 0
    did = 0

    def emit(track_id, lat, lon, ts, sensor, domain):
        nonlocal did
        did += 1
        d = Detection(id=f"d{did}", ts=ts, lat=round(lat, 5), lon=round(lon, 5),
                      sensor=sensor, domain=domain, source=sensor.upper())
        dets.append(d)
        truth[d.id] = track_id

    def track(domain, sensors, base_lat, base_lon, heading):
        nonlocal tid
        tid += 1
        track_id = f"T{tid}"
        lat, lon = base_lat, base_lon
        t0 = 1_700_000_000.0
        for i in range(fixes):
            ts = t0 + i * step_s
            lat += heading[0] * 0.01
            lon += heading[1] * 0.01
            for s in sensors:
                jlat = lat + rng.uniform(-0.001, 0.001)
                jlon = lon + rng.uniform(-0.001, 0.001)
                emit(track_id, jlat, jlon, ts, s, domain)
        return track_id

    for _ in range(n_maritime):
        track("maritime", ["radar", "eo", "ais"],
              rng.uniform(8.5, 10.5), rng.uniform(-80.0, -78.0),
              (rng.choice([-1, 1]) * rng.random(), rng.choice([-1, 1]) * rng.random()))
    for _ in range(n_dark):
        t = track("maritime", ["radar", "eo"],
                  rng.uniform(8.5, 10.5), rng.uniform(-80.0, -78.0),
                  (rng.choice([-1, 1]) * rng.random(), rng.choice([-1, 1]) * rng.random()))
        dark_truth.add(t)
    for _ in range(n_air):
        track("air", ["radar", "adsb"],
              rng.uniform(8.5, 10.5), rng.uniform(-80.0, -78.0),
              (rng.choice([-1, 1]) * rng.random(), rng.choice([-1, 1]) * rng.random()))

    rng.shuffle(dets)
    return dets, {"detection_track": truth, "dark_tracks": dark_truth}


def scene_with_targets(seed=40, H=64, W=64, n_targets=5, clutter=0.05, amp=0.45):
    """A cluttered EO/IR scene with a handful of planted 1-pixel targets
    (~9 sigma over clutter). Returns (image, planted_pixels)."""
    rng = random.Random(seed)
    img = [[max(0.0, rng.gauss(0.2, clutter)) for _ in range(W)] for _ in range(H)]
    truth = set()
    for _ in range(n_targets):
        r, c = rng.randint(5, H - 6), rng.randint(5, W - 6)
        img[r][c] += amp
        truth.add((r, c))
    return img, truth


def video_faint_static(seed=43, H=48, W=48, frames=12, clutter=0.06, amp=0.14):
    """A faint STATIC target below single-frame detectability (SNR ~2.3), planted
    at a fixed pixel across many frames — recoverable only by SNR-stacking.
    Returns (frames, (row, col))."""
    rng = random.Random(seed)
    r0, c0 = H // 2, W // 2
    vid = []
    for _ in range(frames):
        img = [[max(0.0, rng.gauss(0.2, clutter)) for _ in range(W)] for _ in range(H)]
        img[r0][c0] += amp
        vid.append(img)
    return vid, (r0, c0)


def video_with_target(seed=41, H=48, W=48, frames=6, clutter=0.06, amp=0.5):
    """A video (frame stack) of churny background with one moving target
    (e.g. a swimmer drifting). Returns (frames, planted_pixels_per_frame)."""
    rng = random.Random(seed)
    vid, truth = [], []
    r0, c0 = 8, 8
    for i in range(frames):
        img = [[max(0.0, rng.gauss(0.2, clutter)) for _ in range(W)] for _ in range(H)]
        r, c = r0 + i * 3, c0 + i * 3
        if 0 <= r < H and 0 <= c < W:
            img[r][c] += amp
            truth.append((r, c))
        vid.append(img)
    return vid, truth
