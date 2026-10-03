# Data Availability

This repository contains SpikeAgent source code. Large raw electrophysiology recordings, generated benchmark artifacts, and source data for manuscript analyses are not stored directly in Git.

## Public Data

Known public datasets include:

- Neuropixels 2.0 chronic recordings in mice: <https://doi.org/10.5522/04/24411841>

## Pending Public Artifacts

Publication artifacts that may need DOI-backed release or final access statements include:

- Flexible-probe recording generated for SpikeAgent validation.
- Figure and table source data.
- MEArec simulated ground-truth datasets.
- Exact archived SpikeAgent code release used for manuscript analyses.

## What Not To Commit

Do not commit:

- Raw neural recordings.
- Generated SpikeInterface analyzer folders.
- Generated source-data archives.
- Generated plots or VLM reasoning dumps.
- API keys or `.env` files.

Use discipline-specific repositories, Zenodo, Figshare, Dryad, institutional repositories, or another stable public archive for large data and publication-critical artifacts.
