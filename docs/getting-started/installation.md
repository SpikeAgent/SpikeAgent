# Installation

SpikeAgent supports Python 3.11 or later.

## Install From Source

```bash
git clone https://github.com/SpikeAgent/SpikeAgent.git
cd SpikeAgent
pip install -e ".[app]"
```

For development, include the development tools:

```bash
pip install -e ".[app,dev]"
```

For documentation work, install the docs extras:

```bash
pip install -e ".[docs]"
```

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
