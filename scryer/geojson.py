"""Export tracks as GeoJSON LineStrings (dark contacts flagged)."""

from __future__ import annotations

import json


def tracks_to_geojson(tracks, dark_ids=None) -> dict:
    dark_ids = set(dark_ids or [])
    feats = []
    for tr in tracks:
        coords = [[round(d.lon, 6), round(d.lat, 6)] for d in tr.detections]
        geom = ({"type": "Point", "coordinates": coords[0]} if len(coords) == 1
                else {"type": "LineString", "coordinates": coords})
        feats.append({
            "type": "Feature", "geometry": geom,
            "properties": {"track_id": tr.id, "domain": tr.domain,
                           "sensors": sorted(tr.sensors), "dark": tr.id in dark_ids,
                           "fixes": len(tr.detections)},
        })
    return {"type": "FeatureCollection", "features": feats}


def to_json(fc, indent=2):
    return json.dumps(fc, indent=indent)
