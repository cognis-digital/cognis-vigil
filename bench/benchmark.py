"""Performance benchmark: detection-fusion throughput."""

from __future__ import annotations

import json
import time

from cognis_vigil import synth
from cognis_vigil.fusion import correlate


def benchmark(sizes=(50, 150, 400)) -> list:
    rows = []
    for n in sizes:
        dets, _ = synth.generate(n_maritime=n, n_dark=max(1, n // 10), n_air=n // 2, fixes=6)
        t0 = time.perf_counter()
        tracks = correlate(dets)
        dt = time.perf_counter() - t0
        rows.append({"contacts": n + max(1, n // 10) + n // 2, "detections": len(dets),
                     "tracks": len(tracks), "fuse_s": round(dt, 4),
                     "detections_per_s": int(len(dets) / dt) if dt > 0 else None})
    return rows


def main():
    print(json.dumps(benchmark(), indent=2))


if __name__ == "__main__":
    main()
