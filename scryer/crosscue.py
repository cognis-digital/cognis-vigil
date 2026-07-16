"""Cross-cue: flag non-cooperative ("dark") tracks.

A maritime track observed by radar/EO/IR but with NO cooperative self-report
(AIS) is a classic go-fast / semi-submersible signature. Air tracks with no
ADS-B are the equivalent. Output is a prioritized, confidence-scored lead list
for interdiction by law-enforcement partners (non-kinetic).
"""

from __future__ import annotations

from .motion import predict_next

NONCOOP_SENSORS = {"radar", "eo", "ir", "sar"}


def find_dark_contacts(tracks, min_fixes: int = 2, predict_horizon_s: float = 1800.0,
                       with_kinematics: bool = False) -> list:
    """Flag non-cooperative tracks as confidence-scored leads.

    A track qualifies when it carries no cooperative report (AIS/ADS-B) and has
    at least ``min_fixes`` non-cooperative fixes. Confidence rises with the
    count and diversity of non-cooperative sensors. When ``with_kinematics`` is
    set, each lead gains additive ``kinematics`` and ``classification`` keys
    (speed/heading and a go-fast/loiterer label); the default is off so existing
    output is byte-for-byte unchanged.
    """
    dark = []
    for tr in tracks:
        noncoop_fixes = [d for d in tr.detections if d.sensor in NONCOOP_SENSORS]
        if not tr.has_ais and len(noncoop_fixes) >= min_fixes:
            # confidence rises with number & diversity of non-cooperative sensors
            sensor_div = len({d.sensor for d in noncoop_fixes})
            conf = min(0.95, 0.5 + 0.1 * len(noncoop_fixes) + 0.1 * sensor_div)
            last = sorted(tr.detections, key=lambda d: d.ts)[-1]
            entry = {
                "track_id": tr.id, "domain": tr.domain,
                "fixes": len(tr.detections), "sensors": sorted(tr.sensors),
                "last_lat": last.lat, "last_lon": last.lon, "last_ts": last.ts,
                "predicted_next": predict_next(tr, predict_horizon_s),
                "confidence": round(conf, 4),
            }
            if with_kinematics:
                from .kinematics import classify_track, track_kinematics
                entry["kinematics"] = track_kinematics(tr)
                entry["classification"] = classify_track(tr)
            dark.append(entry)
    dark.sort(key=lambda x: -x["confidence"])
    return dark
