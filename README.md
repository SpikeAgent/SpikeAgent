<p align="center">
  <img src="docs/spikeagent_logo.png" alt="SpikeAgent Logo" width="300" style="display:block; margin:auto; background:#fff; box-shadow:0 2px 12px rgba(0,0,0,0.15); border-radius:10px;">
</p>

<!-- 
If the logo image does not appear above this line, make sure the file exists at:
docs/img/spikeagent_logo.png
-->

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

- **CPU Version**: For systems without GPU support or when GPU acceleration is not required
- **GPU Version**: For systems with NVIDIA GPUs for accelerated computation

> **Note**: Some spike sorters (e.g., Kilosort4) require GPU support. If you plan to use these sorters, you must use the GPU version.

#### Using Pre-built Images

**CPU Version (Pre-built Package Available):**

A pre-built CPU Docker image is available on GitHub Container Registry. You can pull and run it directly:

```bash
# Pull the latest CPU image
docker pull ghcr.io/arnaumarin/spikeagent-cpu:latest

# Create a .env file with your API keys (see Prerequisites section)
# Then run the container
docker run --rm -p 8501:8501 --env-file .env ghcr.io/arnaumarin/spikeagent-cpu:latest
```

> **Important**: You must create a `.env` file in your working directory with at least one API key before running the container. The `.env` file should contain:
> ```
> OPENAI_API_KEY=your_openai_key_here
> ANTHROPIC_API_KEY=your_anthropic_key_here
> GOOGLE_API_KEY=your_google_key_here
> ```
> You need at least one of these keys for the application to work.

**GPU Version (Build Locally):**

The GPU version is not yet available as a pre-built package. You need to build it locally:

```bash
# Build the GPU image
docker build -f docker_files/Dockerfile.gpu -t spikeagent:gpu .

# Create a .env file with your API keys, then run the container
docker run --rm --gpus all -p 8501:8501 --env-file .env spikeagent:gpu
```

> **Note**: The first time you pull from GitHub Container Registry, you may need to authenticate. You can create a [Personal Access Token (PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) with `read:packages` permission and login using:
> ```bash
> echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
> ```

Once the Docker container is running, access the application at `http://localhost:8501` in your web browser.

## Open Source Neural Data

You can test SpikeAgent with open datasets such as [Neuropixels 2.0 chronic recordings in mice](https://doi.org/10.5522/04/24411841.v1) and [AutoSort flexible electrode recordings](https://github.com/LiuLab-Bioelectronics-Harvard/AutoSort).

## Tutorials

The repository includes Jupyter notebook tutorials to help you get started:

- **`notebook tutorials/vlm_noise_rejection_tutorial.ipynb`**: Tutorial on using Vision Language Models (VLM) for AI-assisted spike curation
  - Classifying units as "Good" or "Bad" based on visual features
  - Using waveforms, autocorrelograms, and spike locations for quality control
  - Applying curation to filter out noise units

- **`notebook tutorials/vlm_merge_simple_tutorial.ipynb`**: Tutorial on using VLM for merge analysis
  - Finding potential merge candidates automatically
  - Analyzing visual features using AI (crosscorrelograms, amplitude plots, PCA clustering)
  - Making merge decisions based on AI analysis
  - Applying merges to consolidate units from the same neuron

## Project Structure

```
spikeagent/
├── src/spikeagent/                      # Main source code package
│   ├── app/                            # Application code
│   └── curation/                       # Curation and VLM analysis tools
├── docker_files/                       # Docker configuration files
│   ├── Dockerfile.cpu                  # CPU Docker image
│   └── Dockerfile.gpu                  # GPU Docker image
├── docs/                               # Documentation
│   └── img/                            # Documentation images
├── notebook tutorials/                 # Jupyter notebook tutorials
│   ├── vlm_merge_simple_tutorial.ipynb # VLM merge analysis tutorial
│   └── vlm_noise_rejection_tutorial.ipynb # VLM curation tutorial
└── tests/                              # Test suite
```

## Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

- **[Installation Guide](docs/installation.md)**: Detailed setup and installation instructions
- **[User Guide](docs/user-guide.md)**: How to use SpikeAgent for spike sorting and curation
- **[API Reference](docs/api-reference.md)**: Programmatic API documentation

## Getting Help

For detailed setup instructions, troubleshooting, and usage information:
- Review the [Installation Guide](docs/installation.md)
- Check the [User Guide](docs/user-guide.md) for workflows
- Explore the Jupyter notebook tutorials in `notebook tutorials/`
- Ensure your `.env` file contains the required API keys

## Citation

If you find SpikeAgent useful for your work, please cite:

**SpikeAgent**:
Lin, Z., Marin-Llobet, A., Baek, J., He, Y., Lee, J., Wang, W., ... & Liu, J. (2025). Spike sorting AI agent. Preprint at bioRxiv: https://doi.org/10.1101/2025.02.11.637754

**SpikeInterface**:
Buccino, A. P., Hurwitz, C. L., Garcia, S., Magland, J., Siegle, J. H., Hurwitz, R., & Hennig, M. H. (2020). SpikeInterface, a unified framework for spike sorting. Elife, 9, e61834.
