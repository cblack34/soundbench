# Tools

Each child directory is an independent packaged uv command-line application.
It owns its `.python-version`, `pyproject.toml`, `uv.lock`, `.venv`, source,
tests, documentation, license, notices, and CI gate.

The `tools/` directory is not a uv project or workspace. Do not add shared
dependencies or a shared virtual environment here.
