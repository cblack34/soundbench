"""Deterministic onset, dynamics, and spectral-proxy measurements."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from strum_lab import __version__
from strum_lab.audio import AudioData
from strum_lab.manifest import ExpectedStroke, expected_strokes
from strum_lab.models import (
    AudioSummary,
    BeatAggregate,
    Manifest,
    Report,
    StrokeMeasurement,
)

_EPSILON = 1e-12
_SPECTRAL_CHUNK_FRAMES = 512


@dataclass(frozen=True)
class SpectralFrames:
    times: NDArray[np.float64]
    onset_envelope: NDArray[np.float64]
    low_power: NDArray[np.float64]
    mid_power: NDArray[np.float64]
    high_power: NDArray[np.float64]


def _dbfs(value: float) -> float:
    return float(20.0 * np.log10(max(value, _EPSILON)))


def _spectral_frames(audio: AudioData, manifest: Manifest) -> SpectralFrames:
    frame_length = manifest.analysis.frame_length
    hop_length = manifest.analysis.hop_length
    if audio.samples.size < frame_length:
        raise ValueError("audio is shorter than one analysis frame")

    views = np.lib.stride_tricks.sliding_window_view(audio.samples, frame_length)
    frames = views[::hop_length]
    window = np.hanning(frame_length)
    frequencies = np.fft.rfftfreq(frame_length, 1.0 / audio.sample_rate)
    masks = (
        _band_mask(frequencies, manifest.analysis.low_band_hz),
        _band_mask(frequencies, manifest.analysis.mid_band_hz),
        _band_mask(frequencies, manifest.analysis.high_band_hz),
    )
    for name, mask in zip(("low", "mid", "high"), masks, strict=True):
        if not np.any(mask):
            raise ValueError(
                f"{name} frequency band contains no FFT bins; increase frame_length"
            )

    frame_count = frames.shape[0]
    onset = np.zeros(frame_count, dtype=np.float64)
    band_power = [np.zeros(frame_count, dtype=np.float64) for _ in masks]
    previous_log_magnitude: NDArray[np.float64] | None = None
    for start in range(0, frame_count, _SPECTRAL_CHUNK_FRAMES):
        end = min(start + _SPECTRAL_CHUNK_FRAMES, frame_count)
        magnitude = np.abs(np.fft.rfft(frames[start:end] * window, axis=1))
        log_magnitude = np.log1p(magnitude)
        if previous_log_magnitude is not None:
            onset[start] = float(
                np.maximum(log_magnitude[0] - previous_log_magnitude, 0.0).sum()
            )
        if end - start > 1:
            onset[start + 1 : end] = np.maximum(
                np.diff(log_magnitude, axis=0), 0.0
            ).sum(axis=1)
        previous_log_magnitude = log_magnitude[-1]
        power = np.square(magnitude)
        for target, mask in zip(band_power, masks, strict=True):
            target[start:end] = power[:, mask].sum(axis=1)

    times = (
        np.arange(frame_count, dtype=np.float64) * hop_length + frame_length / 2
    ) / audio.sample_rate
    return SpectralFrames(
        times=times,
        onset_envelope=onset,
        low_power=band_power[0],
        mid_power=band_power[1],
        high_power=band_power[2],
    )


def _noise_floor(audio: AudioData, first_expected: float) -> float:
    silence_end = min(max(first_expected - 0.25, 0.0), 2.0)
    sample_count = int(silence_end * audio.sample_rate)
    if sample_count < int(0.05 * audio.sample_rate):
        return _dbfs(float(np.sqrt(np.mean(np.square(audio.samples)))))
    window = max(1, int(0.01 * audio.sample_rate))
    silence = audio.samples[:sample_count]
    usable = silence[: silence.size - silence.size % window]
    rms = np.sqrt(np.mean(np.square(usable.reshape(-1, window)), axis=1))
    return _dbfs(float(np.median(rms)))


def _band_mask(
    frequencies: NDArray[np.float64], band: tuple[float, float]
) -> NDArray[np.bool_]:
    return (frequencies >= band[0]) & (frequencies < band[1])


def _band_onset_time(
    frames: SpectralFrames,
    band_power: NDArray[np.float64],
    detected: float,
    attack_seconds: float,
) -> float | None:
    region = (frames.times >= detected - 0.03) & (
        frames.times <= detected + attack_seconds
    )
    if not np.any(region):
        return None
    times = frames.times[region]
    energy = band_power[region]
    if energy.size == 0 or float(np.max(energy)) <= _EPSILON:
        return None
    baseline_count = max(1, min(3, energy.size // 4))
    baseline = float(np.median(energy[:baseline_count]))
    threshold = baseline + 0.2 * (float(np.max(energy)) - baseline)
    crossings = np.flatnonzero(energy >= threshold)
    return None if crossings.size == 0 else float(times[crossings[0]])


def _measure_stroke(
    expected: ExpectedStroke,
    audio: AudioData,
    manifest: Manifest,
    frames: SpectralFrames,
) -> StrokeMeasurement:
    radius = manifest.analysis.search_radius_ms / 1000.0
    search = (frames.times >= expected.seconds - radius) & (
        frames.times <= expected.seconds + radius
    )
    candidates = np.flatnonzero(search)
    if candidates.size == 0:
        raise ValueError(
            f"expected stroke {expected.index} at {expected.seconds:.3f}s "
            "has no searchable audio"
        )
    local_envelope = frames.onset_envelope[candidates]
    local_index = int(np.argmax(local_envelope))
    peak_frame = int(candidates[local_index])
    detected = float(frames.times[peak_frame])
    local_median = float(np.median(local_envelope))
    confidence = float(local_envelope[local_index] / max(local_median, _EPSILON))

    attack_seconds = manifest.analysis.attack_window_ms / 1000.0
    sample_start = max(0, int((detected - 0.01) * audio.sample_rate))
    sample_end = min(
        audio.frame_count, int((detected + attack_seconds) * audio.sample_rate)
    )
    attack = audio.samples[sample_start:sample_end]
    if attack.size == 0:
        raise ValueError(f"stroke {expected.index} has an empty attack window")
    peak = float(np.max(np.abs(attack)))
    rms = float(np.sqrt(np.mean(np.square(attack))))

    spectral_region = (frames.times >= detected) & (
        frames.times <= detected + attack_seconds
    )
    low = float(frames.low_power[spectral_region].sum())
    mid = float(frames.mid_power[spectral_region].sum())
    high = float(frames.high_power[spectral_region].sum())
    total = max(low + mid + high, _EPSILON)

    low_onset = _band_onset_time(frames, frames.low_power, detected, attack_seconds)
    high_onset = _band_onset_time(frames, frames.high_power, detected, attack_seconds)
    lag = None
    if low_onset is not None and high_onset is not None:
        lag = (high_onset - low_onset) * 1000.0

    return StrokeMeasurement(
        index=expected.index,
        bar=expected.bar,
        beat=expected.beat,
        beat_label=expected.beat_label,
        direction=expected.direction,
        expected_seconds=expected.seconds,
        detected_seconds=detected,
        timing_error_ms=(detected - expected.seconds) * 1000.0,
        onset_confidence=confidence,
        peak_dbfs=_dbfs(peak),
        rms_dbfs=_dbfs(rms),
        attack_energy=float(np.mean(np.square(attack)) * attack.size),
        low_energy_ratio=low / total,
        mid_energy_ratio=mid / total,
        high_energy_ratio=high / total,
        high_minus_low_onset_ms=lag,
    )


def _median(values: list[float]) -> float:
    return float(np.median(np.asarray(values, dtype=np.float64)))


def _mad(values: list[float]) -> float:
    median = _median(values)
    return _median([abs(value - median) for value in values])


def _beat_aggregates(strokes: list[StrokeMeasurement]) -> list[BeatAggregate]:
    aggregates: list[BeatAggregate] = []
    for beat in sorted({stroke.beat for stroke in strokes}):
        group = [stroke for stroke in strokes if stroke.beat == beat]
        lags = [
            stroke.high_minus_low_onset_ms
            for stroke in group
            if stroke.high_minus_low_onset_ms is not None
        ]
        aggregates.append(
            BeatAggregate(
                beat=beat,
                beat_label=group[0].beat_label,
                direction=group[0].direction,
                stroke_count=len(group),
                median_timing_error_ms=_median(
                    [stroke.timing_error_ms for stroke in group]
                ),
                timing_mad_ms=_mad([stroke.timing_error_ms for stroke in group]),
                median_peak_dbfs=_median([stroke.peak_dbfs for stroke in group]),
                median_rms_dbfs=_median([stroke.rms_dbfs for stroke in group]),
                rms_mad_db=_mad([stroke.rms_dbfs for stroke in group]),
                median_low_energy_ratio=_median(
                    [stroke.low_energy_ratio for stroke in group]
                ),
                median_mid_energy_ratio=_median(
                    [stroke.mid_energy_ratio for stroke in group]
                ),
                median_high_energy_ratio=_median(
                    [stroke.high_energy_ratio for stroke in group]
                ),
                median_high_minus_low_onset_ms=None if not lags else _median(lags),
            )
        )
    return aggregates


def analyze(path: str, audio: AudioData, manifest: Manifest) -> Report:
    """Analyze all declared strokes and return a validated report model."""

    expected = expected_strokes(manifest)
    if not expected:
        raise ValueError("manifest expands to no expected strokes")
    last_measurement_end = (
        expected[-1].seconds
        + manifest.analysis.search_radius_ms / 1000.0
        + manifest.analysis.attack_window_ms / 1000.0
        + manifest.analysis.frame_length / (2.0 * audio.sample_rate)
    )
    if last_measurement_end > audio.duration_seconds:
        raise ValueError(
            "manifest requires audio through "
            f"{last_measurement_end:.3f}s for the complete final measurement, "
            f"but WAV duration is {audio.duration_seconds:.3f}s"
        )
    nyquist = audio.sample_rate / 2.0
    configured_bands = (
        ("low", manifest.analysis.low_band_hz),
        ("mid", manifest.analysis.mid_band_hz),
        ("high", manifest.analysis.high_band_hz),
    )
    for name, band in configured_bands:
        if band[1] > nyquist:
            raise ValueError(
                f"{name} band ends at {band[1]:.1f} Hz, "
                f"above the {nyquist:.1f} Hz Nyquist frequency"
            )

    frames = _spectral_frames(audio, manifest)
    strokes = [_measure_stroke(stroke, audio, manifest, frames) for stroke in expected]
    observations: list[str] = [
        "Frequency-band ratios and attack lag are proxies, not per-string levels."
    ]
    if audio.clipped_sample_count:
        observations.append(
            f"Input contains {audio.clipped_sample_count} clipped "
            "selected-channel samples."
        )
    low_confidence = sum(stroke.onset_confidence < 2.0 for stroke in strokes)
    if low_confidence:
        observations.append(
            f"{low_confidence} stroke(s) have onset confidence below 2.0; "
            "inspect the overlay."
        )

    return Report(
        tool_version=__version__,
        recording_id=manifest.recording_id,
        notes=manifest.notes,
        audio=AudioSummary(
            path=path,
            sha256=audio.sha256,
            sample_rate=audio.sample_rate,
            source_channels=audio.source_channels,
            selected_channel=audio.selected_channel,
            bits_per_sample=audio.bits_per_sample,
            frame_count=audio.frame_count,
            duration_seconds=audio.duration_seconds,
            clipped_sample_count=audio.clipped_sample_count,
            clipped_sample_fraction=audio.clipped_sample_fraction,
        ),
        manifest=manifest.model_dump(mode="json"),
        noise_floor_dbfs=_noise_floor(audio, expected[0].seconds),
        observations=observations,
        strokes=strokes,
        beat_aggregates=_beat_aggregates(strokes),
    )
