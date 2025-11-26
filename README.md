<div align="center">
  <img src="src/logo.png" alt="SpikeAgent Logo" width="300"/>
</div>

# SpikeAgent

**An AI-powered assistant for spike sorting and neural data analysis**

SpikeAgent is a web-based AI assistant designed to help neuroscience laboratories analyze neural electrophysiology data. It provides an intuitive interface for spike sorting workflows, data curation, and neural data analysis, powered by state-of-the-art language models (OpenAI, Anthropic, and Google's Gemini).

## What is SpikeAgent?

SpikeAgent automates and streamlines the spike sorting pipeline, from raw neural recordings to curated spike trains. It leverages AI to assist with:

- **Spike sorting**: Automated detection and classification of action potentials
- **Data curation**: AI-assisted quality control and unit validation
- **Visual analysis**: Vision-language models for analyzing spike sorting outputs
- **Workflow guidance**: Interactive assistance throughout the analysis pipeline

The tool integrates with [SpikeInterface](https://github.com/SpikeInterface/spikeinterface), a unified framework for spike sorting, providing a seamless experience for analyzing neural data from various recording systems.

## Setup for Your Lab

### Prerequisites

- **Docker** installed and running on your system
- **API Keys** for at least one AI provider:
  - [OpenAI API Key](https://platform.openai.com/api-keys)
  - [Anthropic API Key](https://console.anthropic.com/)
  - [Google API Key](https://makersuite.google.com/app/apikey)
- **For GPU version**: NVIDIA GPU with CUDA support and appropriate drivers

### Docker Images

SpikeAgent provides two Docker image variants to suit different hardware configurations:

- **CPU Version** (`spikeagent_0.102.3_cpu`): For systems without GPU support or when GPU acceleration is not required
- **GPU Version** (`spikeagent_0.102.3_gpu`): For systems with NVIDIA GPUs for accelerated computation

> **Note**: Some spike sorters (e.g., Kilosort4) require GPU support. If you plan to use these sorters, you must use the GPU version.

**For detailed setup, build, and run instructions**, see the individual README files:
- [CPU Version README](spikeagent_0.102.3_cpu/README.md) - Complete setup guide for CPU version
- [GPU Version README](spikeagent_0.102.3_gpu/README.md) - Complete setup guide for GPU version

Once the Docker container is running, access the application at `http://localhost:8501` in your web browser.

## Open Source Neural Data

You can test SpikeAgent with open datasets such as [Neuropixels 2.0 chronic recordings in mice](https://doi.org/10.5522/04/24411841.v1) and [AutoSort flexible electrode recordings](https://github.com/LiuLab-Bioelectronics-Harvard/AutoSort).

## Tutorials

The repository includes Jupyter notebook tutorials to help you get started:

- **`jupyter notebook tutorials/vlm_curation_tutorial.ipynb`**: Comprehensive tutorial on using Vision Language Models (VLM) for AI-assisted spike curation
  - Finding potential merge candidates automatically
  - Analyzing visual features using AI (crosscorrelograms and amplitude plots)
  - Making merge decisions based on AI analysis
  - Saving and reviewing merge decision logs

## Project Structure

```
spikeagent/
├── spikeagent_0.102.3_cpu/              # CPU Docker image configuration
├── spikeagent_0.102.3_gpu/              # GPU Docker image configuration
└── jupyter notebook tutorials/          # Jupyter notebook tutorials
    └── vlm_curation_tutorial.ipynb      # Main VLM curation tutorial
```

## Getting Help

For detailed setup instructions, troubleshooting, and usage information, refer to:
- [CPU Version README](spikeagent_0.102.3_cpu/README.md)
- [GPU Version README](spikeagent_0.102.3_gpu/README.md)

## Citation

If you find SpikeAgent useful for your work, please cite:

**SpikeAgent**:
Zuwan Lin#, Arnau Marin-Llobet#, Jongmin Baek, Yichun He, Jaeyong Lee, Wenbo Wang, Xinhe Zhang, Ariel J. Lee, Ningyue Liang, Jin Du, Jie Ding, Na Li, Jia Liu*  
Preprint at bioRxiv (2025): https://doi.org/10.1101/2025.02.11.637754

**SpikeInterface** (if used):
Buccino, Alessio Paolo, Hurwitz, Cole Lincoln, Garcia, Samuel, Magland, Jeremy, Siegle, Joshua H, Hurwitz, Roger, & Hennig, Matthias H. (2020). SpikeInterface, a unified framework for spike sorting. Elife, 9, e61834.
