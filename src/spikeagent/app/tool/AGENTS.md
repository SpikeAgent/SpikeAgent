# AGENTS.md

Guidance for Codex and other agents working in SpikeAgent app tools.

## Scope

These instructions apply to `SpikeAgent/src/spikeagent/app/tool/`.
They supplement `SpikeAgent/AGENTS.md`.

## Project Shape

- Top-level `*_new.py` modules provide guidance functions for environment setup,
  recording loading/saving, preprocessing, sorting, visualization, and review.
- `document_tool.py` provides SpikeInterface documentation lookup behavior.
- `think_and_review_tool.py` supports explicit review-before-response behavior.
- `utils/` contains model selection, file/system helpers, Intan/NWB readers, compute
  helpers, and the Python REPL implementation.
- `si_custom/` contains SpikeInterface plotting and image dataframe helpers.
- `__init__.py` registers tool functions exported to the app.

## Behavioral Contracts

- Guidance functions return formatted reasoning plus executable code snippets. Preserve
  this pattern when editing or adding tools.
- Update `__all__` and `app/tool/__init__.py` whenever adding, removing, or renaming a
  tool function.
- Keep code snippets adaptable: variables created in the Python REPL may persist across
  agent turns.
- Preserve pipeline guardrails that ask users before advancing destructive, expensive,
  or semantically important workflow steps.

## Data And Execution Safety

- The Python REPL can execute arbitrary code. Keep timeout, sanitization, and warning
  behavior conservative.
- Never delete, overwrite, or move user recordings/results unless the user explicitly
  asks for that operation.
- Prefer read-only directory inspection before choosing raw data loaders or saved
  analyzer/recording paths.
- Validate probe/channel mismatches before saving recordings with attached probes.
- Do not hardcode local user paths, API keys, dataset paths, or model credentials.

## SpikeInterface Workflow Rules

- Keep data-format inference explicit and conservative for Neuropixels, Intan RHD, NWB,
  and SpikeInterface binary recordings.
- Use SpikeInterface objects and APIs rather than ad hoc file parsing when possible.
- For computationally heavy operations, prefer small examples, temporary directories,
  and clear user-facing warnings.
- Keep package data in `pyproject.toml` synchronized when adding app prompts, CSS,
  YAML autorun parameters, or bundled SpikeInterface API docs.

## Testing

Run from `SpikeAgent/`:

```bash
python -m pytest tests/curation
python -m ruff check src tests
python -m black --check src tests
```

For VLM or model-provider paths, mock external calls unless live validation is
explicitly requested.
