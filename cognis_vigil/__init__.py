"""Cognis Vigil — multi-domain ISR sensor fusion for counternarcotics.

Correlates EO/IR, radar, AIS (maritime) and ADS-B (air) detections into tracks,
flags "dark" contacts (radar/EO detections with no corresponding AIS — a
signature of go-fast vessels and semi-submersibles), and models coverage
cost-per-hour against a legacy baseline. Detection and monitoring only — this is
explicitly NOT a targeting or kinetic-finish capability.

(c) 2026 Cognis Digital LLC (Wyoming, USA). Source-available under COCL-1.0.
"""

__version__ = "0.3.0"
__all__ = ["geo", "model", "fusion", "motion", "crosscue", "coverage",
           "smalltarget", "imagery", "geojson", "report", "synth"]
