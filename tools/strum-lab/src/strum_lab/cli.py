"""Command-line interface for Strum Lab."""

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from strum_lab import __version__
from strum_lab.analysis import analyze
from strum_lab.audio import read_pcm_wav
from strum_lab.manifest import load_manifest
from strum_lab.output import write_outputs


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="strum-lab",
        description="Analyze annotated guitar-strum PCM WAV references.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    analyze_parser = commands.add_parser(
        "analyze", help="measure expected strokes and write an evidence report"
    )
    analyze_parser.add_argument("audio", type=Path, help="source PCM WAV")
    analyze_parser.add_argument(
        "--manifest", required=True, type=Path, help="versioned YAML manifest"
    )
    analyze_parser.add_argument(
        "--output", required=True, type=Path, help="new evidence output directory"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process status."""

    args = _parser().parse_args(argv)
    if args.command != "analyze":
        _parser().error(f"unsupported command: {args.command}")

    try:
        manifest = load_manifest(args.manifest)
        audio = read_pcm_wav(args.audio, manifest.audio.channel)
        report = analyze(str(args.audio), audio, manifest)
        hashes = write_outputs(args.output, report, audio)
    except (OSError, ValueError, ValidationError) as error:
        print(f"strum-lab: error: {error}", file=sys.stderr)
        return 2

    print(f"Analyzed {len(report.strokes)} strokes into {args.output}")
    for name, digest in sorted(hashes.items()):
        print(f"{digest}  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
