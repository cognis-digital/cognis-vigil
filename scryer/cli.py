"""Scryer CLI."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__, synth
from .coverage import coverage_plan
from .crosscue import find_dark_contacts
from .fusion import correlate, load_detections
from .geojson import to_json, tracks_to_geojson
from .report import render_json, render_text

DEMO_FLEET = [
    {"name": "HALE-UAS", "coverage_km2": 120000, "cost_per_hour": 3500, "dwell_hours": 24},
    {"name": "MALE-UAS", "coverage_km2": 40000, "cost_per_hour": 1800, "dwell_hours": 16},
    {"name": "coastal-radar-net", "coverage_km2": 30000, "cost_per_hour": 300, "dwell_hours": 24},
]
LEGACY_CPH = 22000  # legacy manned maritime patrol, illustrative


def _build(detections, with_coverage=True):
    tracks = correlate(detections)
    dark = find_dark_contacts(tracks)
    product = {
        "detections": len(detections), "tracks": len(tracks),
        "dark_contacts": dark,
        "track_summary": [t.to_dict() for t in tracks],
    }
    if with_coverage:
        product["coverage"] = coverage_plan(DEMO_FLEET, 250000, LEGACY_CPH)
    return product, tracks, dark


def cmd_demo(args):
    dets, _ = synth.generate()
    product, tracks, dark = _build(dets)
    print(render_text(product))
    if args.geojson:
        with open(args.geojson, "w", encoding="utf-8") as f:
            f.write(to_json(tracks_to_geojson(tracks, {d["track_id"] for d in dark})))
        print(f"\n[+] GeoJSON -> {args.geojson}")
    return 0


def cmd_fuse(args):
    dets = load_detections(args.detections)
    product, _, _ = _build(dets, with_coverage=False)
    print(render_json(product) if args.json else render_text(product))
    return 0


def cmd_coverage(args):
    with open(args.platforms, "r", encoding="utf-8") as f:
        platforms = json.load(f)
    print(json.dumps(coverage_plan(platforms, args.area, args.legacy), indent=2))
    return 0


def cmd_search(args):
    """Small/point-target search-and-rescue demo (swimmer / small craft in EO/IR)."""
    from . import synth
    from .smalltarget import detect_in_video, detect_small_targets, detect_with_stacking, pfa_to_k
    k = pfa_to_k(args.pfa) if args.pfa else args.k
    if args.stack:
        vid, tpt = synth.video_faint_static()
        single = detect_small_targets(vid[0], k=k)
        blobs = detect_with_stacking(vid, k=k)
        truth = {tpt}
        medium = f"{len(vid)}-frame SNR-stack (faint static target; single-frame found {len(single)})"
    elif args.video:
        vid, truth = synth.video_with_target()
        blobs = detect_in_video(vid, k=k)
        medium = f"{len(vid)}-frame video (temporal background subtraction)"
    else:
        img, truth = synth.scene_with_targets()
        blobs = detect_small_targets(img, k=k)
        medium = f"{len(img)}x{len(img[0])} scene (CA-CFAR)"
    print(f"COGNIS VIGIL | small-target search over {medium}")
    print(f"planted targets: {len(truth)}   detections: {len(blobs)}   (k={round(k,2)} sigma)")
    for i, b in enumerate(blobs[:10], 1):
        print(f"  [{i}] pixel ({b['row']},{b['col']}) size={b['size']}px "
              f"SNR={b['peak_snr']} conf={b['confidence']:.2f}")
    print("NOTE: non-kinetic search leads; corroborate before tasking assets.")
    return 0


def cmd_heatmap(args):
    from . import synth
    from .heatmap import ascii_preview, heatmap_from_image, heatmap_geojson, to_json
    img, truth = synth.scene_with_targets()
    grid = heatmap_from_image(img, cell=8)
    print(f"COGNIS VIGIL | georeferenced search-priority heatmap ({len(grid)}x{len(grid[0])} cells)")
    print(ascii_preview(grid))
    if args.geojson:
        gt = {"origin_lat": 9.5, "origin_lon": -79.9, "dlat": -0.001, "dlon": 0.001}
        with open(args.geojson, "w", encoding="utf-8") as f:
            f.write(to_json(heatmap_geojson(grid, gt, cell=8)))
        print(f"[+] heatmap GeoJSON -> {args.geojson}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="scryer",
                                description="Scryer — multi-domain ISR fusion (non-kinetic)")
    p.add_argument("--version", action="version", version=f"scryer {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("demo", help="end-to-end demo on synthetic multi-sensor data")
    d.add_argument("--geojson")
    d.set_defaults(func=cmd_demo)

    f = sub.add_parser("fuse", help="correlate detections into tracks + dark contacts")
    f.add_argument("--detections", required=True)
    f.add_argument("--json", action="store_true")
    f.set_defaults(func=cmd_fuse)

    c = sub.add_parser("coverage", help="coverage & cost-per-hour vs legacy baseline")
    c.add_argument("--platforms", required=True)
    c.add_argument("--area", type=float, required=True)
    c.add_argument("--legacy", type=float, required=True)
    c.set_defaults(func=cmd_coverage)

    s = sub.add_parser("search", help="small-target search-and-rescue (swimmer/small craft)")
    s.add_argument("--video", action="store_true", help="temporal video detection")
    s.add_argument("--stack", action="store_true", help="SNR frame-stacking for a faint static target")
    s.add_argument("--k", type=float, default=5.0, help="CFAR threshold (sigma)")
    s.add_argument("--pfa", type=float, help="target probability of false alarm (overrides --k)")
    s.set_defaults(func=cmd_search)

    h = sub.add_parser("heatmap", help="georeferenced detection-confidence heatmap")
    h.add_argument("--geojson", help="write heatmap GeoJSON to this path")
    h.set_defaults(func=cmd_heatmap)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
