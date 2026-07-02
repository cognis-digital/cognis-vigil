from bench import evaluate


def test_track_association_strong():
    r = evaluate.evaluate()
    assert r["track_association"]["f1"] >= 0.9


def test_dark_contact_recall():
    r = evaluate.evaluate()
    assert r["dark_contact"]["recall"] >= 0.9


def test_cost_savings_and_determinism():
    r = evaluate.evaluate()
    assert r["cost_per_hour_savings"] > 0
    assert r["determinism"] is True


def test_small_target_recall():
    r = evaluate.evaluate()
    assert r["small_target"]["recall"] >= 0.9


def test_roc_is_characterized():
    roc = evaluate.evaluate()["roc"]
    assert len(roc) >= 4
    # detection probability is non-increasing as the threshold rises
    pds = [pt["pd"] for pt in roc]
    assert all(pds[i] >= pds[i + 1] for i in range(len(pds) - 1))


def test_stacking_gain():
    s = evaluate.evaluate()["stacking"]
    assert s["single_frame_detected"] is False
    assert s["stacked_detected"] is True
