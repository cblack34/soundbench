# Strum Lab

Strum Lab measures annotated acoustic-guitar reference recordings. It produces
repeatable evidence about attack timing, dynamics, and frequency balance; it
does not decide what a musical performance should sound like.

The tool is independent of Melos and every other product repository. Other
projects may consume a retained report only through its documented, versioned
file contract and recorded hashes.

## Scope of v0.1

- Read uncompressed PCM WAV without modifying, normalizing, or resampling it.
- Require an explicit channel choice for multi-channel input.
- Align detected attacks to a manifest-declared tempo and beat grid.
- Measure timing, peak and RMS level, attack energy, band-energy ratios, and a
  low-to-high frequency attack-lag proxy.
- Write deterministic JSON, CSV, SVG, and SHA-256 evidence files.

A chord recording cannot establish exact per-string volume because the
strings' fundamentals and harmonics overlap. Band metrics and attack lag are
proxies whose limitations must remain visible in reports.

## Quick start

```bash
uv sync --locked
uv run strum-lab --help
uv run strum-lab analyze ../../data/recording.wav \
  --manifest examples/e-major-quarter-down.yaml \
  --output ../../artifacts/e-major-quarter-down
```

The example assumes that bar 1 is a silent count-in and that quarter-note
downstrokes begin at bar 2. Adjust a local copy of the manifest to match the
actual take; do not commit recordings or recording-specific reports without
explicit approval.

## Verification

Run from this directory:

```bash
uv lock --check
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest
uv run strum-lab --help
```

## Inputs and outputs

The manifest and report schemas are documented in
[`docs/analysis-contract.md`](docs/analysis-contract.md). The repeatable capture
procedure is in [`docs/recording-protocol.md`](docs/recording-protocol.md).

Strum Lab is licensed under Apache License 2.0. Dependency licenses and notices
are recorded in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
