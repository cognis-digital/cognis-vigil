"""Bridge small-target imagery detections into the tracking pipeline.

Turns detected blobs (from a single image or a video stack) into geolocated
Detections that flow through fusion / cross-cue / motion just like any other
sensor — so a swimmer or small craft found in EO/IR imagery becomes a track with
a projected drift position (non-kinetic search lead).
"""

from __future__ import annotations

from .model import Detection
from .smalltarget import detect_in_video, detect_small_targets


def blobs_to_detections(blobs, geotransform, ts=1_700_000_000.0,
                        sensor="eo", domain="maritime") -> list:
    gt = geotransform
    dets = []
    for i, b in enumerate(blobs, 1):
        lat = gt["origin_lat"] + b["row"] * gt["dlat"]
        lon = gt["origin_lon"] + b["col"] * gt["dlon"]
        dets.append(Detection(
            id=f"img-{i}", ts=ts, lat=round(lat, 6), lon=round(lon, 6),
            sensor=sensor, domain=domain, source="EO-SMALLTARGET",
            meta={"peak_snr": b["peak_snr"], "confidence": b["confidence"], "size": b["size"]}))
    return dets


def search_image(image, geotransform, **kw) -> list:
    return blobs_to_detections(detect_small_targets(image, **kw), geotransform)


def search_video(frames, geotransform, **kw) -> list:
    return blobs_to_detections(detect_in_video(frames, **kw), geotransform)
