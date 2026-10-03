# Reproducibility

This document describes the repository-side plan for reproducing analyses reported in
the SpikeAgent manuscript.

Some workflows require external datasets and live LLM/VLM provider credentials. Live
model calls may be nondeterministic and may incur API costs.

## Environment

Install from the repository root:

```bash
pip install -e ".[app,dev]"
```

The package targets Python 3.11+ for local development. The manuscript reports analyses
run with Python 3.10.13 and the following key packages:

- LangGraph 0.2.64
- LangChain 0.3.11
- SpikeInterface 0.102.3
- Jupyter Notebook 7.2.2
- Seaborn 0.13.2
- Pandas 2.2.1
- SciPy 1.14.1
- NumPy 1.26.4
- scikit-learn 1.4.1.post1
- Matplotlib 3.9.3
- UMAP-learn 0.5.6
- HDBSCAN 0.8.40
- Streamlit 1.41.1

Spike sorter versions reported in the manuscript:

- MountainSort 4 1.0.6
- MountainSort 5 0.3.3
- KiloSort 4 4.0.21
- HerdingSpikes 0.4.6
- Tridesclous 1.6.8

## Required Credentials

VLM curation and merge analyses may require one or more model-provider API keys:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`

Do not commit API keys or `.env` files.

## Data

See `DATA_AVAILABILITY.md` for the dataset and artifact inventory.

Known public data:

- Neuropixels 2.0 recordings: https://doi.org/10.5522/04/24411841

Pending deposits/placeholders:

- `FLEXIBLE_PROBE_DATA_DOI_OR_URL`
- `SOURCE_DATA_DOI_OR_URL`

Author decisions as of 2026-08-28:

- MEArec simulated datasets will be documented through the manuscript Methods rather
  than a generated-data deposit, unless the authors later choose to release cleaned
  notebooks/configs.
- The current public GitHub repository is considered sufficient for code availability;
  no separate Zenodo or Code Ocean archive is currently planned.

## Reproducibility Assets

Manuscript reproduction scaffolding lives in `reproducibility/`.

Current scaffold:

- `reproducibility/README.md`
- `reproducibility/data_manifest.template.tsv`
- `reproducibility/configs/`

Expected future scripts/configs:

- Optional cleaned MEArec simulation notebooks, scripts, or configs if the authors
  decide to publish them beyond the Methods description.
- Curation benchmark scripts.
- Merge benchmark scripts.
- Figure/table source-data export scripts.
- Dataset-specific manifests mapping deposited files to manuscript figures and tables.

## Running Tests

Focused curation tests can be run from this directory:

```bash
python -m pytest tests/curation
```

Full local checks, when dependencies are installed:

```bash
python -m pytest
python -m ruff check src tests
python -m black --check src tests
python -m mypy src
```

## Reproducibility Limits

- Live VLM calls can vary across model versions and sampling settings.
- Some analyses may require paid API usage.
- Raw and generated electrophysiology datasets are intentionally not stored in Git.
- Large outputs should be deposited in public data repositories and linked from
  `DATA_AVAILABILITY.md`.
