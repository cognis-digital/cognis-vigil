from scryer import synth
from scryer.coverage import coverage_plan
from scryer.crosscue import find_dark_contacts
from scryer.fusion import correlate
from scryer.geo import haversine_km
from scryer.geojson import tracks_to_geojson


def test_haversine_known_distance():
    # ~111 km per degree of latitude
    assert 110 < haversine_km(0, 0, 1, 0) < 112


def test_correlate_forms_tracks():
    dets, truth = synth.generate()
    tracks = correlate(dets)
    # number of tracks should be close to number of true tracks
    n_true = len(set(truth["detection_track"].values()))
    assert abs(len(tracks) - n_true) <= 2


def test_dark_contacts_found():
    dets, truth = synth.generate()
    dark = find_dark_contacts(correlate(dets))
    assert len(dark) >= len(truth["dark_tracks"]) - 1
    for d in dark:
        assert "ais" not in d["sensors"] and "adsb" not in d["sensors"]


def test_cooperative_tracks_not_flagged():
    dets, _ = synth.generate(n_maritime=5, n_dark=0, n_air=2)
    assert find_dark_contacts(correlate(dets)) == []


def test_coverage_savings():
    cov = coverage_plan(
        [{"name": "uas", "coverage_km2": 100000, "cost_per_hour": 3000, "dwell_hours": 20}],
        200000, 20000)
    assert cov["cost_per_hour_savings"] > 0
    assert 0 <= cov["coverage_ratio"] <= 1


def test_motion_smoothing_and_prediction():
    from scryer.model import Detection, Track
    from scryer.motion import alpha_beta_smooth, predict_next
    # a track moving steadily north (+lat) with small jitter
    dets = [Detection(id=f"d{i}", ts=1000.0 + i * 300, lat=9.0 + i * 0.02,
                      lon=-79.0, sensor="radar", domain="maritime") for i in range(6)]
    tr = Track(id="T", domain="maritime", detections=dets)
    sm = alpha_beta_smooth(tr)
    assert len(sm) == len(dets)
    pred = predict_next(tr, horizon_s=300.0)
    # prediction continues northward beyond the last fix
    assert pred["lat"] > dets[-1].lat - 0.02


def test_dark_contact_has_prediction():
    from scryer import synth
    dark = find_dark_contacts(correlate(synth.generate()[0]))
    assert dark and dark[0]["predicted_next"] is not None


def test_geojson_shape():
    dets, _ = synth.generate()
    tracks = correlate(dets)
    fc = tracks_to_geojson(tracks, {tracks[0].id})
    assert fc["type"] == "FeatureCollection"
    assert any(f["properties"]["dark"] for f in fc["features"])
