# AGENTS.md

Guidance for Codex and other agents working in this `SpikeAgent/` package.

## Scope

These instructions apply to everything under `SpikeAgent/`. This directory is a
standalone Python package checkout with its own `.git` directory, `pyproject.toml`,
`src/` layout, tests, docs, Dockerfiles, and distribution artifacts.

## Project Shape

- Package source lives in `src/spikeagent/`.
- The Streamlit app entry point is `src/spikeagent/app/main.py`; the console script is
  `spikeagent = "spikeagent.app.main:main"`.
- Agent graph and tool orchestration live under `src/spikeagent/app/`.
- SpikeInterface workflow tools live under `src/spikeagent/app/tool/`.
- VLM curation and merge analysis live under `src/spikeagent/curation/`.
- Tests live under `tests/`, currently focused on curation behavior.
- User-facing docs live under `docs/`; tutorials live under `tutorials/`.
- Docker runtime files live under `dockerfiles/` and `run-spikeagent.sh`.

## Environment

- Target Python is `>=3.11`.
- For local development, install from this directory:

  ```bash
  pip install -e ".[app,dev]"
  ```

- The app and VLM paths use API keys loaded from `.env` via `python-dotenv`.
  Never commit `.env`, API keys, recordings, user datasets, or generated analysis outputs.
- VLM curation currently depends on model-provider credentials. Prefer tests that mock
  provider calls unless the user explicitly asks for live API validation.

## Commands

Run commands from `SpikeAgent/` unless noted otherwise.

```bash
python -m pytest
python -m pytest tests/curation
python -m ruff check src tests
python -m black --check src tests
python -m mypy src
python -m spikeagent.app.main
```

Use the narrower pytest command when working only on curation tests. Run the app command
only when Streamlit and app extras are installed and the user expects an interactive
local app.

## Editing Rules

- Prefer changes in `src/spikeagent/` and matching focused tests in `tests/`.
- Keep public package behavior consistent with the README and docs when changing user
  workflows, CLI/app startup, curation outputs, or Docker usage.
- Do not edit generated or cache files for normal feature work:
  - `dist/`
  - `src/spikeagent.egg-info/`
  - any `__pycache__/`
  - notebook checkpoint directories, if present
- Do not add large neural recording datasets, model outputs, plots, or temporary
  Streamlit/runtime files to the repository.
- Keep package data referenced by `pyproject.toml` in sync when adding app prompts,
  CSS, YAML autorun parameters, or bundled SpikeInterface API docs.

## Testing Notes

- The project uses pytest with `test_*.py`, `Test*`, and `test_*` discovery configured
  in `pyproject.toml`.
- Tests insert `src/` on `sys.path`; keep imports package-relative and avoid depending
  on the current working directory where possible.
- SpikeInterface tests can be computationally heavier than ordinary unit tests. Prefer
  small synthetic recordings, fixed seeds, in-memory analyzers, and temporary
  directories.
- For VLM features, separate deterministic preprocessing/dataframe logic from live
  model calls so the core behavior can be tested without external services.

## Style

- The configured line length is 100 for Black and Ruff.
- Follow the existing module style, but prefer clear package imports from
  `spikeagent...` for new code.
- Keep Streamlit UI state changes localized to app modules. Avoid introducing
  Streamlit dependencies into pure curation or data-processing helpers.
- Preserve user workflow guardrails in curation guidance, especially confirmation steps
  before applying VLM curation results.
