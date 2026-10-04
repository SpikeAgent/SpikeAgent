# Installation

SpikeAgent supports Python 3.11 or later.

## Install From Source

```bash
git clone https://github.com/SpikeAgent/SpikeAgent.git
cd SpikeAgent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[app]"
```

On Windows, activate the environment with `.venv\Scripts\Activate.ps1` in PowerShell.

For development, include the development tools:

```bash
pip install -e ".[app,dev]"
```

For documentation work only, install the documentation requirements:

```bash
python -m pip install -r docs/requirements.txt
python -m mkdocs serve
```

Open <http://127.0.0.1:8000/SpikeAgent/>. If port 8000 is in use, run
`python -m mkdocs serve --dev-addr 127.0.0.1:8001` and use port 8001 instead.

If you also need the Python package, `python -m pip install -e ".[docs]"`
installs SpikeAgent and its documentation extras together.

## Run The App

After installing the app extra, start SpikeAgent with:

```bash
spikeagent
```

or:

```bash
python -m spikeagent.app.main
```

Then open:

```text
http://localhost:8501
```

## Optional Sorters

Spike sorters are not all bundled by default. Install only the sorters needed for your workflow:

```bash
pip install kilosort
pip install mountainsort4
pip install mountainsort5
pip install herdingspikes
pip install MEArec
```

Some sorters require additional system dependencies or GPU support.

## Verify Imports

```python
from spikeagent import run_vlm_curation, run_vlm_merge, create_unit_img_df

print("SpikeAgent is installed.")
```
