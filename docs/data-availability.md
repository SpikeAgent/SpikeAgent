# Data Availability

This repository contains SpikeAgent source code. Large raw electrophysiology recordings, generated benchmark artifacts, and source data for manuscript analyses are not stored directly in Git.

## Public Data

Known public datasets include:

- Neuropixels 2.0 chronic recordings in mice: <https://doi.org/10.5522/04/24411841>.
  The UCL Research Data Repository includes the AL031 and AL036 recordings used
  for the Neuropixels analyses and few-shot generalizability experiments.
- Flexible-probe recordings generated in this study: <https://doi.org/10.5281/zenodo.22180105>.

## Simulated Data

The MEArec simulated ground-truth datasets used for the 1-hour and 20-minute drift
benchmarks were generated using the simulation procedure described in the
manuscript Methods. No separate generated-data deposit is specified.

## Pending Public Artifacts

The repository's data-availability plan identifies these pending public deposits:

- Figure and table source data.

The authors currently consider the public GitHub repository sufficient for code
availability; no separate code DOI archive is planned. This plan may change
before publication.

The full [repository data-availability inventory](https://github.com/SpikeAgent/SpikeAgent/blob/main/DATA_AVAILABILITY.md)
tracks the pending URLs and access statements.

## What Not To Commit

Do not commit:

- Raw neural recordings.
- Generated SpikeInterface analyzer folders.
- Generated source-data archives.
- Generated plots or VLM reasoning dumps.
- API keys or `.env` files.

Use discipline-specific repositories, Zenodo, Figshare, Dryad, institutional repositories, or another stable public archive for large data and publication-critical artifacts.
