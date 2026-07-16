"""Coverage & cost-per-hour modeling + gap analysis."""

from scryer.coverage import coverage_gap, coverage_plan

FLEET = [
    {"name": "a", "coverage_km2": 120000, "cost_per_hour": 3500, "dwell_hours": 24},
    {"name": "b", "coverage_km2": 40000, "cost_per_hour": 1800, "dwell_hours": 16},
]


def test_plan_aggregates_fleet():
    plan = coverage_plan(FLEET, 250000, 22000)
    assert plan["platforms"] == 2
    assert plan["total_coverage_km2"] == 160000
    assert plan["fleet_cost_per_hour"] == 5300
    assert plan["max_dwell_hours"] == 24


def test_cost_savings_fraction():
    plan = coverage_plan(FLEET, 250000, 22000)
    # (22000 - 5300) / 22000
    assert plan["cost_per_hour_savings"] == round((22000 - 5300) / 22000, 4)
    assert 0.0 < plan["cost_per_hour_savings"] < 1.0


def test_coverage_ratio_capped_at_one():
    plan = coverage_plan(FLEET, 100000, 22000)  # coverage exceeds area
    assert plan["coverage_ratio"] == 1.0


def test_zero_area_and_zero_legacy_are_safe():
    plan = coverage_plan(FLEET, 0, 0)
    assert plan["coverage_ratio"] == 0.0
    assert plan["cost_per_hour_savings"] == 0.0


def test_negative_savings_when_fleet_costlier():
    pricey = [{"name": "x", "coverage_km2": 10000, "cost_per_hour": 50000, "dwell_hours": 8}]
    assert coverage_plan(pricey, 100000, 22000)["cost_per_hour_savings"] < 0


def test_coverage_gap_uncovered_and_platforms_needed():
    gap = coverage_gap(FLEET, 250000)
    assert gap["uncovered_km2"] == 90000
    assert gap["covered_ratio"] == round(160000 / 250000, 4)
    # avg footprint 80000 -> ceil(90000/80000) == 2 more platforms
    assert gap["additional_platforms_needed"] == 2
    assert gap["marginal_cost_per_hour"] == 2 * ((3500 + 1800) / 2)


def test_coverage_gap_fully_covered_needs_nothing():
    gap = coverage_gap(FLEET, 100000)
    assert gap["uncovered_km2"] == 0.0
    assert gap["additional_platforms_needed"] == 0
    assert gap["marginal_cost_per_hour"] == 0.0


def test_coverage_gap_empty_fleet():
    gap = coverage_gap([], 100000)
    assert gap["uncovered_km2"] == 100000
    assert gap["additional_platforms_needed"] == 0  # no footprint to size from
