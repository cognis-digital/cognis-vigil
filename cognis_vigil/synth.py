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
