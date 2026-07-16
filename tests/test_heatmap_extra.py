"""Heatmap downsampling, ASCII preview and GeoJSON gridding edges."""

from scryer import synth
from scryer.heatmap import (
    ascii_preview,
    downsample_max,
    heatmap_from_image,
    heatmap_geojson,
)


def test_downsample_dimensions_round_up():
    snr = [[0.0] * 10 for _ in range(10)]
    grid = downsample_max(snr, cell=4)
    assert len(grid) == 3 and len(grid[0]) == 3  # ceil(10/4) == 3


def test_downsample_takes_cell_maximum():
    snr = [[1.0, 2.0], [3.0, 9.0]]
    grid = downsample_max(snr, cell=2)
    assert grid == [[9.0]]


def test_ascii_preview_dimensions_and_charset():
    img, _ = synth.scene_with_targets()
    grid = heatmap_from_image(img, cell=8)
    art = ascii_preview(grid)
    lines = art.split("\n")
    assert len(lines) == len(grid)
    assert all(len(ln) == len(grid[0]) for ln in lines)


def test_heatmap_geojson_floor_filters_low_cells():
    img, _ = synth.scene_with_targets()
    grid = heatmap_from_image(img, cell=8)
    low = heatmap_geojson(grid, {"origin_lat": 9.5, "origin_lon": -79.9,
                                 "dlat": -0.001, "dlon": 0.001}, cell=8, snr_floor=0.0)
    high = heatmap_geojson(grid, {"origin_lat": 9.5, "origin_lon": -79.9,
                                  "dlat": -0.001, "dlon": 0.001}, cell=8, snr_floor=8.0)
    assert len(high["features"]) <= len(low["features"])
    for f in high["features"]:
        assert f["properties"]["snr"] >= 8.0


def test_heatmap_priority_bands():
    grid = [[9.0, 6.0, 4.0]]
    fc = heatmap_geojson(grid, {"origin_lat": 0, "origin_lon": 0,
                                "dlat": -0.001, "dlon": 0.001}, cell=8, snr_floor=3.0)
    prios = {f["properties"]["snr"]: f["properties"]["priority"] for f in fc["features"]}
    assert prios[9.0] == "high" and prios[6.0] == "medium" and prios[4.0] == "low"


def test_heatmap_polygon_is_closed_ring():
    grid = [[10.0]]
    fc = heatmap_geojson(grid, {"origin_lat": 0, "origin_lon": 0,
                                "dlat": -0.001, "dlon": 0.001}, cell=8, snr_floor=3.0)
    ring = fc["features"][0]["geometry"]["coordinates"][0]
    assert ring[0] == ring[-1] and len(ring) == 5  # closed quad
