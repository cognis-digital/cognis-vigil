"""Detection and Track data structures."""

from __future__ import annotations

from dataclasses import dataclass, field

MARITIME_SENSORS = {"radar", "eo", "ir", "ais", "sar"}
AIR_SENSORS = {"radar", "eo", "ir", "adsb"}


@dataclass
class Detection:
    id: str
    ts: float          # epoch seconds
    lat: float
    lon: float
    sensor: str        # radar | eo | ir | ais | adsb | sar
    domain: str        # maritime | air
    source: str = ""
    meta: dict = field(default_factory=dict)

    def to_dict(self):
        return {"id": self.id, "ts": self.ts, "lat": self.lat, "lon": self.lon,
                "sensor": self.sensor, "domain": self.domain, "source": self.source,
                "meta": self.meta}


@dataclass
class Track:
    id: str
    domain: str
    detections: list = field(default_factory=list)

    @property
    def sensors(self):
        return {d.sensor for d in self.detections}

    @property
    def has_ais(self):
        return "ais" in self.sensors or "adsb" in self.sensors

    def to_dict(self):
        return {"id": self.id, "domain": self.domain,
                "sensors": sorted(self.sensors), "has_cooperative": self.has_ais,
                "detections": [d.id for d in self.detections],
                "length": len(self.detections)}
