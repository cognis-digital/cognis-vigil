<h1 align="center">🟣 Cognis Vigil</h1>
<p align="center"><b>Multi-domain ISR sensor fusion for counternarcotics</b><br>
<i>Fuse EO/IR + radar + AIS + ADS-B into tracks, flag "dark" contacts, model coverage cost — self-hosted, offline.</i></p>

<p align="center">
<img alt="license" src="https://img.shields.io/badge/license-COCL--1.0-6D28D9">
<img alt="python" src="https://img.shields.io/badge/python-3.9%2B-6D28D9">
<img alt="deps" src="https://img.shields.io/badge/dependencies-none%20(stdlib)-6D28D9">
<img alt="status" src="https://img.shields.io/badge/status-v0.1.0-6D28D9">
</p>

---

> **Built for:** SOLIC Accelerator / ONIX OTA — **Challenge Area 1: Low-Cost, Long-Dwell ISR for Counternarcotics Detection & Monitoring.**
> Correlate multi-sensor detections into tracks, surface the **dark contacts** (radar/EO with no AIS — go-fast / semi-submersible signature), and show a **materially lower cost-per-hour** than legacy platforms.

> 🛡️ **Detection & monitoring only — explicitly NOT a targeting or kinetic-finish capability.** Outputs are confidence-scored leads for interdiction by law-enforcement partners.

## What it does

- 🛰️ **Track fusion** — kinematically-gated nearest-neighbor association across EO/IR, radar, AIS (maritime) and ADS-B (air).
- 🌑 **Dark-contact cross-cue** — flags non-cooperative maritime tracks (radar/EO, no AIS) with confidence scoring.
- 🔬 **Small-target search-and-rescue** — CA-CFAR + temporal background subtraction pulls a **1–2 pixel target** (swimmer lost at sea, small craft) out of clutter in imagery/video; detections feed the tracker as geolocated leads.
- 💰 **Coverage & cost model** — cost-per-hour vs a legacy baseline (the challenge's key metric).
- 🗺️ **GeoJSON export** — track lines with dark contacts flagged.
- 🔒 **Offline / zero-dependency** — pure Python stdlib.

## Quick start

```bash
git clone https://github.com/cognis-digital/cognis-vigil
cd cognis-vigil
python -m cognis_vigil demo --geojson tracks.geojson
```

## Verification & proof

Measured against **planted ground truth**, gated in CI (`python bench/run_all.py` → [`RESULTS.md`](RESULTS.md)):

| Metric | Value |
|---|---|
| Track association (pairwise) | P/R/F1 = **1.00** |
| Dark-contact detection | P/R/F1 = **1.00** |
| Cost/hour savings vs legacy | **76%** |
| Determinism | ✓ |

Throughput: **~23,000 detections/sec** single-thread.

## License

Source-available under **COCL v1.0** (see [LICENSE](LICENSE)). Detection/monitoring
use only — see [NOTICE](NOTICE).

<p align="center"><sub>© 2026 Cognis Digital LLC · <a href="https://cognis.digital">cognis.digital</a></sub></p>
