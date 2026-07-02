# Cognis Vigil — Verification Results

Reproduce with: `python bench/run_all.py`.

Environment: CPython 3.14.0 on Windows/AMD64. Deterministic synthetic multi-sensor data.

> Detection/monitoring only (non-kinetic). Metrics measure fusion correctness on planted synthetic tracks, not fielded sensor performance.

## Accuracy vs. planted ground truth

| Metric | Value |
|---|---|
| Track association (pairwise) | P=1.000 / R=1.000 / F1=1.000 |
| Dark-contact detection | P=1.000 / R=1.000 / F1=1.000 |
| Small-target (SAR) recall | 1.000 (5 planted, 0 false alarms) |
| Detections / tracks / true tracks | 228 / 15 / 15 |
| Cost/hour savings vs legacy | 76% |
| Determinism | True |

## Performance (single-thread, stdlib only)

| Contacts | Detections | Tracks | Fuse (s) | Detections/s |
|---:|---:|---:|---:|---:|
| 80 | 1,260 | 80 | 0.0849 | 14,844 |
| 240 | 3,780 | 240 | 0.6823 | 5,540 |
| 640 | 10,080 | 640 | 4.4545 | 2,262 |

Gated in CI by `tests/test_bench.py`. See `docs/LIMITATIONS.md`.
