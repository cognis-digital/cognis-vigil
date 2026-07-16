"""CSV exporters for tracks and dark-contact leads."""

import csv
import io

from scryer import synth
from scryer.crosscue import find_dark_contacts
from scryer.export import (
    DARK_FIELDS,
    TRACK_FIELDS,
    dark_contacts_to_csv,
    tracks_to_csv,
    tracks_to_rows,
    write_csv,
)
from scryer.fusion import correlate


def _parse(text):
    return list(csv.DictReader(io.StringIO(text)))


def test_tracks_csv_header_and_row_count():
    tracks = correlate(synth.generate()[0])
    rows = _parse(tracks_to_csv(tracks))
    assert list(rows[0].keys()) == TRACK_FIELDS
    assert len(rows) == len(tracks)


def test_tracks_csv_marks_dark_column():
    tracks = correlate(synth.generate()[0])
    dark_ids = {d["track_id"] for d in find_dark_contacts(tracks)}
    rows = _parse(tracks_to_csv(tracks, dark_ids))
    dark_rows = [r for r in rows if r["dark"] == "True"]
    assert len(dark_rows) == len(dark_ids)
    for r in dark_rows:
        assert r["track_id"] in dark_ids


def test_tracks_rows_include_kinematics_and_classification():
    tracks = correlate(synth.generate()[0])
    rows = tracks_to_rows(tracks)
    for r in rows:
        assert "classification" in r and "max_speed_kmh" in r
        assert r["classification"] in (
            "fast-mover", "transiter", "loiterer", "stationary", "indeterminate")


def test_sensors_column_is_pipe_joined():
    tracks = correlate(synth.generate()[0])
    rows = _parse(tracks_to_csv(tracks))
    assert all("," not in r["sensors"] for r in rows)  # comma-free (pipe-delimited)


def test_dark_csv_header_and_ranking():
    tracks = correlate(synth.generate()[0])
    dark = find_dark_contacts(tracks)
    rows = _parse(dark_contacts_to_csv(dark))
    assert list(rows[0].keys()) == DARK_FIELDS
    confs = [float(r["confidence"]) for r in rows]
    assert confs == sorted(confs, reverse=True)


def test_dark_csv_carries_prediction_columns():
    tracks = correlate(synth.generate()[0])
    dark = find_dark_contacts(tracks)
    rows = _parse(dark_contacts_to_csv(dark))
    assert rows and rows[0]["pred_lat"] not in ("", None)


def test_empty_inputs_produce_header_only():
    assert _parse(tracks_to_csv([])) == []
    assert _parse(dark_contacts_to_csv([])) == []
    # header line still present
    assert tracks_to_csv([]).splitlines()[0].startswith("track_id")


def test_write_csv_is_utf8_without_bom(tmp_path):
    p = tmp_path / "out.csv"
    write_csv(str(p), tracks_to_csv(correlate(synth.generate()[0])))
    raw = p.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")  # no BOM
    assert p.read_text(encoding="utf-8").startswith("track_id")
