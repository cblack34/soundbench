# SoundBench

Audio analysis and calibration tools for musical-performance research.

SoundBench contains independent, reproducible command-line tools. Each tool
owns its Python version, uv project, lockfile, dependencies, tests, license, and
CI gate. There is intentionally no root Python project or shared tool
environment.

## Repository layout

```text
soundbench/
├── tools/       # independent uv tool projects
├── data/        # local-only recordings and derived inputs
├── artifacts/   # local-only generated reports and media
└── docs/        # shared recording and evidence conventions
```

Only the guidance files under `data/` and `artifacts/` are tracked. Their
contents are ignored by default. A recording or output artifact is published
only after an explicit license, privacy, provenance, and repository-size
decision.

## Tools

- [`Strum Lab`](tools/strum-lab/README.md) analyzes annotated acoustic-guitar
  PCM WAV references and produces deterministic timing, dynamics, and spectral
  evidence.

Run a tool through its independent project:

```bash
uv run --project tools/strum-lab strum-lab --help
```

## Contributing

Read [`AGENTS.md`](AGENTS.md) before planning or implementing a change. License
decisions follow [`LICENSE_POLICY.md`](LICENSE_POLICY.md).
