"""Detection / Track data structures."""

from scryer.model import AIR_SENSORS, MARITIME_SENSORS, Detection, Track


def _det(did, sensor, domain="maritime", ts=0.0, lat=9.0, lon=-79.0):
    return Detection(id=did, ts=ts, lat=lat, lon=lon, sensor=sensor, domain=domain)


def test_detection_to_dict_roundtrip_keys():
    d = _det("d1", "radar")
    out = d.to_dict()
    assert set(out) == {"id", "ts", "lat", "lon", "sensor", "domain", "source", "meta"}
    assert out["id"] == "d1" and out["sensor"] == "radar"
    assert out["meta"] == {} and out["source"] == ""


def test_detection_defaults():
    d = _det("d1", "eo")
    assert d.source == "" and d.meta == {}
    # dataclass default_factory must give each instance its own dict
    d.meta["k"] = 1
    assert _det("d2", "eo").meta == {}


def test_track_sensors_are_unique_set():
    tr = Track(id="T", domain="maritime",
               detections=[_det("a", "radar"), _det("b", "radar"), _det("c", "eo")])
    assert tr.sensors == {"radar", "eo"}


def test_track_has_ais_maritime():
    coop = Track(id="T", domain="maritime", detections=[_det("a", "radar"), _det("b", "ais")])
    dark = Track(id="T", domain="maritime", detections=[_det("a", "radar"), _det("b", "eo")])
    assert coop.has_ais is True
    assert dark.has_ais is False


def test_track_has_ais_air_uses_adsb():
    coop = Track(id="T", domain="air",
                 detections=[_det("a", "radar", "air"), _det("b", "adsb", "air")])
    dark = Track(id="T", domain="air",
                 detections=[_det("a", "radar", "air"), _det("b", "eo", "air")])
    assert coop.has_ais is True
    assert dark.has_ais is False


def test_track_to_dict_shape():
    tr = Track(id="T7", domain="maritime",
               detections=[_det("a", "radar"), _det("b", "eo")])
    out = tr.to_dict()
    assert out["id"] == "T7" and out["length"] == 2
    assert out["sensors"] == ["eo", "radar"]     # sorted
    assert out["detections"] == ["a", "b"]
    assert out["has_cooperative"] is False


def test_empty_track_is_dark_and_zero_length():
    tr = Track(id="T", domain="maritime")
    assert tr.sensors == set() and tr.has_ais is False
    assert tr.to_dict()["length"] == 0


def test_sensor_domain_constants():
    assert "ais" in MARITIME_SENSORS and "adsb" not in MARITIME_SENSORS
    assert "adsb" in AIR_SENSORS and "ais" not in AIR_SENSORS
