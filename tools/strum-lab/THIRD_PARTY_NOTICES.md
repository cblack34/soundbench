# Third-party notices

Resolved versions come from the committed `uv.lock`. License expressions and
texts were checked in the installed distributions' `METADATA` and
`.dist-info/licenses/` directories. Package source links below identify the
exact Python distributions.

The repository distributes source and a lockfile, not dependency wheels. If
Strum Lab is later bundled or redistributed with its environment, preserve the
applicable dependency license texts and repeat the binary-content review.

## Runtime dependency decision

| Package | Resolved version | License | Use and source |
| --- | --- | --- | --- |
| [NumPy](https://pypi.org/project/numpy/2.5.1/) | 2.5.1 | BSD-3-Clause plus permissive licenses identified in its wheel | Imported numerical arrays and windowed FFT. Acceptable; retain its bundled license text when redistributing the wheel. |
| [Pydantic](https://pypi.org/project/pydantic/2.13.4/) | 2.13.4 | MIT | Imported strict manifest/report validation. Acceptable with notice retention. |
| [pydantic-core](https://pypi.org/project/pydantic-core/2.46.4/) | 2.46.4 | MIT | Imported transitively by Pydantic. Acceptable with notice retention. |
| [annotated-types](https://pypi.org/project/annotated-types/0.8.0/) | 0.8.0 | MIT | Imported transitively by Pydantic. Acceptable with notice retention. |
| [typing-inspection](https://pypi.org/project/typing-inspection/0.4.2/) | 0.4.2 | MIT | Imported transitively by Pydantic. Acceptable with notice retention. |
| [typing-extensions](https://pypi.org/project/typing-extensions/4.16.0/) | 4.16.0 | PSF-2.0 | Imported transitively by Pydantic. Acceptable with notice retention. |
| [PyYAML](https://pypi.org/project/PyYAML/6.0.3/) | 6.0.3 | MIT | Imported YAML manifest parsing. Acceptable with notice retention. |

No runtime dependency supplies audio, model, or research data. Strum Lab uses
Python's standard-library `wave` module for PCM decoding and therefore does not
link or redistribute `libsndfile`. Windowed FFT and bounded peak selection use
NumPy directly, avoiding a SciPy runtime and its bundled numerical libraries.

## Build and development dependency decision

| Package | Resolved version | License | Use and source |
| --- | --- | --- | --- |
| [Hatchling](https://pypi.org/project/hatchling/1.31.0/) | 1.31.0 | MIT | Build backend and development dependency. Acceptable with notice retention. |
| [pathspec](https://pypi.org/project/pathspec/1.1.1/) | 1.1.1 | MPL-2.0 | Hatchling-only transitive dependency. Accepted for isolated build use: SoundBench does not modify, copy, or distribute its source; MPL obligations remain file-level if that changes. |
| [trove-classifiers](https://pypi.org/project/trove-classifiers/2026.6.1.19/) | 2026.6.1.19 | Apache-2.0 | Hatchling-only metadata dependency. Acceptable with license and NOTICE obligations when redistributed. |
| [pytest](https://pypi.org/project/pytest/9.1.1/) | 9.1.1 | MIT | Test runner only. Acceptable with notice retention. |
| [iniconfig](https://pypi.org/project/iniconfig/2.3.0/) | 2.3.0 | MIT | pytest-only transitive dependency. Acceptable with notice retention. |
| [packaging](https://pypi.org/project/packaging/26.2/) | 26.2 | Apache-2.0 OR BSD-2-Clause | pytest-only transitive dependency. Acceptable under either permissive option with notice retention. |
| [pluggy](https://pypi.org/project/pluggy/1.6.0/) | 1.6.0 | MIT | pytest-only transitive dependency. Acceptable with notice retention. |
| [Pygments](https://pypi.org/project/Pygments/2.20.0/) | 2.20.0 | BSD-2-Clause | pytest-only terminal formatting. Acceptable with notice retention. |
| [Ruff](https://pypi.org/project/ruff/0.16.1/) | 0.16.1 | MIT | Standalone lint/format executable used only during development and CI. Acceptable with notice retention. |
| [ty](https://pypi.org/project/ty/0.0.65/) | 0.0.65 | MIT | Standalone type-check executable used only during development and CI. Acceptable with notice retention. |

The MPL-2.0 pathspec dependency is intentionally confined to the build toolchain
and is not imported by Strum Lab runtime code. No unclear, noncommercial,
research-only, data, or model license is present in the locked environment.
