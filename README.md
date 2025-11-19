# Spike Agent

A web-based AI assistant for spike sorting and neural data analysis, powered by OpenAI, Anthropic, and Google's Gemini models.

## Overview

This repository contains SpikeAgent, an AI-powered tool for neural data analysis and spike sorting workflows. The project provides two Docker image variants (CPU and GPU) and includes Jupyter notebook tutorials for learning, testing and experimentation.

## Docker Images

This repository includes two Docker image configurations:

### CPU Version (`spikeagent_0.102.3_cpu`)

The CPU version is optimized for systems without GPU support or when GPU acceleration is not required.

- **Base Image**: Python 3.11 slim
- **Use Case**: General-purpose usage, systems without NVIDIA GPUs
- **Build Command**: 
  ```bash
  cd spikeagent_0.102.3_cpu
  docker build -t spikeagent:latest .
  ```
- **Run Command**:
  ```bash
  docker run --rm -p 8501:8501 --env-file .env spikeagent:latest
  ```

For detailed setup instructions, see the [CPU version README](spikeagent_0.102.3_cpu/README.md).

### GPU Version (`spikeagent_0.102.3_gpu`)

The GPU version includes CUDA support for accelerated computation on NVIDIA GPUs.

- **Base Image**: NVIDIA CUDA 12.8.0 runtime with Ubuntu 22.04
- **Use Case**: Systems with NVIDIA GPUs, computationally intensive tasks
- **Requirements**: 
  - NVIDIA GPU with CUDA support
  - NVIDIA drivers installed
  - Docker with GPU support enabled
- **Build Command**:
  ```bash
  cd spikeagent_0.102.3_gpu
  docker build -t spikeagent:latest .
  ```
- **Run Command** (Linux):
  ```bash
  docker run --rm --gpus all -p 8501:8501 --env-file .env spikeagent:latest
  ```
- **Run Command** (Windows/Mac with Docker Desktop):
  ```bash
  docker run --rm --gpus all -p 8501:8501 --env-file .env spikeagent:latest
  ```

For detailed setup instructions and GPU troubleshooting, see the [GPU version README](spikeagent_0.102.3_gpu/README.md).

## Jupyter Notebook Tutorials

The repository includes Jupyter notebook tutorials to help you get started with Spike Agent features:

### Main Tutorial

- **`jupyter notebook tutorials/vlm_curation_tutorial.ipynb`**: A comprehensive tutorial on using Vision Language Models (VLM) for AI-assisted spike curation. This tutorial covers:
  - Finding potential merge candidates automatically
  - Analyzing visual features using AI (crosscorrelograms and amplitude plots)
  - Making merge decisions based on AI analysis
  - Saving and reviewing merge decision logs

### Additional Notebooks

- **`spikeagent_0.102.3_cpu/tool/utils/testllm.ipynb`**: Testing notebook for LLM functionality (CPU version)
- **`spikeagent_0.102.3_gpu/tool/utils/testllm.ipynb`**: Testing notebook for LLM functionality (GPU version)

## Quick Start

1. **Choose Your Docker Image**: Select either the CPU or GPU version based on your system capabilities
2. **Get API Keys**: You'll need at least one API key:
   - OpenAI API Key: https://platform.openai.com/api-keys
   - Anthropic API Key: https://console.anthropic.com/
   - Google API Key: https://makersuite.google.com/app/apikey
3. **Create `.env` File**: Add your API keys to a `.env` file in the appropriate Docker image directory
4. **Build and Run**: Follow the build and run commands for your chosen Docker image
5. **Access the Application**: Open http://localhost:8501 in your browser

## Project Structure

```
spikeagent/
├── spikeagent_0.102.3_cpu/              # CPU Docker image
├── spikeagent_0.102.3_gpu/              # GPU Docker image
└── jupyter notebook tutorials/           # Jupyter notebook tutorials
    └── vlm_curation_tutorial.ipynb       # Main VLM curation tutorial
```

## Requirements

- Docker Desktop installed and running
- For GPU version: NVIDIA GPU with CUDA support and appropriate drivers
- API keys for at least one supported AI provider (OpenAI, Anthropic, or Google)

## Getting Help

For detailed setup instructions, troubleshooting, and usage information, refer to the README files in each Docker image directory:
- [CPU Version README](spikeagent_0.102.3_cpu/README.md)
- [GPU Version README](spikeagent_0.102.3_gpu/README.md)

## Citation

If you find SpikeAgent useful for your work, please cite our paper:

Zuwan Lin#, Arnau Marin-Llobet#, Jongmin Baek, Yichun He, Jaeyong Lee, Wenbo Wang, Xinhe Zhang, Ariel J. Lee, Ningyue Liang, Jin Du, Jie Ding, Na Li, Jia Liu*  
Preprint at bioRxiv (2025): https://doi.org/10.1101/2025.02.11.637754

In addition, if you use the SpikeInterface framework, please cite the following paper:

Buccino, Alessio Paolo, Hurwitz, Cole Lincoln, Garcia, Samuel, Magland, Jeremy, Siegle, Joshua H, Hurwitz, Roger, & Hennig, Matthias H. (2020). SpikeInterface, a unified framework for spike sorting. Elife, 9, e61834.