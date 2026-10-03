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
| Flexible-probe recording generated in this study | Flexible-probe validation and VLM/human curation comparison | Public repository TBD | FLEXIBLE_PROBE_DATA_DOI_OR_URL | Planned | The authors intend to deposit this data publicly. Final repository and DOI/URL are pending. |
| Figure and table source data | Verification of plotted values, matrices, labels, timing, and model-output summaries | Public repository or Nature source-data files TBD | SOURCE_DATA_DOI_OR_URL | Planned | Source data have been shared internally for organization. Final contents and deposit route are pending. |
| MEArec 1-hour simulated ground-truth dataset | Ground-truth curation accuracy and sorter comparison | Methods description | See manuscript Methods | Reproducible from Methods | The authors plan to describe the simulation procedure in Methods rather than deposit generated simulation data. |
| MEArec 20-minute simulated drift dataset | Drift and merge benchmark | Methods description | See manuscript Methods | Reproducible from Methods | The authors plan to describe the simulation procedure in Methods rather than deposit generated simulation data. |
| SpikeAgent source code | Custom code developed for the study | GitHub | https://github.com/SpikeAgent/SpikeAgent | Yes | The authors consider the current GitHub repository sufficient for code availability; no separate DOI archive is currently planned. |

## Manuscript Data Availability Text

Use the final Data Availability statement from the manuscript as the authority once all
DOIs and accessions are known. As of this scaffold, the known public Neuropixels link
is:

```text
https://doi.org/10.5522/04/24411841
```

If this DOI is used in the manuscript's Data Availability section, include the dataset
in the manuscript References:

```text
Lebedeva, A., Okun, M., Krumin, M. K. & Carandini, M. Chronic recordings from Neuropixels 2.0 probes in mice. UCL Research Data Repository https://doi.org/10.5522/04/24411841 (2023).
```

The following placeholders must be resolved before publication:

- `FLEXIBLE_PROBE_DATA_DOI_OR_URL`
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
