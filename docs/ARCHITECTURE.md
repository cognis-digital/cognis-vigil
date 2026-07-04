# Architecture

```
 detections ─► fusion (spatio-temporal NN gating) ─► tracks ─┬─► crosscue (dark contacts)
                                                             ├─► geojson (export)
                                                             └─► report
 platforms  ─► coverage (cost/hour vs legacy)
```

| Module | Responsibility |
|---|---|
| `geo` | Haversine distance, bounding box. |
| `model` | `Detection`, `Track`. |
| `fusion` | Greedy nearest-neighbor tracker with kinematic gating. |
| `crosscue` | Non-cooperative ("dark") track detection + confidence. |
| `coverage` | Coverage ratio + cost-per-hour vs legacy baseline. |
| `geojson`, `report` | Products. |
| `synth` | Deterministic synthetic multi-sensor scenario + ground truth. |
| `cli` | `scryer` entry point. |

## Principles
1. **Non-kinetic** — detection/monitoring; leads for lawful interdiction, never targeting.
2. **Multi-domain fusion** — cooperative (AIS/ADS-B) vs non-cooperative sensing.
3. **Honest cost math** — cost-per-hour stated against an explicit baseline.
4. **Deterministic, offline, zero-dependency.**
