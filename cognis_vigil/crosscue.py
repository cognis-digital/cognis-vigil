"""Cross-cue: flag non-cooperative ("dark") tracks.

A maritime track observed by radar/EO/IR but with NO cooperative self-report
(AIS) is a classic go-fast / semi-submersible signature. Air tracks with no
ADS-B are the equivalent. Output is a prioritized, confidence-scored lead list
for interdiction by law-enforcement partners (non-kinetic).
"""

from __future__ import annotations

NONCOOP_SENSORS = {"radar", "eo", "ir", "sar"}


def find_dark_contacts(tracks, min_fixes: int = 2) -> list:
    dark = []
    for tr in tracks:
        noncoop_fixes = [d for d in tr.detections if d.sensor in NONCOOP_SENSORS]
        if not tr.has_ais and len(noncoop_fixes) >= min_fixes:
            # confidence rises with number & diversity of non-cooperative sensors
            sensor_div = len({d.sensor for d in noncoop_fixes})
            conf = min(0.95, 0.5 + 0.1 * len(noncoop_fixes) + 0.1 * sensor_div)
            last = tr.detections[-1]
            dark.append({
                "track_id": tr.id, "domain": tr.domain,
                "fixes": len(tr.detections), "sensors": sorted(tr.sensors),
                "last_lat": last.lat, "last_lon": last.lon, "last_ts": last.ts,
                "confidence": round(conf, 4),
            })
    dark.sort(key=lambda x: -x["confidence"])
    return dark
