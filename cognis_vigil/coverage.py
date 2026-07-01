"""Coverage & cost-per-hour modeling vs a legacy baseline.

Directly addresses the challenge metric: 'cost per hour of coverage materially
lower than current legacy ISR systems.'
"""

from __future__ import annotations


def coverage_plan(platforms: list, area_km2: float, legacy_cost_per_hour: float) -> dict:
    """platforms: [{name, coverage_km2, cost_per_hour, dwell_hours}]"""
    total_coverage = sum(p["coverage_km2"] for p in platforms)
    fleet_cost_per_hour = sum(p["cost_per_hour"] for p in platforms)
    coverage_ratio = round(min(1.0, total_coverage / area_km2), 4) if area_km2 else 0.0
    max_dwell = max((p.get("dwell_hours", 0) for p in platforms), default=0)
    savings = 0.0
    if legacy_cost_per_hour:
        savings = round((legacy_cost_per_hour - fleet_cost_per_hour) / legacy_cost_per_hour, 4)
    return {
        "platforms": len(platforms),
        "area_km2": area_km2,
        "total_coverage_km2": total_coverage,
        "coverage_ratio": coverage_ratio,
        "fleet_cost_per_hour": round(fleet_cost_per_hour, 2),
        "legacy_cost_per_hour": legacy_cost_per_hour,
        "cost_per_hour_savings": savings,
        "max_dwell_hours": max_dwell,
    }
