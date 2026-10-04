# Data Availability

This repository contains code for SpikeAgent. Large raw electrophysiology recordings,
generated benchmark artifacts, and source data for the manuscript are not stored
directly in Git.

The table below lists the datasets and data artifacts used in the SpikeAgent
manuscript, where they can be obtained, and which records still need a public DOI,
source-data upload, or access statement before publication.

## Dataset And Artifact Inventory

| Dataset / artifact | Used for | Source or repository | DOI / accession / URL | Public? | Notes |
| --- | --- | --- | --- | --- | --- |
| Public Neuropixels 2.0 recordings | Neuropixels analyses and few-shot generalizability experiments | UCL Research Data Repository | https://doi.org/10.5522/04/24411841 | Yes | Includes AL031 and AL036 recordings. |
| Flexible-probe recordings generated in this study | Flexible-probe validation and VLM/human curation comparison | Zenodo | https://doi.org/10.5281/zenodo.22180105 | Yes | Recordings generated for this study. |
| Figure and table source data | Verification of plotted values, matrices, labels, timing, and model-output summaries | Public repository or Nature source-data files TBD | SOURCE_DATA_DOI_OR_URL | Planned | Source data have been shared internally for organization. Final contents and deposit route are pending. |
| MEArec 1-hour simulated ground-truth dataset | Ground-truth curation accuracy and sorter comparison | Methods description | See manuscript Methods | Generated from Methods | Generated using the simulation procedure described in the manuscript Methods. No separate generated-data deposit is specified. |
| MEArec 20-minute simulated drift dataset | Drift and merge benchmark | Methods description | See manuscript Methods | Generated from Methods | Generated using the simulation procedure described in the manuscript Methods. No separate generated-data deposit is specified. |
| SpikeAgent source code | Custom code developed for the study | GitHub | https://github.com/SpikeAgent/SpikeAgent | Yes | The authors consider the current GitHub repository sufficient for code availability; no separate DOI archive is currently planned. |

## Manuscript Data Availability Text

The public Neuropixels 2.0 recordings analyzed in this study are available from the
UCL Research Data Repository at <https://doi.org/10.5522/04/24411841>. This repository
includes the AL031 and AL036 recordings used for the Neuropixels analyses and
few-shot generalizability experiments. The flexible-probe recordings generated in
this study are available at <https://doi.org/10.5281/zenodo.22180105>. The MEArec
simulated ground-truth datasets used for the 1-hour and 20-minute drift benchmarks
were generated using the simulation procedure described in the Methods section.

Include the public Neuropixels dataset in the manuscript References:

```text
Lebedeva, A., Okun, M., Krumin, M. K. & Carandini, M. Chronic recordings from Neuropixels 2.0 probes in mice. UCL Research Data Repository https://doi.org/10.5522/04/24411841 (2023).
```

The following placeholders must be resolved before publication:

- `SOURCE_DATA_DOI_OR_URL`

The following placeholders are no longer planned unless the authors change direction:

- `SIMULATED_DATA_DOI_OR_URL`
- `CODE_ARCHIVE_DOI_OR_URL`

## Restricted Data

If any dataset cannot be made public, the manuscript and reporting summary must state:

- the exact dataset affected;
- the specific reason access is restricted;
- the contact for access requests;
- who is eligible to request access;
- the conditions of access or data-use agreement;
- the expected response timeframe.

## What Is Not Stored Here

Do not commit:

- raw neural recordings;
- generated SpikeInterface analyzer folders;
- generated source-data archives;
- generated plots or VLM reasoning dumps;
- API keys or `.env` files.

Store large data and source-data packages in public data repositories or as journal
source-data files, then link the final DOI/URL or source-data record here.
