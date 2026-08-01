from pathlib import Path

import pytest

from strum_lab.analysis import analyze
from strum_lab.audio import read_pcm_wav
from strum_lab.manifest import load_manifest
from strum_lab.output import write_outputs
from tests.helpers import manifest_text, synthetic_strums, write_pcm24


def _analyze_synthetic(tmp_path: Path):
    audio_path = tmp_path / "strums.wav"
    manifest_path = tmp_path / "manifest.yaml"
    samples, expected = synthetic_strums()
    write_pcm24(audio_path, samples)
    manifest_path.write_text(manifest_text(), encoding="utf-8")
    manifest = load_manifest(manifest_path)
    audio = read_pcm_wav(audio_path, manifest.audio.channel)
    return analyze(str(audio_path), audio, manifest), audio, expected


def test_finds_synthetic_onsets_and_dynamic_contrast(tmp_path: Path) -> None:
    report, _, expected = _analyze_synthetic(tmp_path)

    assert len(report.strokes) == 8
    errors = [
        abs(stroke.detected_seconds - target)
        for stroke, target in zip(report.strokes, expected, strict=True)
    ]
    assert max(errors) <= 0.04
    strong = [stroke.rms_dbfs for stroke in report.strokes if stroke.beat in {1, 3}]
    relaxed = [stroke.rms_dbfs for stroke in report.strokes if stroke.beat in {2, 4}]
    assert sum(strong) / len(strong) > sum(relaxed) / len(relaxed) + 5.0
    assert all(stroke.high_minus_low_onset_ms is not None for stroke in report.strokes)
    assert len(report.beat_aggregates) == 4
    assert report.beat_aggregates[0].stroke_count == 2
    assert (
        report.beat_aggregates[0].median_rms_dbfs
        > report.beat_aggregates[1].median_rms_dbfs + 5.0
    )


def test_output_is_deterministic_and_refuses_overwrite(tmp_path: Path) -> None:
    report, audio, _ = _analyze_synthetic(tmp_path)
    first = tmp_path / "first"
    second = tmp_path / "second"

    first_hashes = write_outputs(first, report, audio)
    second_hashes = write_outputs(second, report, audio)

    assert first_hashes == second_hashes
    for name in first_hashes:
        assert (first / name).read_bytes() == (second / name).read_bytes()
    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        write_outputs(first, report, audio)


def test_manifest_cannot_extend_past_audio(tmp_path: Path) -> None:
    report, audio, _ = _analyze_synthetic(tmp_path)
    manifest_data = report.manifest
    manifest_data["grid"]["bar_count"] = 3  # type: ignore[index]
    manifest_path = tmp_path / "too-long.yaml"
    import yaml

    manifest_path.write_text(yaml.safe_dump(manifest_data), encoding="utf-8")
    with pytest.raises(ValueError, match="manifest requires audio"):
        analyze(report.audio.path, audio, load_manifest(manifest_path))
