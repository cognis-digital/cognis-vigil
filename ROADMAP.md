# Roadmap

Direction for Scryer. Every item preserves the project's guardrails:
**detection/monitoring only (non-kinetic)**, deterministic, offline, and
zero-runtime-dependency unless a capability genuinely cannot be delivered in the
standard library. New work is layered additively so existing outputs and entry
points stay stable.

## Near-term (0.5.x)

- **Track quality scoring** — expose per-track continuity/consistency metrics
  (gap statistics, residual magnitude from the alpha-beta filter) so weak tracks
  can be de-prioritized before they become leads.
- **Configurable scenarios** — surface `synth.generate` parameters (contact
  counts, speed bands, sensor mixes) through the CLI for repeatable what-if runs.
- **Lead ranking policy** — combine dark-contact confidence with kinematics
  (e.g. fast-mover + straight-line) into a single, documented priority score.
- **KML / CSV round-trip** — a loader for exported CSV so products can be edited
  and re-ingested; a KML writer alongside GeoJSON for common mapping clients.
- **Richer coverage modeling** — sensor-specific footprints and duty cycles,
  and a simple time-on-station schedule optimizer over a fixed budget.

## Mid-term (0.6–0.7)

- **Motion models beyond constant velocity** — a lightweight Kalman option
  (still stdlib) for maneuvering targets, selectable per domain.
- **Association robustness** — gating that accounts for measurement error and
  optional global (assignment-style) association to reduce split/merge under
  dense traffic.
- **Multi-frame small-target tracking** — link CFAR detections across frames
  (track-before-detect) to lift faint, persistent targets above single-frame
  thresholds with quantified gain.
- **Provenance & audit** — carry sensor/source lineage end-to-end and emit an
  audit record per lead (which fixes, which thresholds) for lawful review.
- **Streaming mode** — incremental fusion over an append-only detection feed
  with bounded memory, for long-dwell operation.

## Long-term

- **Pluggable ingest adapters** — thin, dependency-free parsers for common AIS
  and ADS-B message dumps to reduce the glue needed to feed real data.
- **Uncertainty everywhere** — attach covariance/confidence to positions and
  predictions and propagate it into GeoJSON/CSV products.
- **Evaluation corpus** — an expanded, versioned synthetic corpus with harder
  cases (crossing tracks, dropouts, spoofed cooperative reports) and a public
  scoreboard gated in CI.
- **Deployment profiles** — reference configurations for air-gapped and
  low-power edge deployment, with reproducible verification on each.

## Non-goals (hard lines)

- No targeting, weapons cueing, fire-control, or any kinetic-finish capability.
- No feature that requires phoning home or transmitting collected data off-box.
- No dependence on proprietary/networked services for core function.

Feedback and proposals are welcome — see the roadmap discussion (RFC) in the
repository's Discussions, or open an issue.
