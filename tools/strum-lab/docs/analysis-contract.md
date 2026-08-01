# Analysis contract

## Manifest v1

The UTF-8 YAML manifest declares facts supplied by the recorder. Strum Lab does
not infer or silently revise them.

Required fields describe:

- a stable recording identifier;
- tempo and meter;
- the explicitly selected input channel (`left`, `right`, or `mean`);
- the first analyzed bar, number of analyzed bars, beat positions, and stroke
  direction; and
- optional recording notes and beat labels.

Bar and beat numbers are one-based. Time zero is the first audio sample. An
expected beat at bar 2, beat 1 in 4/4 at 60 BPM therefore occurs at 4.0 seconds.
Version 1 supports quarter-note beat units only (`beat_unit: 4`); other meters
must wait for an explicit tempo-unit contract rather than being reinterpreted.

## Report v1

`report.json` contains:

- schema and tool versions;
- the input path as supplied, SHA-256, PCM format, duration, and selected
  channel;
- the complete normalized analysis configuration;
- recording-level clipping and noise-floor observations;
- one measurement per expected stroke; and
- median and median-absolute-deviation summaries grouped by beat; and
- SHA-256 hashes for `strokes.csv` and `diagnostic.svg`.

`strokes.csv` is the stable tabular projection. `diagnostic.svg` overlays
expected and detected onsets over a downsampled waveform envelope.
`checksums.sha256` hashes all three outputs.

## Stroke metrics

- expected and detected onset time, plus signed timing error;
- peak and 100 ms RMS level in dBFS;
- attack energy over 100 ms;
- low, mid, and high STFT energy ratios;
- high-band onset minus low-band onset in milliseconds; and
- manifest direction and beat label.

The default bands are 80-300 Hz, 300-1,200 Hz, and 1,200-6,000 Hz. They are
analysis proxies rather than string identities or a direction classifier.
Configuration is recorded in the report so later changes do not rewrite
historical meaning.
