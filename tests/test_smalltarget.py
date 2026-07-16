from scryer import synth
from scryer.heatmap import heatmap_from_image, heatmap_geojson
from scryer.imagery import search_image
from scryer.smalltarget import (
    detect_in_video,
    detect_small_targets,
    detect_with_stacking,
    pfa_to_k,
)


def _matched(blobs, truth, tol=1.5):
    tp = 0
    for (tr, tc) in truth:
        if any(abs(b["row"] - tr) <= tol and abs(b["col"] - tc) <= tol for b in blobs):
            tp += 1
    return tp


def test_detects_planted_point_targets():
    img, truth = synth.scene_with_targets()
    blobs = detect_small_targets(img, k=5.0)
    assert _matched(blobs, truth) == len(truth)      # recall = 1.0
    assert len(blobs) <= len(truth) + 2              # few false alarms


def test_blank_scene_no_targets():
    import random
    rng = random.Random(0)
    blank = [[max(0.0, rng.gauss(0.2, 0.05)) for _ in range(48)] for _ in range(48)]
    assert len(detect_small_targets(blank, k=6.0)) <= 1  # CFAR keeps false alarms low


def test_video_finds_moving_swimmer():
    vid, truth = synth.video_with_target()
    blobs = detect_in_video(vid, k=5.0)
    assert blobs  # the drifting target survives temporal background subtraction


def test_pfa_to_k_monotonic():
    # a stricter false-alarm rate demands a higher sigma threshold
    assert pfa_to_k(1e-6) > pfa_to_k(1e-4) > pfa_to_k(1e-2)
    assert 3.0 < pfa_to_k(1e-4) < 4.5


def test_stacking_recovers_faint_static_target():
    vid, (tr, tc) = synth.video_faint_static()
    single = detect_small_targets(vid[0], k=5.0)
    stacked = detect_with_stacking(vid, k=5.0)
    single_hit = any(abs(b["row"] - tr) <= 1.5 and abs(b["col"] - tc) <= 1.5 for b in single)
    stacked_hit = any(abs(b["row"] - tr) <= 1.5 and abs(b["col"] - tc) <= 1.5 for b in stacked)
    assert not single_hit          # below single-frame detectability
    assert stacked_hit             # recovered by SNR stacking


def test_heatmap_georeferenced():
    img, _ = synth.scene_with_targets()
    grid = heatmap_from_image(img, cell=8)
    gt = {"origin_lat": 9.5, "origin_lon": -79.9, "dlat": -0.001, "dlon": 0.001}
    fc = heatmap_geojson(grid, gt, cell=8, snr_floor=3.0)
    assert fc["type"] == "FeatureCollection" and fc["features"]
    f = fc["features"][0]
    assert f["geometry"]["type"] == "Polygon"
    assert f["properties"]["priority"] in ("low", "medium", "high")


def test_image_search_emits_geolocated_detections():
    img, truth = synth.scene_with_targets(n_targets=3)
    gt = {"origin_lat": 9.5, "origin_lon": -79.9, "dlat": -0.001, "dlon": 0.001}
    dets = search_image(img, gt, k=5.0)
    assert dets
    for d in dets:
        assert d.sensor == "eo" and d.source == "EO-SMALLTARGET"
        assert -90 <= d.lat <= 90 and "peak_snr" in d.meta
