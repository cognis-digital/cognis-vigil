from cognis_vigil import synth
from cognis_vigil.imagery import search_image
from cognis_vigil.smalltarget import detect_in_video, detect_small_targets


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


def test_image_search_emits_geolocated_detections():
    img, truth = synth.scene_with_targets(n_targets=3)
    gt = {"origin_lat": 9.5, "origin_lon": -79.9, "dlat": -0.001, "dlon": 0.001}
    dets = search_image(img, gt, k=5.0)
    assert dets
    for d in dets:
        assert d.sensor == "eo" and d.source == "EO-SMALLTARGET"
        assert -90 <= d.lat <= 90 and "peak_snr" in d.meta
