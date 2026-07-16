"""Spatio-temporal track fusion (greedy NN gating)."""

import json

from scryer import synth
from scryer.fusion import correlate, load_detections
from scryer.model import Detection


def _d(did, ts, lat, lon, sensor="radar", domain="maritime"):
    return Detection(id=did, ts=ts, lat=lat, lon=lon, sensor=sensor, domain=domain)


def test_empty_input_gives_no_tracks():
    assert correlate([]) == []


def test_single_detection_is_one_track():
    tracks = correlate([_d("a", 0.0, 9.0, -79.0)])
    assert len(tracks) == 1 and len(tracks[0].detections) == 1


def test_close_in_time_and_space_merges_into_one_track():
    # two fixes 5 minutes apart, ~0.5 km — well within the gate
    tracks = correlate([_d("a", 0.0, 9.0, -79.0), _d("b", 300.0, 9.004, -79.0)])
    assert len(tracks) == 1
    assert [d.id for d in tracks[0].detections] == ["a", "b"]


def test_far_apart_in_space_splits_tracks():
    # 5 minutes apart but ~110 km away: unreachable at 80 km/h -> new track
    tracks = correlate([_d("a", 0.0, 9.0, -79.0), _d("b", 300.0, 10.0, -79.0)])
    assert len(tracks) == 2


def test_gap_too_large_splits_tracks():
    # same place, but beyond max_gap_s -> cannot associate
    tracks = correlate([_d("a", 0.0, 9.0, -79.0), _d("b", 5000.0, 9.0, -79.0)],
                       max_gap_s=1800.0)
    assert len(tracks) == 2


def test_different_domains_never_merge():
    tracks = correlate([_d("a", 0.0, 9.0, -79.0, domain="maritime"),
                        _d("b", 60.0, 9.0, -79.0, sensor="radar", domain="air")])
    assert len(tracks) == 2
    assert {t.domain for t in tracks} == {"maritime", "air"}


def test_gate_grows_with_elapsed_time():
    # 30 km in 30 min = 60 km/h < 80 km/h max_speed -> reachable, one track
    close = correlate([_d("a", 0.0, 9.0, -79.0), _d("b", 1800.0, 9.27, -79.0)])
    assert len(close) == 1


def test_higher_max_speed_allows_association():
    dets = [_d("a", 0.0, 9.0, -79.0), _d("b", 300.0, 9.05, -79.0)]  # ~5.6 km in 5 min = 66 km/h
    assert len(correlate(dets, max_speed_kmh=10.0)) == 2   # too slow to link
    assert len(correlate(dets, max_speed_kmh=120.0)) == 1  # fast enough to link


def test_negative_dt_is_ignored_by_sorting():
    # supplied out of order; correlate sorts by (ts, id) so association still holds
    tracks = correlate([_d("b", 300.0, 9.004, -79.0), _d("a", 0.0, 9.0, -79.0)])
    assert len(tracks) == 1
    assert [d.id for d in tracks[0].detections] == ["a", "b"]


def test_determinism_across_runs():
    dets, _ = synth.generate()
    a = [[d.id for d in t.detections] for t in correlate(dets)]
    b = [[d.id for d in t.detections] for t in correlate(dets)]
    assert a == b


def test_track_ids_are_sequential_and_unique():
    dets, _ = synth.generate()
    ids = [t.id for t in correlate(dets)]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("trk-") for i in ids)


def test_load_detections_roundtrip(tmp_path):
    src = [_d("a", 0.0, 9.0, -79.0).to_dict(), _d("b", 300.0, 9.004, -79.0).to_dict()]
    p = tmp_path / "dets.json"
    p.write_text(json.dumps(src), encoding="utf-8")
    loaded = load_detections(str(p))
    assert [d.id for d in loaded] == ["a", "b"]
    assert len(correlate(loaded)) == 1
