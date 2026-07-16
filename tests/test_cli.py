"""End-to-end CLI behavior via scryer.cli.main."""

import json

import pytest

from scryer import synth
from scryer.cli import main


def _write_dets(tmp_path):
    dets, _ = synth.generate()
    p = tmp_path / "dets.json"
    p.write_text(json.dumps([d.to_dict() for d in dets]), encoding="utf-8")
    return str(p)


def test_version(capsys):
    with pytest.raises(SystemExit) as e:
        main(["--version"])
    assert e.value.code == 0
    assert "scryer" in capsys.readouterr().out


def test_no_command_errors():
    with pytest.raises(SystemExit) as e:
        main([])
    assert e.value.code != 0


def test_demo_runs_and_reports(capsys):
    assert main(["demo"]) == 0
    out = capsys.readouterr().out
    assert "Multi-Domain ISR Fusion" in out
    assert "Dark contacts" in out


def test_demo_writes_geojson_and_csv(tmp_path, capsys):
    gj = tmp_path / "tracks.geojson"
    csvp = tmp_path / "tracks.csv"
    assert main(["demo", "--geojson", str(gj), "--csv", str(csvp), "--kinematics"]) == 0
    fc = json.loads(gj.read_text(encoding="utf-8"))
    assert fc["type"] == "FeatureCollection" and fc["features"]
    assert csvp.read_text(encoding="utf-8").splitlines()[0].startswith("track_id")


def test_fuse_json_output(tmp_path, capsys):
    dets = _write_dets(tmp_path)
    assert main(["fuse", "--detections", dets, "--json"]) == 0
    product = json.loads(capsys.readouterr().out)
    assert product["detections"] > 0 and "dark_contacts" in product
    assert "coverage" not in product  # fuse omits coverage


def test_fuse_csv_side_output(tmp_path, capsys):
    dets = _write_dets(tmp_path)
    csvp = tmp_path / "f.csv"
    assert main(["fuse", "--detections", dets, "--csv", str(csvp)]) == 0
    assert csvp.exists() and csvp.read_text(encoding="utf-8").startswith("track_id")


def test_coverage_subcommand(tmp_path, capsys):
    plats = tmp_path / "p.json"
    plats.write_text(json.dumps(
        [{"name": "a", "coverage_km2": 100000, "cost_per_hour": 3000, "dwell_hours": 20}]),
        encoding="utf-8")
    assert main(["coverage", "--platforms", str(plats), "--area", "250000",
                 "--legacy", "22000"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["cost_per_hour_savings"] > 0


def test_export_writes_all_three_products(tmp_path, capsys):
    dets = _write_dets(tmp_path)
    gj, csvp, dcsv = tmp_path / "e.geojson", tmp_path / "e.csv", tmp_path / "e_dark.csv"
    rc = main(["export", "--detections", dets, "--geojson", str(gj),
               "--csv", str(csvp), "--dark-csv", str(dcsv)])
    assert rc == 0
    assert json.loads(gj.read_text(encoding="utf-8"))["type"] == "FeatureCollection"
    assert csvp.read_text(encoding="utf-8").startswith("track_id")
    assert dcsv.read_text(encoding="utf-8").startswith("track_id,domain,confidence")


def test_export_with_no_outputs_returns_nonzero(tmp_path, capsys):
    dets = _write_dets(tmp_path)
    assert main(["export", "--detections", dets]) == 2


def test_search_and_heatmap_smoke(capsys):
    assert main(["search"]) == 0
    assert "small-target search" in capsys.readouterr().out
    assert main(["heatmap"]) == 0
    assert "heatmap" in capsys.readouterr().out.lower()
