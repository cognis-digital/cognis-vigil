# SOLIC Challenge Area 1 — Capability Mapping

| Desired capability | Scryer | Module |
|---|---|---|
| Multi-domain ISR (air/maritime/land) detection & cueing | EO/IR + radar + AIS + ADS-B fusion into tracks | `fusion` |
| Detect go-fast vessels / semi-submersibles evading legacy systems | Dark-contact cross-cue (non-cooperative tracks) | `crosscue` |
| Cost per hour materially lower than legacy | Coverage + cost-per-hour vs baseline model | `coverage` |
| Unclassified products for partner-nation coordination | GeoJSON track export | `geojson` |
| Minimal-training, government-operable | Single CLI, structured output, zero dependencies | `cli` |

## Non-kinetic
Per the challenge ("This is not a request for kinetic finish capability"),
Scryer is detection/monitoring only. It emits confidence-scored leads for
interdiction by law-enforcement partners — no targeting.

## TRL posture (honest)
- **Fusion, cross-cue, coverage, export (working, measured):** tested with
  reproducible metrics (`RESULTS.md`) — track association & dark-contact F1 = 1.00
  on synthetic ground truth, ~76% modeled cost-per-hour reduction.
- **Prototype scope (post-award):** ingest real sensor/AIS/ADS-B feeds, add
  motion-model tracking (Kalman/MHT), validate against a Government reference
  dataset, and integrate unclassified partner dissemination.
