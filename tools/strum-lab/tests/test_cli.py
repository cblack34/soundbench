from pathlib import Path

from strum_lab.cli import main
from tests.helpers import manifest_text, synthetic_strums, write_pcm24


def test_cli_writes_evidence_set(tmp_path: Path, capsys) -> None:
    audio_path = tmp_path / "strums.wav"
    manifest_path = tmp_path / "manifest.yaml"
    output = tmp_path / "report"
    samples, _ = synthetic_strums()
    write_pcm24(audio_path, samples)
    manifest_path.write_text(manifest_text(), encoding="utf-8")

    result = main(
        [
            "analyze",
            str(audio_path),
            "--manifest",
            str(manifest_path),
            "--output",
            str(output),
        ]
    )

    assert result == 0
    assert "Analyzed 8 strokes" in capsys.readouterr().out
    assert {path.name for path in output.iterdir()} == {
        "report.json",
        "strokes.csv",
        "diagnostic.svg",
        "checksums.sha256",
    }


def test_cli_returns_actionable_validation_error(tmp_path: Path, capsys) -> None:
    manifest_path = tmp_path / "manifest.yaml"
    manifest_path.write_text("schema_version: 1\n", encoding="utf-8")

    result = main(
        [
            "analyze",
            str(tmp_path / "missing.wav"),
            "--manifest",
            str(manifest_path),
            "--output",
            str(tmp_path / "output"),
        ]
    )

    assert result == 2
    assert "strum-lab: error:" in capsys.readouterr().err
