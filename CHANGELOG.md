# Changelog

Adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- **Per-track kinematics** (`kinematics.py`): speed, heading, path length,
  duration and straightness, plus a transparent behavior classifier
  (`fast-mover` / `transiter` / `loiterer` / `stationary`) surfacing the go-fast
  signature. Great-circle `initial_bearing` and `destination_point` helpers
  added to `geo.py`.
- **CSV exporters** (`export.py`): flat per-track CSV (with kinematics +
  classification) and a confidence-ranked dark-contact lead CSV for spreadsheet
  triage and case management.
- **Coverage gap analysis** (`coverage.coverage_gap`): uncovered area, covered
  fraction, and the marginal platforms/cost to close the gap.
- **CLI `export`** subcommand (GeoJSON + track CSV + dark-contact lead CSV) and
  `--csv` / `--kinematics` flags on `demo` and `fuse`.
- **Opt-in kinematics enrichment** on `crosscue.find_dark_contacts`
  (`with_kinematics=True`) — additive keys; default output unchanged.
- **Docs**: overhauled README (architecture, install, config reference, FAQ);
  new `docs/USAGE.md`; expanded `docs/ARCHITECTURE.md`; `ROADMAP.md`.
- **Tests & CI**: 101 new tests (122 total). CI adds a ruff lint job, an
  editable-install packaging smoke test, and a CLI end-to-end product-export job;
  `py.typed` marker and a `[dev]` extra.

### Notes
- Fully backward compatible: no files removed, no public function or CLI entry
  point changed; all additions are new modules, new flags, or opt-in parameters.

## [0.4.0] — 2026-07-02

### Added
- **SNR frame-stacking** (`detect_with_stacking`): coherently averages N frames to
  recover a faint static target below single-frame detectability (verified: a
  target invisible in one frame is recovered after stacking).
- **Pfa-controlled CFAR** (`pfa_to_k`): set the detection threshold from a target
  probability of false alarm; `search --pfa`.
- **Georeferenced confidence heatmap** (`heatmap.py`): dense CA-CFAR SNR surface
  downsampled to cells, exported as GeoJSON priority polygons / ASCII preview;
  CLI `heatmap`.
- **ROC characterization** in `bench/` (Pd vs false alarms across thresholds,
  monotonicity gated) and an honest `docs/COMPLIANCE.md` posture statement.

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
- CLI (`scryer`): `demo`, `fuse`, `coverage`.
- Verification harness: track-association + dark-contact metrics + performance;
  results in `RESULTS.md`. 9 tests. GitHub Actions CI across Python 3.9–3.13.
