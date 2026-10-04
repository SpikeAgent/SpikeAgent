# AGENTS.md

Guidance for Codex and other agents working in SpikeAgent curation code.

## Scope

These instructions apply to `SpikeAgent/src/spikeagent/curation/`.
They supplement `SpikeAgent/AGENTS.md`.

## Project Shape

- `curation_new.py` exposes guidance-formatting functions used by the Streamlit agent.
- `vlm_curation/` implements VLM-based unit classification.
- `vlm_merge/` implements VLM-assisted merge analysis.
- Prompt assets live under `vlm_curation/prompts/` and `vlm_merge/prompts/`.
- Public curation exports are defined in `__init__.py`.

## Behavioral Contracts

- Curation guidance functions return formatted reasoning plus executable code snippets;
  keep this interface stable for the app.
- VLM curation produces per-unit classifications and reasoning from SpikeInterface
  analyzer-derived images and optional metrics.
- VLM merge analysis evaluates candidate unit pairs using inter-unit evidence such as
  template similarity, cross-correlograms, and amplitude distributions.
- Preserve explicit user-confirmation steps before applying curation or merge results,
  unless a documented autonomous mode already applies.

## SpikeInterface Preconditions

Before VLM curation, verify required analyzer extensions for selected features:

- `waveform_single` -> `templates`
- `waveform_multi` -> `templates`
- `autocorr` -> `correlograms`
- `spike_locations` -> `spike_locations`
- `amplitude_plot` -> `spike_amplitudes`
- metrics-enabled workflows -> `quality_metrics`

Compute upstream dependencies such as `random_spikes` and `waveforms` before
the extensions that require them.

Prefer clear preflight errors over allowing downstream model or plotting failures.

## Model And Data Safety

- Do not run live VLM/API calls in tests unless the user explicitly asks for live
  validation and provides credentials.
- Keep deterministic preprocessing, image/dataframe construction, and prompt loading
  testable without external services.
- Do not commit generated unit images, VLM reasoning CSVs, neural recordings, analyzer
  folders, or API keys.
- Treat prompt files as part of behavior; update tests or docs when prompt semantics
  change materially.

## Testing

Run from `SpikeAgent/`:

```bash
python -m pytest tests/curation
```

Use synthetic SpikeInterface data, fixed seeds, in-memory analyzers, and temporary
directories for focused tests.
