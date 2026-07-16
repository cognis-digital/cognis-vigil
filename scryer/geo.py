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


def initial_bearing(a_lat, a_lon, b_lat, b_lon) -> float:
    """Initial great-circle bearing from A to B, in degrees clockwise from true
    north in [0, 360). Returns 0.0 for a zero-length segment."""
    if a_lat == b_lat and a_lon == b_lon:
        return 0.0
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dl = math.radians(b_lon - a_lon)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0


def destination_point(lat, lon, bearing_deg, distance_km) -> tuple:
    """Great-circle destination given a start point, bearing (deg) and distance
    (km). Inverse of ``initial_bearing``/``haversine_km`` for short legs."""
    ang = distance_km / EARTH_KM
    brg = math.radians(bearing_deg)
    p1 = math.radians(lat)
    l1 = math.radians(lon)
    p2 = math.asin(math.sin(p1) * math.cos(ang) +
                   math.cos(p1) * math.sin(ang) * math.cos(brg))
    l2 = l1 + math.atan2(math.sin(brg) * math.sin(ang) * math.cos(p1),
                         math.cos(ang) - math.sin(p1) * math.sin(p2))
    return round(math.degrees(p2), 6), round((math.degrees(l2) + 540.0) % 360.0 - 180.0, 6)
