# SpikeAgent

SpikeAgent is an AI-powered assistant for spike sorting and neural data analysis. It combines a Streamlit chat interface, SpikeInterface workflows, and vision-language-model curation tools to help laboratories move from raw electrophysiology recordings to curated spike trains.

The project provides two main ways to work:

- **Interactive analysis** through the SpikeAgent web app.
- **Programmatic curation** through Python APIs for VLM unit classification, merge analysis, and diagnostic plotting.

## Start Here

- [Install SpikeAgent](getting-started/installation.md)
- [Configure model provider API keys](getting-started/api-keys.md)
- [Run with Docker](getting-started/docker.md)
- [Use the interactive app](user-guide.md)
- [Run VLM curation programmatically](tutorials/vlm-curation-and-merging.md)

## Core Capabilities

- Load electrophysiology recordings supported by SpikeInterface.
- Guide preprocessing, spike sorting, visualization, curation, and merge workflows.
- Generate diagnostic unit images for human or VLM inspection.
- Classify units as good or bad using VLM-assisted curation.
- Evaluate candidate merge groups for oversplit units.
- Preserve human-in-the-loop review before final curation decisions.

## Project Links

- [GitHub repository](https://github.com/SpikeAgent/SpikeAgent)
- [SpikeInterface documentation](https://spikeinterface.readthedocs.io/)
- [Citation](citation.md)
