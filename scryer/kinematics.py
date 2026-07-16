"""Per-track kinematics: speed, heading, distance and a behavior classifier.

Derives motion statistics from a track's ordered fixes — total path length,
elapsed time, mean and peak leg speed, and the current bearing — then applies a
transparent, threshold-based label (``fast-mover`` / ``transiter`` /
``loiterer`` / ``stationary``). For counternarcotics this surfaces the classic
*go-fast* signature: a non-cooperative maritime track running at high speed. The
labels are advisory search context for analysts, never a targeting decision.

All maths are great-circle (stdlib only). A track needs at least two fixes to
have a defined speed/heading; with fewer, fields degrade gracefully to ``None``.
"""

from __future__ import annotations

from .geo import haversine_km, initial_bearing

# Default maritime speed bands (km/h). ~55 km/h ~= 30 kn — a go-fast threshold.
FAST_KMH = 55.0
TRANSIT_KMH = 15.0
LOITER_KMH = 3.0


def _ordered(track):
    return sorted(track.detections, key=lambda d: d.ts)


def track_kinematics(track) -> dict:
    """Return motion statistics for ``track``.

    Keys: ``fixes``, ``distance_km`` (great-circle path length), ``duration_s``,
    ``mean_speed_kmh`` (path length / elapsed time), ``max_speed_kmh`` (fastest
    single leg), ``heading_deg`` (bearing of the final leg) and
    ``straightness`` (net displacement / path length, 1.0 = perfectly straight).
    Speed/heading fields are ``None`` when undefined (fewer than two timed
    fixes)."""
    dets = _ordered(track)
    out = {"fixes": len(dets), "distance_km": 0.0, "duration_s": 0.0,
           "mean_speed_kmh": None, "max_speed_kmh": None,
           "heading_deg": None, "straightness": None}
    if len(dets) < 2:
        return out
    total_km = 0.0
    max_leg_speed = 0.0
    heading = None
    for a, b in zip(dets, dets[1:]):
        leg_km = haversine_km(a.lat, a.lon, b.lat, b.lon)
        total_km += leg_km
        dt_h = (b.ts - a.ts) / 3600.0
        if dt_h > 0:
            max_leg_speed = max(max_leg_speed, leg_km / dt_h)
        heading = initial_bearing(a.lat, a.lon, b.lat, b.lon)
    duration_s = dets[-1].ts - dets[0].ts
    mean_speed = (total_km / (duration_s / 3600.0)) if duration_s > 0 else None
    net_km = haversine_km(dets[0].lat, dets[0].lon, dets[-1].lat, dets[-1].lon)
    straightness = round(net_km / total_km, 4) if total_km > 0 else None
    out.update({
        "distance_km": round(total_km, 4),
        "duration_s": round(duration_s, 2),
        "mean_speed_kmh": round(mean_speed, 2) if mean_speed is not None else None,
        "max_speed_kmh": round(max_leg_speed, 2),
        "heading_deg": round(heading, 2) if heading is not None else None,
        "straightness": straightness,
    })
    return out


def classify_track(track, fast_kmh: float = FAST_KMH, transit_kmh: float = TRANSIT_KMH,
                   loiter_kmh: float = LOITER_KMH) -> str:
    """Label a track by its peak leg speed.

    ``fast-mover`` (>= ``fast_kmh``), ``transiter`` (>= ``transit_kmh``),
    ``loiterer`` (> ``loiter_kmh``), ``stationary`` (<= ``loiter_kmh``), or
    ``indeterminate`` when speed is undefined. Bands are inclusive at the upper
    edge and evaluated high-to-low."""
    k = track_kinematics(track)
    speed = k["max_speed_kmh"]
    if speed is None:
        return "indeterminate"
    if speed >= fast_kmh:
        return "fast-mover"
    if speed >= transit_kmh:
        return "transiter"
    if speed > loiter_kmh:
        return "loiterer"
    return "stationary"
