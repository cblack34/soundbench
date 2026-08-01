"""Manifest loading and expected-grid expansion."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

from strum_lab.models import Manifest


@dataclass(frozen=True)
class ExpectedStroke:
    index: int
    bar: int
    beat: float
    beat_label: str | None
    direction: Literal["down", "up"]
    seconds: float


def load_manifest(path: Path) -> Manifest:
    """Load and strictly validate a UTF-8 YAML manifest."""

    try:
        parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ValueError(f"invalid YAML manifest: {error}") from error
    if not isinstance(parsed, dict):
        raise ValueError("manifest must contain a YAML mapping")
    return Manifest.model_validate(parsed)


def expected_strokes(manifest: Manifest) -> list[ExpectedStroke]:
    """Expand the declared one-based bar/beat grid into absolute times."""

    seconds_per_beat = 60.0 / manifest.performance.tempo_bpm
    seconds_per_bar = manifest.performance.beats_per_bar * seconds_per_beat
    strokes: list[ExpectedStroke] = []
    index = 1
    for bar in range(
        manifest.grid.first_bar,
        manifest.grid.first_bar + manifest.grid.bar_count,
    ):
        bar_start = (bar - 1) * seconds_per_bar
        for beat in manifest.grid.beats:
            strokes.append(
                ExpectedStroke(
                    index=index,
                    bar=bar,
                    beat=beat,
                    beat_label=manifest.grid.beat_labels.get(beat),
                    direction=manifest.grid.direction,
                    seconds=bar_start + (beat - 1.0) * seconds_per_beat,
                )
            )
            index += 1
    return strokes
