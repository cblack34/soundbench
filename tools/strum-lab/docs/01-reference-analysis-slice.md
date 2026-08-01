# Tactical slice: reference analysis v0.1

**Status:** approved, active, and revisable
**Authority:** subordinate to the repository `AGENTS.md`, current human
direction, and GitHub issue #2

## Outcome

Establish whether deterministic signal measurements can replace subjective
iteration when calibrating guitar-strum timing, dynamics, and spectral balance.
The slice succeeds when synthetic ground truth and one local E-major recording
produce trustworthy, inspectable evidence.

## Boundaries

This slice owns one standalone uv CLI, its versioned manifest/report contract,
tests, documentation, dependency decisions, and path-scoped CI. It does not
change Melos, generate MIDI, recommend renderer parameters, perform source
separation, infer musical structure, or publish local recordings.

## Gates and stop conditions

1. Use only dependencies whose Python 3.14 compatibility and license terms are
   recorded; the initial probe removed SciPy because NumPy covers the bounded
   v0.1 signal operations with fewer transitive obligations.
2. Prove onset timing and level behavior against generated signals.
3. Inspect detected attacks over the real waveform before treating results as
   evidence.
4. Keep band energy and attack lag labeled as proxies, not string separation.
5. Stop on clipping, automatic gain control, click bleed, ambiguous channel
   handling, misleading detection, or unclear dependency terms.

## Acceptance evidence

- Locked, independently runnable uv project.
- Deterministic reports with version, configuration, and SHA-256 provenance.
- Synthetic onset timing within the documented tolerance.
- Manual verification of the real-recording overlay.
- Full lint, format, type, test, CLI, CI, and independent-review gates green.
