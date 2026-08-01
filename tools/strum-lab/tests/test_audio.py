from pathlib import Path

import numpy as np
import pytest

from strum_lab.audio import read_pcm_wav
from tests.helpers import write_pcm24


def test_reads_stereo_pcm24_with_explicit_mean(tmp_path: Path) -> None:
    path = tmp_path / "stereo.wav"
    samples = np.array([[0.5, 0.25], [-0.5, -0.25], [0.0, 0.0]])
    write_pcm24(path, samples)

    audio = read_pcm_wav(path, "mean")

    assert audio.sample_rate == 16_000
    assert audio.source_channels == 2
    assert audio.bits_per_sample == 24
    assert audio.samples == pytest.approx([0.375, -0.375, 0.0], abs=2e-7)
    assert len(audio.sha256) == 64


def test_rejects_right_channel_for_mono(tmp_path: Path) -> None:
    path = tmp_path / "mono.wav"
    write_pcm24(path, np.zeros(160, dtype=np.float64))

    with pytest.raises(ValueError, match="right channel requested for mono"):
        read_pcm_wav(path, "right")


def test_rejects_non_wav(tmp_path: Path) -> None:
    path = tmp_path / "not-a-wave.wav"
    path.write_text("not audio", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid or unsupported WAV"):
        read_pcm_wav(path, "mean")


def test_rejects_truncated_pcm_with_consistent_error(tmp_path: Path) -> None:
    path = tmp_path / "truncated.wav"
    write_pcm24(path, np.zeros((160, 2), dtype=np.float64))
    path.write_bytes(path.read_bytes()[:-1])

    with pytest.raises(ValueError, match="invalid or unsupported WAV"):
        read_pcm_wav(path, "mean")
