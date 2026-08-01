"""Deterministic evidence-file serialization."""

import csv
import hashlib
import io
import json
from html import escape
from pathlib import Path

import numpy as np

from strum_lab.audio import AudioData
from strum_lab.models import Report


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _require_strokes(report: Report) -> None:
    if not report.strokes:
        raise ValueError("report must contain at least one stroke")


def _csv_bytes(report: Report) -> bytes:
    _require_strokes(report)
    stream = io.StringIO(newline="")
    fields = list(report.strokes[0].model_dump().keys())
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for stroke in report.strokes:
        row = stroke.model_dump()
        writer.writerow(
            {key: "" if value is None else value for key, value in row.items()}
        )
    return stream.getvalue().encode("utf-8")


def _svg_bytes(report: Report, audio: AudioData) -> bytes:
    width = 1200
    height = 420
    left = 60
    right = 20
    top = 50
    bottom = 50
    plot_width = width - left - right
    plot_height = height - top - bottom
    center = top + plot_height / 2
    bucket_count = min(plot_width, audio.samples.size)
    edges = np.linspace(0, audio.samples.size, bucket_count + 1, dtype=np.int64)
    envelope = np.array(
        [
            float(np.max(np.abs(audio.samples[edges[i] : edges[i + 1]])))
            for i in range(bucket_count)
        ]
    )
    points = " ".join(
        f"{left + i * plot_width / max(bucket_count - 1, 1):.2f},"
        f"{center - value * plot_height * 0.45:.2f}"
        for i, value in enumerate(envelope)
    )
    mirrored = " ".join(
        f"{left + i * plot_width / max(bucket_count - 1, 1):.2f},"
        f"{center + value * plot_height * 0.45:.2f}"
        for i, value in reversed(list(enumerate(envelope)))
    )

    markers: list[str] = []
    for stroke in report.strokes:
        expected_x = (
            left + stroke.expected_seconds / audio.duration_seconds * plot_width
        )
        detected_x = (
            left + stroke.detected_seconds / audio.duration_seconds * plot_width
        )
        markers.append(
            f'<line x1="{expected_x:.2f}" y1="{top}" x2="{expected_x:.2f}" '
            f'y2="{top + plot_height}" stroke="#8a8f98" stroke-width="1" />'
        )
        markers.append(
            f'<line x1="{detected_x:.2f}" y1="{top}" x2="{detected_x:.2f}" '
            f'y2="{top + plot_height}" stroke="#d73a49" stroke-width="1" />'
        )

    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n'
        '<rect width="100%" height="100%" fill="#ffffff" />\n'
        f'<text x="{left}" y="28" font-family="sans-serif" font-size="18">'
        f"{escape(report.recording_id)} — expected (gray), detected (red)</text>\n"
        f'<polygon points="{points} {mirrored}" fill="#2f81f7" opacity="0.45" />\n'
        + "\n".join(markers)
        + "\n"
        f'<line x1="{left}" y1="{center:.2f}" x2="{left + plot_width}" '
        f'y2="{center:.2f}" stroke="#24292f" stroke-width="1" />\n'
        f'<text x="{left}" y="{height - 18}" font-family="sans-serif" font-size="12">'
        f"0.0 s</text>\n"
        f'<text x="{left + plot_width - 65}" y="{height - 18}" '
        f'font-family="sans-serif" font-size="12">'
        f"{audio.duration_seconds:.2f} s</text>\n"
        "</svg>\n"
    )
    return svg.encode("utf-8")


def write_outputs(output: Path, report: Report, audio: AudioData) -> dict[str, str]:
    """Write a complete evidence set into a new output directory."""

    _require_strokes(report)
    if output.exists():
        raise FileExistsError(f"output directory already exists: {output}")
    output.mkdir(parents=True, exist_ok=False)

    csv_payload = _csv_bytes(report)
    svg_payload = _svg_bytes(report, audio)
    supporting_hashes = {
        "strokes.csv": _sha256(csv_payload),
        "diagnostic.svg": _sha256(svg_payload),
    }
    final_report = report.model_copy(update={"output_sha256": supporting_hashes})
    report_payload = (
        json.dumps(
            final_report.model_dump(mode="json"),
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    ).encode()

    payloads = {
        "report.json": report_payload,
        "strokes.csv": csv_payload,
        "diagnostic.svg": svg_payload,
    }
    hashes = {name: _sha256(payload) for name, payload in payloads.items()}
    checksum_payload = "".join(
        f"{digest}  {name}\n" for name, digest in sorted(hashes.items())
    ).encode()
    payloads["checksums.sha256"] = checksum_payload
    for name, payload in payloads.items():
        (output / name).write_bytes(payload)
    return {name: _sha256(payload) for name, payload in payloads.items()}
