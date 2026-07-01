"""Human-readable / JSON ISR fusion products."""

from __future__ import annotations

import json


def render_json(product) -> str:
    return json.dumps(product, indent=2)


def render_text(product) -> str:
    L = []
    L.append("=" * 72)
    L.append("  COGNIS VIGIL  |  Multi-Domain ISR Fusion (detection & monitoring)")
    L.append("  Cognis Digital LLC - non-kinetic; leads for law-enforcement interdiction")
    L.append("=" * 72)
    L.append(f"Detections: {product['detections']}   Tracks: {product['tracks']}")
    L.append(f"Dark contacts (no cooperative report): {len(product['dark_contacts'])}")
    L.append("")
    for i, d in enumerate(product["dark_contacts"][:10], 1):
        L.append(f"  [{i}] {d['track_id']} {d['domain']:8} conf={d['confidence']:.2f} "
                 f"fixes={d['fixes']} sensors={','.join(d['sensors'])} "
                 f"@({d['last_lat']:.3f},{d['last_lon']:.3f})")
    cov = product.get("coverage")
    if cov:
        L.append("")
        L.append(f"Coverage: {cov['coverage_ratio']*100:.0f}% of {cov['area_km2']:,} km^2 "
                 f"with {cov['platforms']} platforms")
        L.append(f"Cost/hour: ${cov['fleet_cost_per_hour']:,} vs legacy ${cov['legacy_cost_per_hour']:,} "
                 f"=> {cov['cost_per_hour_savings']*100:.0f}% lower")
    L.append("")
    L.append("NOTE: Detection/monitoring only. Confidence-scored leads require corroboration.")
    return "\n".join(L)
