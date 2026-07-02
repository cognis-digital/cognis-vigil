"""Run accuracy + performance; write bench/results.json and RESULTS.md."""

from __future__ import annotations

import json
import os
import platform
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bench import benchmark, evaluate  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def build_results():
    return {"accuracy": evaluate.evaluate(), "performance": benchmark.benchmark(),
            "environment": {"python": platform.python_version(),
                            "implementation": platform.python_implementation(),
                            "system": platform.system(), "machine": platform.machine()}}


def render_md(res) -> str:
    a = res["accuracy"]
    env = res["environment"]
    L = []
    L.append("# Cognis Vigil — Verification Results\n")
    L.append("Reproduce with: `python bench/run_all.py`.\n")
    L.append(f"Environment: {env['implementation']} {env['python']} on {env['system']}/{env['machine']}. "
             "Deterministic synthetic multi-sensor data.\n")
    L.append("> Detection/monitoring only (non-kinetic). Metrics measure fusion correctness on "
             "planted synthetic tracks, not fielded sensor performance.\n")
    L.append("## Accuracy vs. planted ground truth\n")
    L.append("| Metric | Value |")
    L.append("|---|---|")
    t = a["track_association"]
    d = a["dark_contact"]
    L.append(f"| Track association (pairwise) | P={t['precision']:.3f} / R={t['recall']:.3f} / F1={t['f1']:.3f} |")
    L.append(f"| Dark-contact detection | P={d['precision']:.3f} / R={d['recall']:.3f} / F1={d['f1']:.3f} |")
    st = a.get("small_target")
    if st:
        L.append(f"| Small-target (SAR) recall | {st['recall']:.3f} "
                 f"({st['planted']} planted, {st['false_alarms']} false alarms) |")
    L.append(f"| Detections / tracks / true tracks | {a['detections']} / {a['tracks']} / {a['true_tracks']} |")
    L.append(f"| Cost/hour savings vs legacy | {a['cost_per_hour_savings']*100:.0f}% |")
    L.append(f"| Determinism | {a['determinism']} |")
    L.append("")
    L.append("## Performance (single-thread, stdlib only)\n")
    L.append("| Contacts | Detections | Tracks | Fuse (s) | Detections/s |")
    L.append("|---:|---:|---:|---:|---:|")
    for r in res["performance"]:
        L.append(f"| {r['contacts']} | {r['detections']:,} | {r['tracks']} | {r['fuse_s']} | {r['detections_per_s']:,} |")
    L.append("")
    L.append("Gated in CI by `tests/test_bench.py`. See `docs/LIMITATIONS.md`.\n")
    return "\n".join(L)


def main():
    res = build_results()
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    with open(os.path.join(ROOT, "RESULTS.md"), "w", encoding="utf-8") as f:
        f.write(render_md(res))
    print("[+] wrote bench/results.json and RESULTS.md")
    print(render_md(res))


if __name__ == "__main__":
    main()
