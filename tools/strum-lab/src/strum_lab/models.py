"""Versioned input and output models for Strum Lab."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    """Reject unknown fields so evidence is never silently reinterpreted."""

    model_config = ConfigDict(extra="forbid")


class AudioConfig(StrictModel):
    channel: Literal["left", "right", "mean"]


class PerformanceConfig(StrictModel):
    tempo_bpm: float = Field(gt=0.0, le=400.0)
    beats_per_bar: int = Field(ge=1, le=16)
    beat_unit: Literal[4]


class GridConfig(StrictModel):
    first_bar: int = Field(ge=1)
    bar_count: int = Field(ge=1, le=10_000)
    beats: list[float] = Field(min_length=1)
    direction: Literal["down", "up"]
    beat_labels: dict[float, str] = Field(default_factory=dict)

    @field_validator("beats")
    @classmethod
    def beats_are_unique_and_ordered(cls, beats: list[float]) -> list[float]:
        if any(beat < 1.0 for beat in beats):
            raise ValueError("beat positions must be at least 1")
        if beats != sorted(set(beats)):
            raise ValueError("beat positions must be unique and increasing")
        return beats

    @model_validator(mode="after")
    def labels_reference_configured_beats(self) -> GridConfig:
        unknown_beats = set(self.beat_labels) - set(self.beats)
        if unknown_beats:
            formatted = ", ".join(str(beat) for beat in sorted(unknown_beats))
            raise ValueError(
                "beat_labels keys must reference configured beats; "
                f"unknown: {formatted}"
            )
        return self


class AnalysisConfig(StrictModel):
    search_radius_ms: float = Field(default=300.0, gt=0.0, le=499.0)
    frame_length: int = Field(default=1024, ge=128, le=8192)
    hop_length: int = Field(default=128, ge=16, le=2048)
    attack_window_ms: float = Field(default=100.0, gt=10.0, le=500.0)
    low_band_hz: tuple[float, float] = (80.0, 300.0)
    mid_band_hz: tuple[float, float] = (300.0, 1200.0)
    high_band_hz: tuple[float, float] = (1200.0, 6000.0)

    @field_validator("low_band_hz", "mid_band_hz", "high_band_hz")
    @classmethod
    def band_is_increasing(cls, band: tuple[float, float]) -> tuple[float, float]:
        if band[0] < 0.0 or band[0] >= band[1]:
            raise ValueError(
                "frequency bands must contain increasing nonnegative values"
            )
        return band

    @model_validator(mode="after")
    def frames_are_compatible(self) -> AnalysisConfig:
        if self.hop_length > self.frame_length:
            raise ValueError("hop_length must not exceed frame_length")
        if self.low_band_hz[1] > self.mid_band_hz[0]:
            raise ValueError("low and mid frequency bands must not overlap")
        if self.mid_band_hz[1] > self.high_band_hz[0]:
            raise ValueError("mid and high frequency bands must not overlap")
        return self


class Manifest(StrictModel):
    schema_version: Literal[1]
    recording_id: str = Field(min_length=1, max_length=200)
    notes: str | None = None
    audio: AudioConfig
    performance: PerformanceConfig
    grid: GridConfig
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)

    @model_validator(mode="after")
    def beats_fit_meter(self) -> Manifest:
        if any(beat > self.performance.beats_per_bar for beat in self.grid.beats):
            raise ValueError("grid beat positions must fit within beats_per_bar")
        return self


class AudioSummary(StrictModel):
    path: str
    sha256: str
    sample_rate: int
    source_channels: int
    selected_channel: Literal["left", "right", "mean"]
    bits_per_sample: int
    frame_count: int
    duration_seconds: float
    clipped_sample_count: int
    clipped_sample_fraction: float


class StrokeMeasurement(StrictModel):
    index: int
    bar: int
    beat: float
    beat_label: str | None
    direction: Literal["down", "up"]
    expected_seconds: float
    detected_seconds: float
    timing_error_ms: float
    onset_confidence: float
    peak_dbfs: float
    rms_dbfs: float
    attack_energy: float
    low_energy_ratio: float
    mid_energy_ratio: float
    high_energy_ratio: float
    high_minus_low_onset_ms: float | None


class BeatAggregate(StrictModel):
    beat: float
    beat_label: str | None
    direction: Literal["down", "up"]
    stroke_count: int
    median_timing_error_ms: float
    timing_mad_ms: float
    median_peak_dbfs: float
    median_rms_dbfs: float
    rms_mad_db: float
    median_low_energy_ratio: float
    median_mid_energy_ratio: float
    median_high_energy_ratio: float
    median_high_minus_low_onset_ms: float | None


class Report(StrictModel):
    schema_version: Literal[1] = 1
    tool_name: Literal["strum-lab"] = "strum-lab"
    tool_version: str
    recording_id: str
    notes: str | None
    audio: AudioSummary
    manifest: dict[str, object]
    noise_floor_dbfs: float
    observations: list[str]
    strokes: list[StrokeMeasurement]
    beat_aggregates: list[BeatAggregate]
    output_sha256: dict[str, str] = Field(default_factory=dict)
