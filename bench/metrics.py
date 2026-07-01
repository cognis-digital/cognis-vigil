"""Metrics: pairwise clustering PRF (track association) and label PRF."""

from __future__ import annotations


def _pairs(clusters, universe=None):
    U = set(universe) if universe is not None else None
    s = set()
    for c in clusters:
        items = sorted(x for x in c if (U is None or x in U))
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                s.add((items[i], items[j]))
    return s


def pairwise_prf(pred_clusters, truth_clusters, universe=None) -> dict:
    P, T = _pairs(pred_clusters, universe), _pairs(truth_clusters, universe)
    tp, fp, fn = len(P & T), len(P - T), len(T - P)
    prec = tp / (tp + fp) if (tp + fp) else 1.0
    rec = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
    return {"precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}


def label_prf(pred_set, truth_set) -> dict:
    pred, truth = set(pred_set), set(truth_set)
    tp, fp, fn = len(pred & truth), len(pred - truth), len(truth - pred)
    prec = tp / (tp + fp) if (tp + fp) else 1.0
    rec = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
    return {"precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}
