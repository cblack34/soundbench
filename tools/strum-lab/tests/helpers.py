"""Generated PCM fixtures; no recorded audio is committed."""

import wave
from pathlib import Path

import numpy as np
from numpy.typing import NDArray


def write_pcm24(path: Path, samples: NDArray[np.float64]) -> None:
    """Write mono or frame-by-channel float samples as little-endian PCM24."""

    framed = samples[:, None] if samples.ndim == 1 else samples
    integers = np.rint(np.clip(framed, -1.0, 1.0) * 8388607.0).astype(np.int32)
    octets = np.empty((*integers.shape, 3), dtype=np.uint8)
    octets[..., 0] = integers & 0xFF
    octets[..., 1] = (integers >> 8) & 0xFF
    octets[..., 2] = (integers >> 16) & 0xFF
    with wave.open(str(path), "wb") as target:
        target.setnchannels(framed.shape[1])
        target.setsampwidth(3)
        target.setframerate(16_000)
        target.writeframes(octets.tobytes())


def synthetic_strums() -> tuple[NDArray[np.float64], list[float]]:
    sample_rate = 16_000
    duration = 12.0
    times = list(np.arange(4.0, 12.0, 1.0))
    samples = np.zeros(int(duration * sample_rate), dtype=np.float64)
    for index, onset in enumerate(times):
        amplitude = 0.72 if index % 4 in {0, 2} else 0.34
        for delay, frequency, weight, decay in (
            (0.000, 110.0, 1.00, 9.0),
            (0.006, 500.0, 0.55, 13.0),
            (0.014, 2500.0, 0.24, 18.0),
        ):
            start = int((onset + delay) * sample_rate)
            length = min(int(0.35 * sample_rate), samples.size - start)
            local_time = np.arange(length) / sample_rate
            envelope = np.exp(-decay * local_time)
            samples[start : start + length] += (
                amplitude
                * weight
                * envelope
                * np.sin(2.0 * np.pi * frequency * local_time)
            )
    samples *= 0.78 / np.max(np.abs(samples))
    stereo = np.column_stack((samples, samples * 0.92))
    return stereo, times


def manifest_text() -> str:
    return """\
schema_version: 1
recording_id: synthetic-quarter-down
audio:
  channel: mean
performance:
  tempo_bpm: 60.0
  beats_per_bar: 4
  beat_unit: 4
grid:
  first_bar: 2
  bar_count: 2
  beats: [1, 2, 3, 4]
  direction: down
  beat_labels:
    1: strong
    2: relaxed
    3: strong
    4: relaxed
analysis:
  search_radius_ms: 250.0
  frame_length: 512
  hop_length: 64
  attack_window_ms: 100.0
  low_band_hz: [80.0, 300.0]
  mid_band_hz: [300.0, 1200.0]
  high_band_hz: [1200.0, 6000.0]
"""
