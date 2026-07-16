# Usage

Scryer is usable as a **CLI** (`scryer …` or `python -m scryer …`) and as a
**library**. Everything is stdlib; nothing here needs network or third-party
packages.

## CLI

### `demo`
End-to-end run on the built-in synthetic scenario.

```bash
python -m scryer demo --geojson tracks.geojson --csv tracks.csv --kinematics
```

| Flag | Effect |
|---|---|
| `--geojson PATH` | write track GeoJSON (dark contacts flagged) |
| `--csv PATH` | write a per-track CSV including kinematics + classification |
| `--kinematics` | enrich the printed dark contacts with speed/heading + label |

### `fuse`
Fuse your own detections file.

```bash
python -m scryer fuse --detections dets.json --json --csv tracks.csv
```

`dets.json` is a JSON list of detection records (see the README). `--json`
prints the machine-readable product; `--csv` additionally writes a track CSV.

### `export`
Non-interactive product generation from a detections file.

```bash
python -m scryer export --detections dets.json \
    --geojson tracks.geojson --csv tracks.csv --dark-csv leads.csv
```

Writes any combination of a track GeoJSON, a per-track CSV, and a
confidence-ranked dark-contact **lead** CSV. Exits non-zero if no output flag is
given.

### `coverage`
Cost-per-hour vs a legacy baseline.

```bash
python -m scryer coverage --platforms fleet.json --area 250000 --legacy 22000
```

`fleet.json` is a list of `{name, coverage_km2, cost_per_hour, dwell_hours}`.

### `search`
Small / point-target search-and-rescue.

```bash
python -m scryer search                 # single frame (CA-CFAR)
python -m scryer search --video         # temporal background subtraction
python -m scryer search --stack         # SNR frame-stacking (faint static target)
python -m scryer search --pfa 1e-5      # set threshold from a false-alarm rate
```

### `heatmap`
Georeferenced search-priority heatmap (ASCII preview + optional GeoJSON).

```bash
python -m scryer heatmap --geojson heat.geojson
```

## Library

### Fuse detections into tracks
```python
from scryer.model import Detection
from scryer.fusion import correlate

dets = [
    Detection(id="d1", ts=1_700_000_000.0, lat=9.50, lon=-79.30, sensor="radar", domain="maritime"),
    Detection(id="d2", ts=1_700_000_300.0, lat=9.51, lon=-79.30, sensor="eo",    domain="maritime"),
]
tracks = correlate(dets, max_speed_kmh=80.0, max_gap_s=1800.0)
```

### Surface dark contacts (with kinematics)
```python
from scryer.crosscue import find_dark_contacts

leads = find_dark_contacts(tracks, min_fixes=2, with_kinematics=True)
for lead in leads:
    print(lead["track_id"], lead["confidence"],
          lead["classification"], lead["kinematics"]["max_speed_kmh"],
          lead["predicted_next"])
```

### Per-track kinematics & classification
```python
from scryer.kinematics import track_kinematics, classify_track

k = track_kinematics(tracks[0])
# {'fixes':.., 'distance_km':.., 'duration_s':.., 'mean_speed_kmh':..,
#  'max_speed_kmh':.., 'heading_deg':.., 'straightness':..}
label = classify_track(tracks[0], fast_kmh=55.0)  # fast-mover|transiter|loiterer|stationary
```

### Export products
```python
from scryer.geojson import tracks_to_geojson, to_json
from scryer.export import tracks_to_csv, dark_contacts_to_csv, write_csv

dark_ids = {d["track_id"] for d in leads}
write_csv("tracks.csv", tracks_to_csv(tracks, dark_ids))
write_csv("leads.csv", dark_contacts_to_csv(leads))
open("tracks.geojson", "w", encoding="utf-8").write(to_json(tracks_to_geojson(tracks, dark_ids)))
```

### Coverage & gap analysis
```python
from scryer.coverage import coverage_plan, coverage_gap

fleet = [{"name": "a", "coverage_km2": 120000, "cost_per_hour": 3500, "dwell_hours": 24}]
plan = coverage_plan(fleet, area_km2=250000, legacy_cost_per_hour=22000)
gap  = coverage_gap(fleet, area_km2=250000)   # uncovered_km2, additional_platforms_needed, marginal_cost_per_hour
```

### Small-target detection from imagery
```python
from scryer.smalltarget import detect_small_targets, detect_with_stacking
from scryer.imagery import search_image

blobs = detect_small_targets(image, k=5.0)              # image = 2-D list of intensities
faint = detect_with_stacking(frames, k=5.0)             # recover a faint static target
gt = {"origin_lat": 9.5, "origin_lon": -79.9, "dlat": -0.001, "dlon": 0.001}
dets = search_image(image, gt, k=5.0)                   # geolocated Detections for fusion
```

## Reproducing the verification numbers

```bash
PYTHONUTF8=1 python -m pytest -q      # 122 tests
PYTHONUTF8=1 python bench/run_all.py  # writes bench/results.json + RESULTS.md
```
