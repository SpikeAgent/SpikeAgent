# Reproducibility

Some SpikeAgent workflows require external datasets and live LLM or VLM provider credentials. Live model calls may be nondeterministic and may incur API costs.

## Environment

Install for local development:

```bash
pip install -e ".[app,dev]"
```

Install docs dependencies:

```bash
pip install -e ".[docs]"
```

## Key Runtime Dependencies

SpikeAgent targets Python 3.11 or later. Core dependencies include:

- SpikeInterface and ProbeInterface for electrophysiology analysis.
- LangChain and LangGraph for model and tool orchestration.
- OpenAI, Anthropic, and Google Gemini integrations.
- Streamlit for the web app.
- NumPy, SciPy, pandas, h5py, matplotlib, and Pillow for scientific data handling and plotting.

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
