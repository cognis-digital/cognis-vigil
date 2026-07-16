"""Per-track kinematics and behavior classification."""

import pytest

from scryer.geo import destination_point
from scryer.kinematics import classify_track, track_kinematics
from scryer.model import Detection, Track


def _track_from_points(points, domain="maritime"):
    dets = [Detection(id=f"d{i}", ts=ts, lat=lat, lon=lon, sensor="radar", domain=domain)
            for i, (ts, lat, lon) in enumerate(points)]
    return Track(id="T", domain=domain, detections=dets)


def _straight_run(speed_kmh, legs=4, step_s=600.0, start=(9.0, -79.0), bearing=90.0):
    """Build a track that moves at a constant speed on a fixed bearing."""
    pts = []
    lat, lon = start
    t = 1000.0
    pts.append((t, lat, lon))
    for _ in range(legs):
        dist = speed_kmh * (step_s / 3600.0)
        lat, lon = destination_point(lat, lon, bearing, dist)
        t += step_s
        pts.append((t, lat, lon))
    return _track_from_points(pts)


def test_fewer_than_two_fixes_is_undefined():
    tr = _track_from_points([(1000.0, 9.0, -79.0)])
    k = track_kinematics(tr)
    assert k["fixes"] == 1
    assert k["mean_speed_kmh"] is None and k["heading_deg"] is None
    assert classify_track(tr) == "indeterminate"


def test_mean_speed_matches_construction():
    tr = _straight_run(40.0, legs=5)
    k = track_kinematics(tr)
    assert k["mean_speed_kmh"] == pytest.approx(40.0, abs=0.5)
    assert k["max_speed_kmh"] == pytest.approx(40.0, abs=0.5)


def test_heading_matches_construction():
    tr = _straight_run(30.0, bearing=90.0)
    assert track_kinematics(tr)["heading_deg"] == pytest.approx(90.0, abs=1.0)


def test_straightness_near_one_for_straight_line():
    tr = _straight_run(30.0, legs=6)
    assert track_kinematics(tr)["straightness"] == pytest.approx(1.0, abs=0.01)


def test_classify_fast_mover():
    assert classify_track(_straight_run(70.0)) == "fast-mover"


def test_classify_transiter():
    assert classify_track(_straight_run(25.0)) == "transiter"


def test_classify_loiterer():
    assert classify_track(_straight_run(6.0)) == "loiterer"


def test_classify_stationary():
    # all fixes at the same place -> zero speed
    tr = _track_from_points([(1000.0 + i * 300, 9.0, -79.0) for i in range(4)])
    assert classify_track(tr) == "stationary"


def test_custom_threshold_shifts_label():
    tr = _straight_run(40.0)
    assert classify_track(tr, fast_kmh=100.0) == "transiter"
    assert classify_track(tr, fast_kmh=35.0) == "fast-mover"


def test_zero_duration_leaves_mean_speed_undefined():
    # two fixes at identical timestamps: no elapsed time
    tr = _track_from_points([(1000.0, 9.0, -79.0), (1000.0, 9.1, -79.0)])
    k = track_kinematics(tr)
    assert k["mean_speed_kmh"] is None
    assert k["distance_km"] > 0
