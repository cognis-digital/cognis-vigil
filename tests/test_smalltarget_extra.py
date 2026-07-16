"""Small-target CFAR internals: SNR map, clustering, Pfa mapping edges."""

import random

from scryer.smalltarget import (
    _cluster,
    detect_small_targets,
    pfa_to_k,
    snr_map,
    stack_frames,
    temporal_residual,
)


def _noisy(h, w, seed=7, mean=0.2, sd=0.03):
    rng = random.Random(seed)
    return [[max(0.0, rng.gauss(mean, sd)) for _ in range(w)] for _ in range(h)]


def test_empty_image_returns_no_detections():
    assert detect_small_targets([]) == []
    assert detect_small_targets([[]]) == []


def test_snr_map_dimensions_match_input():
    img = [[0.2] * 12 for _ in range(12)]
    s = snr_map(img)
    assert len(s) == 12 and len(s[0]) == 12


def test_snr_peaks_at_a_bright_pixel():
    # CFAR needs clutter (non-zero local sigma) for a defined contrast ratio
    img = _noisy(15, 15)
    img[7][7] += 5.0
    s = snr_map(img)
    assert s[7][7] == max(max(row) for row in s)
    assert s[7][7] > 5.0  # strongly above background sigma


def test_pfa_to_k_clamps_extremes():
    # absurd inputs are clamped into a sane sigma band, not NaN/inf
    lo = pfa_to_k(1e-20)   # clamped to 1e-12
    hi = pfa_to_k(0.9)     # clamped to 0.5 -> ~0 sigma
    assert 6.5 < lo < 7.5
    assert hi == 0.0


def test_pfa_to_k_monotonic_decreasing_in_pfa():
    ks = [pfa_to_k(p) for p in (1e-2, 1e-3, 1e-4, 1e-5, 1e-6)]
    assert ks == sorted(ks)  # stricter Pfa -> higher sigma


def test_cluster_rejects_oversized_blobs():
    # a solid 4x4 hot block (16 px) exceeds max_size=8 -> rejected as clutter
    snr = [[0.0] * 8 for _ in range(8)]
    for r in range(2, 6):
        for c in range(2, 6):
            snr[r][c] = 10.0
    assert _cluster(snr, k=5.0, max_size=8) == []
    # a 1-px hit survives
    tiny = [[0.0] * 8 for _ in range(8)]
    tiny[4][4] = 10.0
    assert len(_cluster(tiny, k=5.0, max_size=8)) == 1


def test_temporal_residual_flags_changing_pixel():
    frames = [[[0.2, 0.2], [0.2, 0.2]] for _ in range(4)]
    frames[2][0][1] = 1.0  # one pixel spikes in one frame
    resid = temporal_residual(frames)
    assert resid[0][1] > resid[0][0]


def test_stack_frames_averages():
    frames = [[[2.0, 4.0]], [[4.0, 8.0]]]
    assert stack_frames(frames) == [[3.0, 6.0]]


def test_pfa_argument_overrides_k_in_detect():
    img = _noisy(20, 20)
    img[10][10] += 3.0
    # a very strict Pfa should still find a strong point target
    blobs = detect_small_targets(img, pfa=1e-4)
    assert any(abs(b["row"] - 10) <= 1 and abs(b["col"] - 10) <= 1 for b in blobs)
