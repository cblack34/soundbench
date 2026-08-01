from pathlib import Path

import pytest
from pydantic import ValidationError

from strum_lab.manifest import expected_strokes, load_manifest
from tests.helpers import manifest_text


def test_expands_one_based_bars_and_beats(tmp_path: Path) -> None:
    path = tmp_path / "manifest.yaml"
    path.write_text(manifest_text(), encoding="utf-8")

    strokes = expected_strokes(load_manifest(path))

    assert [stroke.seconds for stroke in strokes] == list(range(4, 12))
    assert strokes[0].bar == 2
    assert strokes[0].beat == 1
    assert strokes[-1].bar == 3
    assert strokes[-1].beat == 4


def test_rejects_unknown_manifest_fields(tmp_path: Path) -> None:
    path = tmp_path / "manifest.yaml"
    path.write_text(manifest_text() + "surprise: true\n", encoding="utf-8")

    with pytest.raises(ValidationError, match="surprise"):
        load_manifest(path)


def test_rejects_beats_outside_meter(tmp_path: Path) -> None:
    path = tmp_path / "manifest.yaml"
    manifest = manifest_text().replace("[1, 2, 3, 4]", "[1, 2, 3, 5]")
    manifest = manifest.replace("    4: relaxed", "    5: relaxed")
    path.write_text(manifest, encoding="utf-8")

    with pytest.raises(ValidationError, match="fit within beats_per_bar"):
        load_manifest(path)


def test_rejects_labels_for_unconfigured_beats(tmp_path: Path) -> None:
    path = tmp_path / "manifest.yaml"
    path.write_text(
        manifest_text().replace("    4: relaxed", "    5: relaxed"), encoding="utf-8"
    )

    with pytest.raises(ValidationError, match=r"unknown: 5\.0"):
        load_manifest(path)


def test_wraps_yaml_syntax_errors(tmp_path: Path) -> None:
    path = tmp_path / "manifest.yaml"
    path.write_text("schema_version: [1\n", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid YAML manifest"):
        load_manifest(path)


def test_wraps_non_utf8_manifest_errors(tmp_path: Path) -> None:
    path = tmp_path / "manifest.yaml"
    path.write_bytes(b"schema_version: \xff\n")

    with pytest.raises(ValueError, match="manifest must be valid UTF-8"):
        load_manifest(path)


def test_rejects_unsupported_beat_unit(tmp_path: Path) -> None:
    path = tmp_path / "manifest.yaml"
    path.write_text(
        manifest_text().replace("beat_unit: 4", "beat_unit: 8"), encoding="utf-8"
    )

    with pytest.raises(ValidationError, match="beat_unit"):
        load_manifest(path)
