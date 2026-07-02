"""Constant-velocity motion model (alpha-beta filter).

Smooths noisy multi-sensor fixes into a track state (position + velocity) and
predicts a future position — used to cue interdiction assets to where a contact
will be (non-kinetic; a projected intercept point, not a firing solution).
"""

from __future__ import annotations


def alpha_beta_smooth(track, alpha: float = 0.5, beta: float = 0.3) -> list:
    dets = sorted(track.detections, key=lambda d: d.ts)
    if not dets:
        return []
    est_lat, est_lon = dets[0].lat, dets[0].lon
    v_lat = v_lon = 0.0
    prev_ts = dets[0].ts
    out = []
    for d in dets:
        dt = d.ts - prev_ts
        pred_lat = est_lat + v_lat * dt
        pred_lon = est_lon + v_lon * dt
        r_lat, r_lon = d.lat - pred_lat, d.lon - pred_lon
        est_lat = pred_lat + alpha * r_lat
        est_lon = pred_lon + alpha * r_lon
        if dt > 0:
            v_lat += beta * r_lat / dt
            v_lon += beta * r_lon / dt
        out.append({"ts": d.ts, "lat": round(est_lat, 6), "lon": round(est_lon, 6),
                    "v_lat": v_lat, "v_lon": v_lon})
        prev_ts = d.ts
    return out


def predict_next(track, horizon_s: float = 1800.0, alpha: float = 0.5, beta: float = 0.3):
    sm = alpha_beta_smooth(track, alpha, beta)
    if not sm:
        return None
    last = sm[-1]
    return {"horizon_s": horizon_s,
            "lat": round(last["lat"] + last["v_lat"] * horizon_s, 6),
            "lon": round(last["lon"] + last["v_lon"] * horizon_s, 6)}
