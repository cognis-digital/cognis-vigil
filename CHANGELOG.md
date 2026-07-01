# Changelog

Adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-07-01

Initial public release.

### Added
- Geospatial helpers (haversine, bbox) — `geo`.
- Detection/Track model — `model`.
- Spatio-temporal nearest-neighbor track fusion — `fusion`.
- Cross-cue "dark contact" detection (non-cooperative radar/EO tracks) — `crosscue`.
- Coverage & cost-per-hour vs legacy baseline — `coverage`.
- GeoJSON track export — `geojson`.
- Deterministic synthetic multi-sensor generator with planted ground truth — `synth`.
- CLI (`cognis-vigil`): `demo`, `fuse`, `coverage`.
- Verification harness: track-association + dark-contact metrics + performance;
  results in `RESULTS.md`. 9 tests. GitHub Actions CI across Python 3.9–3.13.
