"""Accuracy evaluation vs planted ground truth."""

from __future__ import annotations

import json
from collections import Counter

from cognis_vigil import synth
from cognis_vigil.coverage import coverage_plan
from cognis_vigil.crosscue import find_dark_contacts
from cognis_vigil.fusion import correlate
from cognis_vigil.smalltarget import detect_small_targets

from .metrics import label_prf, pairwise_prf


def evaluate() -> dict:
    dets, truth = synth.generate()
    tracks = correlate(dets)

    tt = truth["detection_track"]
    pred_clusters = [{d.id for d in t.detections} for t in tracks]
    truth_groups = {}
    for did, tid in tt.items():
        truth_groups.setdefault(tid, set()).add(did)
    assoc = pairwise_prf(pred_clusters, list(truth_groups.values()), universe=set(tt))

    dark = find_dark_contacts(tracks)
    dark_track_ids = {d["track_id"] for d in dark}
    pred_dark_trues = set()
    for t in tracks:
        if t.id in dark_track_ids:
            maj = Counter(tt[d.id] for d in t.detections).most_common(1)[0][0]
            pred_dark_trues.add(maj)
    dark_prf = label_prf(pred_dark_trues, truth["dark_tracks"])

    determinism = ([len(t.detections) for t in correlate(dets)]
                   == [len(t.detections) for t in tracks])
    cov = coverage_plan(
        [{"name": "a", "coverage_km2": 120000, "cost_per_hour": 3500, "dwell_hours": 24},
         {"name": "b", "coverage_km2": 40000, "cost_per_hour": 1800, "dwell_hours": 16}],
        250000, 22000)

    # small/point-target detection (search-and-rescue) vs planted pixels
    img, tpix = synth.scene_with_targets()
    blobs = detect_small_targets(img, k=5.0)
    tp = sum(1 for (r, c) in tpix
             if any(abs(b["row"] - r) <= 1.5 and abs(b["col"] - c) <= 1.5 for b in blobs))
    small_target = {"planted": len(tpix), "detected": len(blobs),
                    "recall": round(tp / len(tpix), 4) if tpix else 0.0,
                    "false_alarms": max(0, len(blobs) - tp)}

    return {
        "detections": len(dets), "tracks": len(tracks),
        "true_tracks": len(truth_groups),
        "track_association": assoc,
        "dark_contact": dark_prf,
        "small_target": small_target,
        "cost_per_hour_savings": cov["cost_per_hour_savings"],
        "determinism": determinism,
    }


def main():
    print(json.dumps(evaluate(), indent=2))


if __name__ == "__main__":
    main()
