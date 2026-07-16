# Architecture

Scryer is a small, layered, dependency-free pipeline. Data flows one direction:
raw detections (and imagery) become tracks, and tracks become products.

```
 detections ─► fusion (spatio-temporal NN gating) ─► tracks ─┬─► crosscue (dark contacts + prediction)
                                                             ├─► kinematics (speed/heading/classify)
                                                             ├─► geojson / export (GeoJSON, CSV)
                                                             └─► report (text / JSON)
 imagery/video ─► smalltarget (CA-CFAR / stacking) ─► blobs ─► imagery (geolocate) ─► detections
 platforms  ─► coverage (cost/hour vs legacy + gap analysis)
```

## Module map

| Module | Responsibility |
|---|---|
| `geo` | Haversine distance, bounding box, great-circle bearing, destination point. |
| `model` | `Detection`, `Track` (sensor set, cooperative-report test). |
| `fusion` | Greedy nearest-neighbor tracker with a time-growing kinematic gate. |
| `motion` | Constant-velocity alpha-beta smoothing + future-position prediction. |
| `crosscue` | Non-cooperative ("dark") track detection + confidence + prediction. |
| `kinematics` | Per-track speed/heading/distance/straightness + behavior classifier. |
| `coverage` | Coverage ratio + cost-per-hour vs legacy; uncovered-area gap analysis. |
| `smalltarget` | CA-CFAR point-target detection, temporal residual, SNR frame-stacking. |
| `imagery` | Bridge image/video blobs into geolocated `Detection`s. |
| `heatmap` | Downsample the CFAR SNR surface into georeferenced priority cells. |
| `geojson` | Track LineString/Point export with dark flag. |
| `export` | Flat CSV exporters (tracks + kinematics; dark-contact leads). |
| `report` | Human-readable and JSON fusion products. |
| `synth` | Deterministic synthetic multi-sensor scenario + planted ground truth. |
| `cli` | `scryer` entry point (`demo`, `fuse`, `export`, `coverage`, `search`, `heatmap`). |

## Data model

- **`Detection`** — an `(id, ts, lat, lon, sensor, domain, source, meta)` record.
  `sensor ∈ {radar, eo, ir, ais, adsb, sar}`; `domain ∈ {maritime, air}`.
- **`Track`** — an ordered set of detections sharing one domain. `has_ais` is the
  cooperative-report test: AIS for maritime, ADS-B for air.

## Association (fusion)

`correlate` sorts detections by `(ts, id)` and greedily extends the nearest open
track in the same domain whose last fix is reachable within
`base_gate_km + max_speed_kmh · Δt`. Otherwise it opens a new track. The gate
**grows with elapsed time**, so a slow revisit still associates while an
implausible jump starts a fresh track. The algorithm is deterministic: identical
input yields identical tracks.

This is a transparent baseline. `docs/LIMITATIONS.md` describes where it can
split/merge tracks and what a production tracker (Kalman, MHT) would add.

## Cross-cue & kinematics

`crosscue.find_dark_contacts` flags tracks with no cooperative report and at
least `min_fixes` non-cooperative fixes, scoring confidence by the count and
diversity of non-cooperative sensors, and attaching a projected next position
from `motion.predict_next`. With `with_kinematics=True` (opt-in, additive) each
lead also carries `kinematics` (speed/heading/straightness) and a
`classification` label from `kinematics.classify_track` — surfacing the go-fast
signature without changing the default output.

## Imagery path

`smalltarget` runs cell-averaging CFAR over a scene, optionally after temporal
background subtraction (moving target) or SNR frame-stacking (faint static
target). `imagery.blobs_to_detections` georeferences the resulting blobs via a
simple linear geotransform so an EO/IR find becomes a normal `Detection` and
flows through the same fusion/cross-cue/motion pipeline.

## Principles

1. **Non-kinetic** — detection/monitoring; leads for lawful interdiction, never targeting.
2. **Multi-domain fusion** — cooperative (AIS/ADS-B) vs non-cooperative sensing.
3. **Honest cost math** — cost-per-hour stated against an explicit baseline.
4. **Deterministic, offline, zero-dependency.**
5. **Additive evolution** — new capability is layered on; existing outputs stay stable.
