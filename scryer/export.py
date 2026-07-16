"""Tabular exporters for fusion products (stdlib ``csv`` only).

GeoJSON is ideal for maps; analysts and case-management systems usually want
flat CSV. These helpers render tracks and dark-contact leads as CSV strings (or
write them to disk), with kinematics columns included so a spreadsheet triage is
sortable by speed, heading and confidence. Purely additive: nothing here mutates
tracks or the existing GeoJSON path.
"""

from __future__ import annotations

import csv
import io

from .kinematics import classify_track, track_kinematics

TRACK_FIELDS = [
    "track_id", "domain", "sensors", "fixes", "dark", "classification",
    "distance_km", "duration_s", "mean_speed_kmh", "max_speed_kmh",
    "heading_deg", "straightness", "last_lat", "last_lon", "last_ts",
]

DARK_FIELDS = [
    "track_id", "domain", "confidence", "fixes", "sensors",
    "last_lat", "last_lon", "last_ts", "pred_lat", "pred_lon",
]


def _last(track):
    return max(track.detections, key=lambda d: d.ts) if track.detections else None


def tracks_to_rows(tracks, dark_ids=None) -> list:
    """Flatten tracks into ordered dict rows (kinematics + classification)."""
    dark_ids = set(dark_ids or [])
    rows = []
    for tr in tracks:
        k = track_kinematics(tr)
        last = _last(tr)
        rows.append({
            "track_id": tr.id, "domain": tr.domain,
            "sensors": "|".join(sorted(tr.sensors)),
            "fixes": len(tr.detections),
            "dark": tr.id in dark_ids,
            "classification": classify_track(tr),
            "distance_km": k["distance_km"], "duration_s": k["duration_s"],
            "mean_speed_kmh": k["mean_speed_kmh"], "max_speed_kmh": k["max_speed_kmh"],
            "heading_deg": k["heading_deg"], "straightness": k["straightness"],
            "last_lat": last.lat if last else "", "last_lon": last.lon if last else "",
            "last_ts": last.ts if last else "",
        })
    return rows


def _write_csv(fieldnames, rows) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def tracks_to_csv(tracks, dark_ids=None) -> str:
    """Render all tracks as a CSV string (one row per track)."""
    return _write_csv(TRACK_FIELDS, tracks_to_rows(tracks, dark_ids))


def dark_contacts_to_csv(dark) -> str:
    """Render dark-contact leads (from ``find_dark_contacts``) as a CSV string,
    highest confidence first."""
    rows = []
    for d in dark:
        pn = d.get("predicted_next") or {}
        rows.append({
            "track_id": d["track_id"], "domain": d["domain"],
            "confidence": d["confidence"], "fixes": d["fixes"],
            "sensors": "|".join(d["sensors"]),
            "last_lat": d["last_lat"], "last_lon": d["last_lon"], "last_ts": d["last_ts"],
            "pred_lat": pn.get("lat", ""), "pred_lon": pn.get("lon", ""),
        })
    return _write_csv(DARK_FIELDS, rows)


def write_csv(path: str, text: str) -> None:
    """Write a rendered CSV string to ``path`` as UTF-8 (no BOM)."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
