"""Report rendering and GeoJSON export shape."""

import json

from scryer import synth
from scryer.crosscue import find_dark_contacts
from scryer.fusion import correlate
from scryer.geojson import to_json, tracks_to_geojson
from scryer.model import Detection, Track
from scryer.report import render_json, render_text


def _product():
    dets, _ = synth.generate()
    tracks = correlate(dets)
    dark = find_dark_contacts(tracks)
    return {
        "detections": len(dets), "tracks": len(tracks), "dark_contacts": dark,
        "track_summary": [t.to_dict() for t in tracks],
    }, tracks, dark


def test_render_text_contains_banner_and_counts():
    product, _, dark = _product()
    txt = render_text(product)
    assert "COGNIS VIGIL" in txt
    assert f"Tracks: {product['tracks']}" in txt
    assert "NOTE: Detection/monitoring only" in txt


def test_render_text_shows_coverage_when_present():
    product, _, _ = _product()
    product["coverage"] = {
        "coverage_ratio": 0.76, "area_km2": 250000, "platforms": 3,
        "fleet_cost_per_hour": 5600, "legacy_cost_per_hour": 22000,
        "cost_per_hour_savings": 0.75,
    }
    txt = render_text(product)
    assert "Coverage:" in txt and "% lower" in txt


def test_render_json_is_valid_json():
    product, _, _ = _product()
    parsed = json.loads(render_json(product))
    assert parsed["tracks"] == product["tracks"]


def test_geojson_linestring_for_multi_fix_track():
    dets = [Detection(id=f"d{i}", ts=i * 300.0, lat=9.0 + i * 0.004, lon=-79.0,
                      sensor="radar", domain="maritime") for i in range(3)]
    tr = Track(id="T", domain="maritime", detections=dets)
    fc = tracks_to_geojson([tr])
    geom = fc["features"][0]["geometry"]
    assert geom["type"] == "LineString" and len(geom["coordinates"]) == 3
    # GeoJSON is [lon, lat] order
    assert geom["coordinates"][0] == [-79.0, 9.0]


def test_geojson_point_for_single_fix_track():
    tr = Track(id="T", domain="maritime",
               detections=[Detection(id="d", ts=0.0, lat=9.0, lon=-79.0,
                                     sensor="radar", domain="maritime")])
    geom = tracks_to_geojson([tr])["features"][0]["geometry"]
    assert geom["type"] == "Point" and geom["coordinates"] == [-79.0, 9.0]


def test_geojson_dark_flag_and_serialization():
    _, tracks, dark = _product()
    dark_ids = {d["track_id"] for d in dark}
    fc = tracks_to_geojson(tracks, dark_ids)
    flagged = [f for f in fc["features"] if f["properties"]["dark"]]
    assert len(flagged) == len(dark_ids)
    # round-trips through json
    assert json.loads(to_json(fc))["type"] == "FeatureCollection"
