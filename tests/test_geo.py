"""Geospatial helpers: haversine, bbox, bearing, destination."""

import math

import pytest

from scryer.geo import bbox, destination_point, haversine_km, initial_bearing


def test_haversine_zero_distance():
    assert haversine_km(9.5, -79.9, 9.5, -79.9) == pytest.approx(0.0, abs=1e-9)


def test_haversine_symmetric():
    d1 = haversine_km(9.0, -79.0, 9.5, -78.5)
    d2 = haversine_km(9.5, -78.5, 9.0, -79.0)
    assert d1 == pytest.approx(d2, rel=1e-12)


def test_haversine_one_degree_latitude():
    # one degree of latitude is ~111.19 km anywhere on the sphere
    assert haversine_km(0, 0, 1, 0) == pytest.approx(111.19, abs=0.5)
    assert haversine_km(45, 10, 46, 10) == pytest.approx(111.19, abs=0.5)


def test_haversine_longitude_shrinks_with_latitude():
    # a degree of longitude spans less ground the further from the equator
    at_equator = haversine_km(0, 0, 0, 1)
    at_60 = haversine_km(60, 0, 60, 1)
    assert at_60 < at_equator
    assert at_60 == pytest.approx(at_equator * math.cos(math.radians(60)), abs=1.0)


def test_bbox_bounds():
    pts = [(9.0, -80.0), (10.0, -78.0), (9.5, -79.0)]
    b = bbox(pts)
    assert b == {"min_lat": 9.0, "max_lat": 10.0, "min_lon": -80.0, "max_lon": -78.0}


def test_initial_bearing_cardinals():
    assert initial_bearing(0, 0, 1, 0) == pytest.approx(0.0, abs=1e-6)      # north
    assert initial_bearing(0, 0, 0, 1) == pytest.approx(90.0, abs=1e-6)     # east
    assert initial_bearing(1, 0, 0, 0) == pytest.approx(180.0, abs=1e-6)    # south
    assert initial_bearing(0, 1, 0, 0) == pytest.approx(270.0, abs=1e-6)    # west


def test_initial_bearing_range_and_degenerate():
    b = initial_bearing(9.0, -79.0, 9.6, -78.4)
    assert 0.0 <= b < 360.0
    assert initial_bearing(5.0, 5.0, 5.0, 5.0) == 0.0  # zero-length leg


def test_destination_point_roundtrips_with_haversine_and_bearing():
    lat, lon = 9.5, -79.5
    for brg in (0.0, 45.0, 90.0, 200.0, 315.0):
        dlat, dlon = destination_point(lat, lon, brg, 25.0)
        assert haversine_km(lat, lon, dlat, dlon) == pytest.approx(25.0, abs=0.05)
        assert initial_bearing(lat, lon, dlat, dlon) == pytest.approx(brg, abs=0.5)


def test_destination_point_wraps_longitude_into_range():
    _, dlon = destination_point(0.0, 179.9, 90.0, 50.0)
    assert -180.0 <= dlon <= 180.0
