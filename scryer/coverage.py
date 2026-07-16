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


def coverage_gap(platforms: list, area_km2: float) -> dict:
    """Quantify the shortfall between fleet coverage and the area of interest.

    Returns the uncovered area (km^2), the covered fraction, and — using the
    mean per-platform footprint as a unit — how many additional like platforms
    would be needed to close the gap and their marginal cost/hour. Purely an
    analysis helper over ``platforms``; it does not modify ``coverage_plan``.
    """
    total_coverage = sum(p["coverage_km2"] for p in platforms)
    uncovered = max(0.0, area_km2 - total_coverage)
    covered_ratio = round(min(1.0, total_coverage / area_km2), 4) if area_km2 else 0.0
    n = len(platforms)
    avg_footprint = (total_coverage / n) if n else 0.0
    avg_cost = (sum(p["cost_per_hour"] for p in platforms) / n) if n else 0.0
    import math as _math
    add_needed = int(_math.ceil(uncovered / avg_footprint)) if avg_footprint > 0 and uncovered > 0 else 0
    return {
        "area_km2": area_km2,
        "total_coverage_km2": total_coverage,
        "uncovered_km2": round(uncovered, 2),
        "covered_ratio": covered_ratio,
        "avg_platform_footprint_km2": round(avg_footprint, 2),
        "additional_platforms_needed": add_needed,
        "marginal_cost_per_hour": round(add_needed * avg_cost, 2),
    }
