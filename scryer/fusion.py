"""Spatio-temporal track fusion: associate detections across sensors and time
into tracks via nearest-neighbor gating (kinematically bounded)."""

from __future__ import annotations

import json

from .geo import haversine_km
from .model import Detection, Track


def load_detections(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Detection(**d) for d in raw]


def correlate(detections, max_speed_kmh: float = 80.0, max_gap_s: float = 1800.0,
              base_gate_km: float = 2.0) -> list:
    """Greedy nearest-neighbor tracker. A detection joins the open track whose
    last fix is reachable within max_speed over the elapsed time (plus sensor
    slack); otherwise it starts a new track."""
    dets = sorted(detections, key=lambda d: (d.ts, d.id))
    tracks = []
    open_tracks = []  # (track, last_detection)
    counter = 0
    for d in dets:
        best = None
        best_dist = None
        for tr, last in open_tracks:
            if tr.domain != d.domain:
                continue
            dt = d.ts - last.ts
            if dt < 0 or dt > max_gap_s:
                continue
            gate = base_gate_km + max_speed_kmh * (dt / 3600.0)
            dist = haversine_km(last.lat, last.lon, d.lat, d.lon)
            if dist <= gate and (best_dist is None or dist < best_dist):
                best, best_dist = tr, dist
        if best is None:
            counter += 1
            best = Track(id=f"trk-{counter:04d}", domain=d.domain)
            tracks.append(best)
            open_tracks.append([best, d])
        else:
            for ot in open_tracks:
                if ot[0] is best:
                    ot[1] = d
                    break
        best.detections.append(d)
    return tracks
