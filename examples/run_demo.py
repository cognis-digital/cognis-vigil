"""End-to-end example. Run from repo root:  python examples/run_demo.py"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cognis_vigil import synth  # noqa: E402
from cognis_vigil.crosscue import find_dark_contacts  # noqa: E402
from cognis_vigil.fusion import correlate  # noqa: E402

dets, _ = synth.generate()
tracks = correlate(dets)
dark = find_dark_contacts(tracks)
print(f"{len(dets)} detections -> {len(tracks)} tracks; {len(dark)} dark contacts:")
for d in dark:
    print(f"  {d['track_id']} conf={d['confidence']} sensors={d['sensors']}")
