from scryer import observer, synth
from scryer.model import Detection


def _dets():
    dets, _ = synth.generate()
    return dets


def test_observe_shape():
    dets = _dets()
    r = observer.observe(dets)
    assert r["total_contacts"] == len(dets)
    assert r["by_class"] and r["by_sensor"]
    assert r["density"]["level"] in ("clear", "light", "moderate", "high", "packed")
    assert r["flow"]["trend"] in ("rising", "steady", "easing")
    assert r["summary"].endswith(".")


def test_density_levels():
    assert observer.density_level(0)[0] == "clear"
    assert observer.density_level(60)[0] == "packed"
    lvl, metric = observer.density_level(28)
    assert lvl == "high" and metric == 28


def test_density_area_normalized():
    # 20 contacts over 1000 km^2 -> 20 per 1000 km^2 -> moderate (>=12)
    lvl, metric = observer.density_level(20, area_km2=1000)
    assert metric == 20.0 and lvl == "moderate"


def test_flow_trend():
    assert observer.flow_trend([1, 1, 5, 6])[0] == "rising"
    assert observer.flow_trend([6, 5, 1, 1])[0] == "easing"
    assert observer.flow_trend([3, 3, 3, 3])[0] == "steady"
    assert observer.flow_trend([2])[0] == "steady"


def test_zone_occupancy_partitions():
    dets = _dets()
    lons = [d.lon for d in dets]; lats = [d.lat for d in dets]
    midx = (min(lons) + max(lons)) / 2; midy = (min(lats) + max(lats)) / 2
    zones = [{"name": "W", "bbox": (min(lons) - 1, min(lats) - 1, midx, max(lats) + 1)},
             {"name": "E", "bbox": (midx, min(lats) - 1, max(lons) + 1, max(lats) + 1)}]
    occ = observer.zone_occupancy(dets, zones)
    assert occ["W"] + occ["E"] + occ["_outside"] == len(dets)
    assert occ["_outside"] == 0  # zones cover the full AOI


def test_noncooperative_flagged():
    # synth plants dark (radar/eo/ir) contacts scryer can see but a camera-only tool can't
    r = observer.observe(_dets())
    assert r["noncooperative"] >= 1


def test_render_text_has_fields():
    txt = observer.render_text(observer.observe(_dets()))
    assert "OBSERVER" in txt
    assert "non-cooperative" in txt.lower()
    assert "by sensor" in txt.lower()


def test_hottest_zone():
    dets = [Detection(id=f"d{i}", ts=1.0 + i, lat=10.0, lon=10.0, sensor="radar", domain="air")
            for i in range(5)]
    dets += [Detection(id="x", ts=1.0, lat=50.0, lon=50.0, sensor="ais", domain="maritime")]
    zones = [{"name": "HOT", "bbox": (9, 9, 11, 11)}, {"name": "COLD", "bbox": (49, 49, 51, 51)}]
    r = observer.observe(dets, zones=zones)
    assert r["hottest_zone"] == "HOT"
    assert r["zones"]["HOT"] == 5
