"""Cognis Vigil CLI."""

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
    from .smalltarget import detect_in_video, detect_small_targets
    if args.video:
        vid, truth = synth.video_with_target()
        blobs = detect_in_video(vid, k=args.k)
        medium = f"{len(vid)}-frame video (temporal background subtraction)"
    else:
        img, truth = synth.scene_with_targets()
        blobs = detect_small_targets(img, k=args.k)
        medium = f"{len(img)}x{len(img[0])} scene (CA-CFAR)"
    print(f"COGNIS VIGIL | small-target search over {medium}")
    print(f"planted targets: {len(truth)}   detections: {len(blobs)}   (k={args.k} sigma)")
    for i, b in enumerate(blobs[:10], 1):
        print(f"  [{i}] pixel ({b['row']},{b['col']}) size={b['size']}px "
              f"SNR={b['peak_snr']} conf={b['confidence']:.2f}")
    print("NOTE: non-kinetic search leads; corroborate before tasking assets.")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="cognis-vigil",
                                description="Cognis Vigil — multi-domain ISR fusion (non-kinetic)")
    p.add_argument("--version", action="version", version=f"cognis-vigil {__version__}")
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
    s.add_argument("--video", action="store_true", help="use temporal video detection")
    s.add_argument("--k", type=float, default=5.0, help="CFAR threshold (sigma)")
    s.set_defaults(func=cmd_search)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
