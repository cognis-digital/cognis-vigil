"""Georeferenced detection-confidence heatmap.

Downsamples the dense CA-CFAR SNR surface into cells, georeferences each cell via
the scene geotransform, and exports the heatmap as GeoJSON polygons (graded by
intensity), CSV, or a compact ASCII preview — a shareable search-priority surface
for tasking assets over an area of interest.
"""

from __future__ import annotations

import json

from .smalltarget import snr_map


def downsample_max(snr, cell: int = 8) -> list:
    H = len(snr)
    W = len(snr[0]) if H else 0
    rows = (H + cell - 1) // cell
    cols = (W + cell - 1) // cell
    grid = [[0.0] * cols for _ in range(rows)]
    for r in range(H):
        for c in range(W):
            v = snr[r][c]
            gr, gc = r // cell, c // cell
            if v > grid[gr][gc]:
                grid[gr][gc] = round(v, 3)
    return grid


def heatmap_from_image(image, cell: int = 8, guard: int = 1, train: int = 4) -> list:
    return downsample_max(snr_map(image, guard, train), cell)


def _cell_polygon(gr, gc, cell, gt):
    def ll(row, col):
        return [round(gt["origin_lon"] + col * gt["dlon"], 6),
                round(gt["origin_lat"] + row * gt["dlat"], 6)]
    r0, c0, r1, c1 = gr * cell, gc * cell, (gr + 1) * cell, (gc + 1) * cell
    return [[ll(r0, c0), ll(r0, c1), ll(r1, c1), ll(r1, c0), ll(r0, c0)]]


def heatmap_geojson(grid, geotransform, cell: int = 8, snr_floor: float = 3.0) -> dict:
    feats = []
    for gr, row in enumerate(grid):
        for gc, v in enumerate(row):
            if v >= snr_floor:
                feats.append({
                    "type": "Feature",
                    "geometry": {"type": "Polygon", "coordinates": _cell_polygon(gr, gc, cell, geotransform)},
                    "properties": {"snr": v, "intensity": round(min(1.0, v / 12.0), 3),
                                   "priority": "high" if v >= 8 else "medium" if v >= 5 else "low"},
                })
    return {"type": "FeatureCollection", "features": feats}


def to_json(fc, indent: int = 2) -> str:
    return json.dumps(fc, indent=indent)


def ascii_preview(grid, ramp=" .:-=+*#%@") -> str:
    hi = max((max(row) for row in grid if row), default=1.0) or 1.0
    lines = []
    for row in grid:
        lines.append("".join(ramp[min(len(ramp) - 1, int((v / hi) * (len(ramp) - 1)))] for v in row))
    return "\n".join(lines)
