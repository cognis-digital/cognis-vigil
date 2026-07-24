<h1 align="center">🟣 Scryer</h1>
<p align="center"><b>Multi-domain ISR sensor fusion for counternarcotics</b><br>
<i>Fuse EO/IR + radar + AIS + ADS-B into tracks, flag "dark" contacts, classify go-fast movers, model coverage cost — self-hosted, offline.</i></p>

<p align="center">
<img alt="license" src="https://img.shields.io/badge/license-COCL--1.0-6D28D9">
<img alt="python" src="https://img.shields.io/badge/python-3.9%2B-6D28D9">
<img alt="deps" src="https://img.shields.io/badge/dependencies-none%20(stdlib)-6D28D9">
<img alt="tests" src="https://img.shields.io/badge/tests-122-6D28D9">
<img alt="status" src="https://img.shields.io/badge/status-v0.4.0-6D28D9">
</p>

---

> **Built for:** SOLIC Accelerator / ONIX OTA — **Challenge Area 1: Low-Cost, Long-Dwell ISR for Counternarcotics Detection & Monitoring.**
> Correlate multi-sensor detections into tracks, surface the **dark contacts** (radar/EO with no AIS — go-fast / semi-submersible signature), and show a **materially lower cost-per-hour** than legacy platforms.

> 🛡️ **Detection & monitoring only — explicitly NOT a targeting or kinetic-finish capability.** Outputs are confidence-scored leads for interdiction by law-enforcement partners.

## What it does

- 🛰️ **Track fusion** — kinematically-gated nearest-neighbor association across EO/IR, radar, AIS (maritime) and ADS-B (air).
- 🌑 **Dark-contact cross-cue** — flags non-cooperative maritime tracks (radar/EO, no AIS) with confidence scoring and a projected next position.
- 🏃 **Kinematics & behavior classification** — per-track speed, heading, path length and straightness, with a transparent `fast-mover` / `transiter` / `loiterer` / `stationary` label (the classic *go-fast* signature).
- 🔬 **Small-target search-and-rescue** — CA-CFAR + temporal background subtraction + SNR frame-stacking pulls a **1–2 pixel target** (swimmer lost at sea, small craft) out of clutter in imagery/video; detections feed the tracker as geolocated leads.
- 💰 **Coverage & cost model** — cost-per-hour vs a legacy baseline, plus **gap analysis** (uncovered area and the marginal platforms/cost to close it).
- 🗺️ **GeoJSON + CSV export** — track lines with dark contacts flagged; flat CSV (with kinematics) for spreadsheet triage and case management.
- 🔒 **Offline / zero-dependency** — pure Python stdlib.

## Install

```bash
git clone https://github.com/cognis-digital/scryer
cd scryer
python -m pip install -e .          # installs the `scryer` console command
# or run without installing:  python -m scryer <command>
```

No runtime dependencies. Python 3.9+. For development extras (test + lint):

```bash
python -m pip install -e ".[dev]"
```

## Quick start

```bash
# End-to-end demo on synthetic multi-sensor data, with map + spreadsheet products
python -m scryer demo --geojson tracks.geojson --csv tracks.csv --kinematics

# Fuse your own detections file (JSON list of detection records)
python -m scryer fuse --detections dets.json --json

# Situational-awareness read-out: zone occupancy, density, flow trend, dark contacts
python -m scryer observe --detections dets.json      # or no flag for a synthetic demo

# Generate GeoJSON, per-track CSV, and a confidence-ranked dark-contact lead CSV
python -m scryer export --detections dets.json \
    --geojson tracks.geojson --csv tracks.csv --dark-csv leads.csv

# Coverage & cost-per-hour vs a legacy baseline
python -m scryer coverage --platforms fleet.json --area 250000 --legacy 22000

# Small-target search-and-rescue (single frame / video / SNR-stacked)
python -m scryer search
python -m scryer search --video
python -m scryer search --stack --pfa 1e-5

# Georeferenced search-priority heatmap
python -m scryer heatmap --geojson heat.geojson
```

