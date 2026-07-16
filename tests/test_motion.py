"""Constant-velocity (alpha-beta) motion model."""

import pytest

from scryer.model import Detection, Track
from scryer.motion import alpha_beta_smooth, predict_next


def _track(coords, domain="maritime"):
    dets = [Detection(id=f"d{i}", ts=ts, lat=lat, lon=lon, sensor="radar", domain=domain)
            for i, (ts, lat, lon) in enumerate(coords)]
    return Track(id="T", domain=domain, detections=dets)


def test_empty_track_smoothing_and_prediction():
    tr = Track(id="T", domain="maritime")
    assert alpha_beta_smooth(tr) == []
    assert predict_next(tr) is None


def test_single_fix_has_zero_velocity_and_flat_prediction():
    tr = _track([(1000.0, 9.0, -79.0)])
    sm = alpha_beta_smooth(tr)
    assert len(sm) == 1 and sm[0]["v_lat"] == 0.0 and sm[0]["v_lon"] == 0.0
    pred = predict_next(tr, horizon_s=600.0)
    assert pred["lat"] == pytest.approx(9.0, abs=1e-6)


def test_smoothing_tracks_steady_northward_motion():
    tr = _track([(1000.0 + i * 300, 9.0 + i * 0.02, -79.0) for i in range(6)])
    sm = alpha_beta_smooth(tr)
    assert len(sm) == 6
    # velocity estimate becomes positive (moving north)
    assert sm[-1]["v_lat"] > 0
    # smoothed final position is near the last measurement
    assert sm[-1]["lat"] == pytest.approx(9.0 + 5 * 0.02, abs=0.02)


def test_prediction_extrapolates_forward():
    tr = _track([(1000.0 + i * 300, 9.0 + i * 0.02, -79.0) for i in range(6)])
    last_lat = tr.detections[-1].lat
    pred = predict_next(tr, horizon_s=600.0)
    assert pred["lat"] > last_lat            # continues north
    assert pred["horizon_s"] == 600.0


def test_zero_dt_between_fixes_does_not_crash():
    # two fixes at the same timestamp -> dt == 0, velocity not updated
    tr = _track([(1000.0, 9.0, -79.0), (1000.0, 9.1, -79.0)])
    sm = alpha_beta_smooth(tr)
    assert len(sm) == 2
    assert all("lat" in s for s in sm)


def test_out_of_order_fixes_are_sorted_by_time():
    dets = [Detection(id="late", ts=2000.0, lat=9.1, lon=-79.0, sensor="radar", domain="maritime"),
            Detection(id="early", ts=1000.0, lat=9.0, lon=-79.0, sensor="radar", domain="maritime")]
    tr = Track(id="T", domain="maritime", detections=dets)
    sm = alpha_beta_smooth(tr)
    assert sm[0]["ts"] == 1000.0 and sm[1]["ts"] == 2000.0
