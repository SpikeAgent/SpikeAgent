# Reproducibility

Some SpikeAgent workflows require external datasets and live LLM or VLM provider credentials. Live model calls may be nondeterministic and may incur API costs.

## Environment

Install for local development:

```bash
pip install -e ".[app,dev]"
```

Install docs dependencies:

```bash
python -m pip install -r docs/requirements.txt
```

## Key Runtime Dependencies

SpikeAgent targets Python 3.11 or later. Core dependencies include:

- SpikeInterface and ProbeInterface for electrophysiology analysis.
- LangChain and LangGraph for model and tool orchestration.
- OpenAI, Anthropic, and Google Gemini integrations.
- Streamlit for the web app.
- NumPy, SciPy, pandas, h5py, matplotlib, and Pillow for scientific data handling and plotting.

## Study Data

- Public Neuropixels 2.0 recordings, including AL031 and AL036:
  <https://doi.org/10.5522/04/24411841>.
- Flexible-probe recordings generated in this study:
  <https://doi.org/10.5281/zenodo.22180105>.
- MEArec simulated ground-truth datasets for the 1-hour and 20-minute drift
  benchmarks were generated using the procedure described in the manuscript Methods.

## Tests

Run focused curation tests:

```bash
python -m pytest tests/curation
```

Run broader local checks when all dependencies are installed:

```bash
python -m pytest
python -m ruff check src tests
python -m black --check src tests
python -m mypy src
```

## Reproducibility Limits

- Live VLM calls can vary across model versions and sampling settings.
- Some analyses require paid API usage.
- Raw and generated electrophysiology datasets are intentionally not stored in Git.
- Large outputs should be deposited in public data repositories and linked from the data availability page.

The [repository reproducibility plan](https://github.com/SpikeAgent/SpikeAgent/blob/main/REPRODUCIBILITY.md)
records the manuscript environment separately from the current package requirements.
