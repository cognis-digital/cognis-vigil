# Changelog

Adheres to [Semantic Versioning](https://semver.org/).

## [0.3.0] — 2026-07-02

### Added
- **Small / point-target detection for search-and-rescue** (`smalltarget.py`):
  CA-CFAR (cell-averaging constant-false-alarm-rate) detection to pull a 1–2 pixel
  target — a swimmer lost at sea, a small craft — out of sea/ground clutter, plus
  temporal background subtraction (`detect_in_video`) to surface a moving/bobbing
  target across video frames.
- `imagery.py` bridges detected blobs into geolocated Detections that flow through
  fusion / cross-cue / motion (imagery target → track → projected drift).
- CLI `search` (image + `--video`); small-target recall gated in CI.
- Verified: recovers all planted point targets (recall 1.0) at 6–10 sigma with
  low false alarms; moving swimmer recovered from video.

## [0.2.0] — 2026-07-02

### Added
- **Constant-velocity motion model** (`motion.py`): alpha-beta track smoothing +
  future-position prediction. Dark contacts now include a projected next position
  (interdiction cueing — non-kinetic projected intercept, not a firing solution).

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
