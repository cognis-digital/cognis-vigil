"""Observer — live situational-awareness analytics over fused contacts.

The value layer a tactical ISR HUD sells (zone occupancy, density/activity level,
flow trend, a plain-language scene read-out, a saved tactical report) — here as
zero-dependency, offline, auditable output on top of scryer's *multi-sensor
fusion*. Unlike a single-camera YOLO overlay, it reads across EO/IR + radar +
AIS/ADS-B and flags **non-cooperative ("dark") contacts** — the thing a
cooperative-only feed misses. Non-kinetic: it describes a scene, it does not
target anything.
"""

from __future__ import annotations

from collections import Counter

# density buckets on contacts per 1,000 km² (or raw count if no area given)
_DENSITY = [(0, "clear"), (4, "light"), (12, "moderate"), (28, "high"), (55, "packed")]
_COOPERATIVE = {"ais", "adsb"}


def _klass(d):
    return (d.meta or {}).get("class") or d.domain


def counts_by(dets, key):
    return dict(Counter(key(d) for d in dets).most_common())


def zone_occupancy(dets, zones):
    """zones: [{"name","bbox":(w,s,e,n)}] → {name: count} (+ '_outside')."""
    out = {z["name"]: 0 for z in zones}
    out["_outside"] = 0
    for d in dets:
        placed = False
        for z in zones:
            w, s, e, n = z["bbox"]
            if w <= d.lon <= e and s <= d.lat <= n:
                out[z["name"]] += 1
                placed = True
                break
        if not placed:
            out["_outside"] += 1
    return out


def density_level(count, area_km2=None):
    metric = count if not area_km2 else count / (area_km2 / 1000.0)
    level = "clear"
    for thr, name in _DENSITY:
        if metric >= thr:
            level = name
    return level, round(metric, 1)


def flow_trend(series):
    """series: contact counts over time bins (oldest→newest) → (direction, delta)."""
    if len(series) < 2:
        return "steady", 0.0
    h = len(series) // 2
    early = sum(series[:h]) / max(1, h)
    late = sum(series[h:]) / max(1, len(series) - h)
    delta = late - early
    d = "rising" if delta > 0.5 else ("easing" if delta < -0.5 else "steady")
    return d, round(delta, 2)


def observe(dets, zones=None, area_km2=None, series=None):
    total = len(dets)
    by_class = counts_by(dets, _klass)
    by_sensor = counts_by(dets, lambda d: d.sensor)
    level, metric = density_level(total, area_km2)
    direction, delta = flow_trend(series or [])
    noncoop = [d for d in dets if d.sensor not in _COOPERATIVE]
    occ = zone_occupancy(dets, zones) if zones else {}
    hot = None
    if occ:
        named = {k: v for k, v in occ.items() if k != "_outside"}
        if named and max(named.values()) > 0:
            hot = max(named, key=named.get)
    report = {
        "total_contacts": total, "by_class": by_class, "by_sensor": by_sensor,
        "density": {"level": level, "metric": metric},
        "flow": {"trend": direction, "delta": delta},
        "noncooperative": len(noncoop),           # scryer's edge over camera-only tools
        "zones": occ, "hottest_zone": hot,
        "summary": scene_summary(total, by_class, level, hot, occ, len(noncoop), direction),
    }
    return report


def scene_summary(total, by_class, level, hot, occ, noncoop, trend):
    cls = ", ".join(f"{v} {k}" for k, v in by_class.items()) or "no"
    parts = [f"{total} contacts ({cls})", f"{level} density", f"activity {trend}"]
    if hot:
        parts.append(f"highest in {hot} ({occ[hot]})")
    if noncoop:
        parts.append(f"{noncoop} non-cooperative/dark")
    return "; ".join(parts) + "."


def render_text(report, title="SCRYER // OBSERVER"):
    L = [f"== {title} ==", report["summary"], "",
         f"contacts: {report['total_contacts']}  "
         f"density: {report['density']['level']} ({report['density']['metric']})  "
         f"flow: {report['flow']['trend']} ({report['flow']['delta']:+})",
         f"non-cooperative (dark): {report['noncooperative']}",
         "by class:  " + ", ".join(f"{k}={v}" for k, v in report["by_class"].items()),
         "by sensor: " + ", ".join(f"{k}={v}" for k, v in report["by_sensor"].items())]
    if report["zones"]:
        L.append("zones:     " + ", ".join(f"{k}={v}" for k, v in report["zones"].items()
                                            if k != "_outside"))
    return "\n".join(L)
