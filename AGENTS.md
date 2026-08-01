# AGENTS.md — SoundBench

Instructions for AI agents that plan and build SoundBench. This is the source of
truth for how work is performed in this repository.

## Purpose

SoundBench is a public collection of independent research tools for analyzing
and calibrating audio and musical-performance behavior. Tools may inform other
projects through versioned reports and measured evidence, but those projects do
not import SoundBench code or dependencies.

The repository stores tool source, tests, documentation, and reproducible
dependency locks. Raw recordings, derived audio, and generated reports remain
local unless a human explicitly approves a specific artifact for publication.

## Reading order

Before changing a tool:

1. Read this file.
2. Read [`README.md`](README.md) and
   [`LICENSE_POLICY.md`](LICENSE_POLICY.md).
3. Read the selected tool's `README.md`, `pyproject.toml`, `LICENSE`, and
   `THIRD_PARTY_NOTICES.md`.
4. Inspect its production code, tests, lockfile, CI workflow, Git state, and
   relevant live issues.
5. Treat generated reports and historical issue discussion as evidence, not as
   authority over current human instructions or recorded repository policy.

Nested `AGENTS.md` files may add genuinely tool-specific rules. Do not create
one merely to repeat this file.

## Repository boundaries

- Each directory under `tools/` is an independent uv project with its own
  `pyproject.toml`, `.python-version`, `uv.lock`, `.venv`, source, tests,
  documentation, license, notices, and CI gate.
- The repository root and `tools/` directory are not uv projects or uv
  workspaces. Do not add a root `pyproject.toml`, root `uv.lock`, or shared
  virtual environment.
- Start a tool as one packaged application. Make that tool an internal uv
  workspace only when it actually contains multiple interconnected packages.
- Do not import another SoundBench tool through an undeclared path or shared
  environment. Propose an explicit shared-package boundary if reuse becomes
  real.
- Do not add Melos or another product repository as a package, path, workspace,
  submodule, or source dependency. Exchange data through documented,
  versioned files with provenance and hashes.
- Do not add speculative tools, adapters, or dependencies.

## Git checkpointing

For every task that changes files:

- Inspect Git status, the current branch, and its upstream before editing.
- Create or continue a task-specific branch before the first edit. Never begin
  implementation on `main`.
- Preserve unrelated human changes and commit only task-owned files.
- Commit after each coherent, verified checkpoint and before risky work.
- Keep pushing and PR creation separate; publish only when requested or when a
  repository instruction explicitly authorizes it.
- Never force-push without approval.
- Never merge to `main`; only the human performs that merge.
- Before finishing, report the branch, commit hashes, verification, published
  state, and intentionally uncommitted files.

## Tool project contract

A new tool normally has this shape:

```text
tools/<tool-name>/
├── .python-version
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
├── THIRD_PARTY_NOTICES.md
├── src/<package_name>/
└── tests/
```

- Use a `src/` layout and a declared `[project.scripts]` CLI entry point.
- Choose and record the Python minor version from live dependency evidence.
- Commit `uv.lock`; it is authoritative for that tool.
- Put runtime dependencies in `[project.dependencies]` and lint, type, and test
  tooling in the development dependency group.
- Prefer a small CLI and typed library seam over ad hoc executable scripts.
- Keep analysis deterministic for identical inputs and configuration. Reports
  must record tool version, configuration, input hashes, and output hashes.
- Validate inputs and fail with actionable messages. Never silently normalize,
  resample, overwrite, or discard source evidence.

Run a tool from any repository directory with explicit project selection:

```bash
uv sync --project tools/<tool-name> --locked
uv run --project tools/<tool-name> <command> --help
```

## Local data and artifacts

- `data/` is for local recordings and derived input data. Everything except its
  README is ignored by Git.
- `artifacts/` is for generated JSON, CSV, plots, audio, MIDI, and reports.
  Everything except its README is ignored by Git.
- Do not globally ignore audio extensions; small synthetic or explicitly
  redistributable test fixtures may be committed inside a tool.
- Never commit a recording, dataset, or generated artifact without explicit
  human approval plus a license, privacy, provenance, and repository-size
  review.
- If another repository needs retained evidence, transfer only the explicitly
  approved artifact and record its SoundBench tool commit, configuration, input
  hash, and output hash there.

## Dependencies and licenses

This is a public repository. Tool isolation prevents product coupling but does
not remove license obligations.

- Follow [`LICENSE_POLICY.md`](LICENSE_POLICY.md) for every direct and
  transitive dependency.
- Each tool must declare its own license before production code is committed.
- Record dependencies, versions, licenses, notices, and material obligations in
  that tool's `THIRD_PARTY_NOTICES.md`.
- Copyleft or source-available dependencies require a tool-local compatibility
  decision that accounts for public distribution and intended use.
- Reject unclear terms and dependencies whose restrictions cannot be satisfied.
- Do not infer that a dependency is acceptable merely because the tool is not
  shipped in a product image.

## Quality and CI

Each tool defines equivalent commands in its README and CI. Unless its recorded
constraints justify a change, the integration gate is:

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest
uv run <tool-command> --help
```

Run these commands from the tool directory or with `--project`. A root GitHub
Actions workflow may target the tool by path, but it must use that tool's Python
version and locked environment. Do not let one tool's dependency resolution or
failure silently affect another tool.

Do not publish or integrate on red, absent, or stale CI. Independent review must
match the final PR HEAD and return clean before a PR is ready for human merge.

## Working style

- Start with a bounded research question and measurable output.
- Keep observations separate from recommendations and record known uncertainty.
- Prefer measured ratios and renderer calibration over treating MIDI velocity
  as standardized loudness.
- Keep the simplest implementation that produces trustworthy evidence.
- Ask before changing repository boundaries, public report formats, licensing
  policy, publication rules, or another project's contract.
