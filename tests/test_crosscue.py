"""Cross-cue: dark (non-cooperative) contact detection."""

from scryer.crosscue import find_dark_contacts
from scryer.model import Detection, Track


def _track(tid, sensors, domain="maritime", n=3):
    dets = []
    for i in range(n):
        for s in sensors:
            dets.append(Detection(id=f"{tid}-{s}-{i}", ts=1000.0 + i * 300,
                                  lat=9.0 + i * 0.01, lon=-79.0, sensor=s, domain=domain))
    return Track(id=tid, domain=domain, detections=dets)


def test_cooperative_track_not_flagged():
    tr = _track("T1", ["radar", "ais"])
    assert find_dark_contacts([tr]) == []


def test_air_track_with_adsb_not_flagged():
    tr = _track("A1", ["radar", "adsb"], domain="air")
    assert find_dark_contacts([tr]) == []


def test_dark_track_flagged():
    tr = _track("T2", ["radar", "eo"])
    dark = find_dark_contacts([tr])
    assert len(dark) == 1
    assert dark[0]["track_id"] == "T2"
    assert "ais" not in dark[0]["sensors"]


def test_min_fixes_threshold():
    tr = _track("T3", ["radar"], n=1)  # single non-coop fix
    assert find_dark_contacts([tr], min_fixes=2) == []
    assert len(find_dark_contacts([tr], min_fixes=1)) == 1


def test_confidence_rises_with_sensor_diversity():
    single = find_dark_contacts([_track("S", ["radar"], n=3)])[0]
    diverse = find_dark_contacts([_track("D", ["radar", "eo", "ir"], n=3)])[0]
    assert diverse["confidence"] > single["confidence"]


def test_confidence_capped_at_0_95():
    tr = _track("Big", ["radar", "eo", "ir", "sar"], n=10)
    assert find_dark_contacts([tr])[0]["confidence"] <= 0.95


def test_results_sorted_by_confidence_desc():
    weak = _track("W", ["radar"], n=2)
    strong = _track("S", ["radar", "eo", "ir"], n=5)
    dark = find_dark_contacts([weak, strong])
    confs = [d["confidence"] for d in dark]
    assert confs == sorted(confs, reverse=True)


def test_every_lead_has_prediction_and_last_fix():
    dark = find_dark_contacts([_track("T", ["radar", "eo"])])
    d = dark[0]
    assert d["predicted_next"] is not None
    assert d["last_ts"] == 1000.0 + 2 * 300  # last fix time


def test_kinematics_enrichment_is_opt_in_and_additive():
    tr = _track("T", ["radar", "eo"])
    plain = find_dark_contacts([tr])[0]
    enriched = find_dark_contacts([tr], with_kinematics=True)[0]
    assert "kinematics" not in plain and "classification" not in plain
    assert "kinematics" in enriched and "classification" in enriched
    # additive: the plain keys are unchanged in the enriched output
    for key, val in plain.items():
        assert enriched[key] == val