A **detection record** is a JSON object:

```json
{"id": "d1", "ts": 1700000000.0, "lat": 9.51, "lon": -79.32,
 "sensor": "radar", "domain": "maritime", "source": "COASTAL-RADAR"}
```

`sensor` ∈ `radar | eo | ir | ais | adsb | sar`; `domain` ∈ `maritime | air`.
Cooperative reports are `ais` (maritime) / `adsb` (air); everything else is
non-cooperative and can raise a dark contact.

## Architecture

```
 detections ─► fusion (spatio-temporal NN gating) ─► tracks ─┬─► crosscue (dark contacts + prediction)
                                                             ├─► kinematics (speed/heading/classify)
                                                             ├─► geojson / export (GeoJSON, CSV)
                                                             └─► report
 imagery/video ─► smalltarget (CA-CFAR / stacking) ─► blobs ─► imagery (geolocate) ─► detections
 platforms  ─► coverage (cost/hour vs legacy + gap)
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the module map and
[`docs/USAGE.md`](docs/USAGE.md) for a full API + CLI walkthrough.

## Configuration reference

| Surface | Parameter | Default | Meaning |
|---|---|---|---|
| `fusion.correlate` | `max_speed_kmh` | `80.0` | max kinematically-plausible speed for association |
| `fusion.correlate` | `max_gap_s` | `1800.0` | max time gap before a track is not extended |
| `fusion.correlate` | `base_gate_km` | `2.0` | fixed sensor slack added to the speed gate |
| `crosscue.find_dark_contacts` | `min_fixes` | `2` | non-cooperative fixes required to raise a lead |
| `crosscue.find_dark_contacts` | `with_kinematics` | `False` | add speed/heading + classification to each lead |
| `kinematics.classify_track` | `fast_kmh` | `55.0` | go-fast threshold (~30 kn) |
| `smalltarget.detect_small_targets` | `k` / `pfa` | `5.0` / — | CFAR threshold in sigma, or derived from Pfa |
| `smalltarget.*` | `guard` / `train` | `1` / `4` | CFAR guard band and training-ring radius |
| `coverage.coverage_plan` | `legacy_cost_per_hour` | — | baseline the savings are stated against |

## Verification & proof

Measured against **planted ground truth**, gated in CI (`python bench/run_all.py` → [`RESULTS.md`](RESULTS.md)):

| Metric | Value |
|---|---|
| Track association (pairwise) | P/R/F1 = **1.00** |
| Dark-contact detection | P/R/F1 = **1.00** |
| Small-target (SAR) recall | **1.00** |
| Cost/hour savings vs legacy | **76%** |
| Determinism | ✓ |

**122 tests** (pytest) + ruff lint run on every push/PR across Python 3.9–3.13.
Throughput: **~23,000 detections/sec** single-thread.

## FAQ

**Is this a targeting or weapons system?** No. Scryer produces confidence-scored
*leads* for lawful interdiction by law-enforcement partners. It has no cueing,
fire-control, or kinetic function. See [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md).

**Does a "dark" contact mean a smuggler?** No — absence of AIS has lawful
explanations. A dark contact is a prioritized lead to corroborate, not a
conclusion.

**Why zero dependencies?** Deterministic, air-gap-friendly deployment. Everything
(great-circle math, CFAR, alpha-beta filtering, GeoJSON/CSV) is stdlib.

**Are the benchmark numbers real sensor accuracy?** No. They measure fusion-
algorithm correctness on deterministic synthetic tracks with planted ground
truth. Fielded data will be noisier; see the limitations doc.

**Can I import it as a library?** Yes — every capability is a small, typed,
documented function. See [`docs/USAGE.md`](docs/USAGE.md).

## License

Source-available under **COCL v1.0** (see [LICENSE](LICENSE)). Detection/monitoring
use only — see [NOTICE](NOTICE) and [`docs/COMPLIANCE.md`](docs/COMPLIANCE.md).

<p align="center"><sub>© 2026 Cognis Digital LLC · <a href="https://cognis.digital">cognis.digital</a></sub></p>
