"""Geospatial helpers (stdlib math only)."""

from __future__ import annotations

import math

EARTH_KM = 6371.0088


def haversine_km(a_lat, a_lon, b_lat, b_lon) -> float:
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dphi = math.radians(b_lat - a_lat)
    dl = math.radians(b_lon - a_lon)
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_KM * math.asin(min(1.0, math.sqrt(h)))


def bbox(points) -> dict:
    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    return {"min_lat": min(lats), "max_lat": max(lats),
            "min_lon": min(lons), "max_lon": max(lons)}
