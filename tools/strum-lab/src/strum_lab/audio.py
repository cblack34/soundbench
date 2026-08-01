"""Strict, non-mutating PCM WAV input."""

import hashlib
import io
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class AudioData:
    samples: NDArray[np.float64]
    sample_rate: int
    source_channels: int
    selected_channel: Literal["left", "right", "mean"]
    bits_per_sample: int
    frame_count: int
    duration_seconds: float
    sha256: str
    clipped_sample_count: int
    clipped_sample_fraction: float


def _decode_pcm(raw: bytes, sample_width: int) -> NDArray[np.float64]:
    if sample_width == 1:
        values = np.frombuffer(raw, dtype=np.uint8).astype(np.float64)
        return (values - 128.0) / 128.0
    if sample_width == 2:
        values = np.frombuffer(raw, dtype="<i2").astype(np.float64)
        return values / 32768.0
    if sample_width == 3:
        octets = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        values = (
            octets[:, 0].astype(np.int32)
            | (octets[:, 1].astype(np.int32) << 8)
            | (octets[:, 2].astype(np.int32) << 16)
        )
        values = np.where(values & 0x800000, values - 0x1000000, values)
        return values.astype(np.float64) / 8388608.0
    if sample_width == 4:
        values = np.frombuffer(raw, dtype="<i4").astype(np.float64)
        return values / 2147483648.0
    raise ValueError(f"unsupported PCM sample width: {sample_width * 8} bits")


def read_pcm_wav(
    path: Path,
    channel: Literal["left", "right", "mean"],
) -> AudioData:
    """Read 8/16/24/32-bit PCM WAV and explicitly select a channel."""

    payload = path.read_bytes()
    try:
        with wave.open(io.BytesIO(payload), "rb") as source:
            if source.getcomptype() != "NONE":
                raise ValueError("only uncompressed PCM WAV is supported")
            channels = source.getnchannels()
            sample_width = source.getsampwidth()
            sample_rate = source.getframerate()
            frame_count = source.getnframes()
            raw = source.readframes(frame_count)
    except (wave.Error, EOFError) as error:
        raise ValueError(f"invalid or unsupported WAV: {error}") from error

    if channels not in {1, 2}:
        raise ValueError(
            f"only mono or stereo WAV is supported; received {channels} channels"
        )
    if frame_count <= 0 or sample_rate <= 0:
        raise ValueError("WAV must contain audio frames at a positive sample rate")

    try:
        decoded = _decode_pcm(raw, sample_width).reshape(frame_count, channels)
    except ValueError as error:
        raise ValueError(f"invalid or unsupported WAV: {error}") from error
    if channels == 1:
        if channel == "right":
            raise ValueError("right channel requested for mono input")
        selected = decoded[:, 0]
    elif channel == "left":
        selected = decoded[:, 0]
    elif channel == "right":
        selected = decoded[:, 1]
    else:
        selected = decoded.mean(axis=1)

    maximum_code = (2 ** (sample_width * 8 - 1) - 1) / 2 ** (sample_width * 8 - 1)
    clipped = int(np.count_nonzero(np.abs(selected) >= maximum_code))
    digest = hashlib.sha256(payload).hexdigest()
    return AudioData(
        samples=np.ascontiguousarray(selected, dtype=np.float64),
        sample_rate=sample_rate,
        source_channels=channels,
        selected_channel=channel,
        bits_per_sample=sample_width * 8,
        frame_count=frame_count,
        duration_seconds=frame_count / sample_rate,
        sha256=digest,
        clipped_sample_count=clipped,
        clipped_sample_fraction=clipped / frame_count,
    )
