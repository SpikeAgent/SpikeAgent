# Manuscript Reproducibility Assets

This folder contains scripts, configs, and manifests intended to support the
SpikeAgent manuscript's Data Availability and Code Availability statements.

Raw data and large generated artifacts are stored outside Git and are listed in
`../DATA_AVAILABILITY.md`.

## Current Contents

- `data_manifest.template.tsv`: template for mapping manuscript datasets, source-data
  files, and generated artifacts to repositories/DOIs.
- `configs/`: placeholder directory for dataset and benchmark configuration files.

## Intended Structure

Future reproducibility assets should be organized here rather than inside package
runtime modules:

```text
reproducibility/
├── README.md
├── data_manifest.template.tsv
├── make_mearec_simulations.py
├── run_curation_benchmark.py
├── run_merge_benchmark.py
├── export_figure_source_data.py
└── configs/
    ├── simulated_1h.yaml
    ├── simulated_drift_20min.yaml
    ├── neuropixels_40min.yaml
    └── flexible_probe.yaml
```

The exact script names may change, but each script should clearly state:

- which manuscript result it supports;
- which input data it expects;
- which API keys, if any, it requires;
- which outputs it writes;
- whether the output is deterministic;
- where large outputs should be deposited.

As of 2026-08-28, the authors plan to rely on the manuscript Methods description for
MEArec simulation reproducibility. Cleaned simulation notebooks/scripts can still be
added here if the team later decides they are needed for review or publication.

## Data Safety

Do not commit:

- raw electrophysiology recordings;
- generated analyzer folders;
- generated source-data archives;
- model-provider API keys;
- `.env` files;
- large plots or VLM result dumps.

Use data repositories for large or publication-critical artifacts and link the stable
DOIs from `../DATA_AVAILABILITY.md`.
