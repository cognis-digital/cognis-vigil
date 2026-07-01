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
