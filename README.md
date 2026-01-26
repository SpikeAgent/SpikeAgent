<p align="center">
  <img src="docs/spikeagent_logo.png" alt="SpikeAgent Logo" width="300" style="display:block; margin:auto; background:#fff; box-shadow:0 2px 12px rgba(0,0,0,0.1)">
</p>

<!--
If the logo image does not appear above this line, make sure the file exists at:
docs/img/spikeagent_logo.png
-->

[![GitHub stars](https://img.shields.io/github/stars/SpikeAgent/SpikeAgent)](https://github.com/LiuLab-Bioelectronics-Harvard/SpikeAgent/stargazers)

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

## Quick Start 

### What You Need

1. **Docker** - Make sure Docker Desktop is installed and running (for Docker installation)
   - OR **Python 3.11+** (for pip installation)
2. **One API Key** - Choose one of these:
   - [OpenAI API Key](https://platform.openai.com/api-keys) (required for VLM curation) - OR -
   - [Anthropic API Key](https://console.anthropic.com/) - OR -
   - [Google API Key](https://makersuite.google.com/app/apikey)

**Tested on:** Linux (Ubuntu) and macOS (Intel/Apple Silicon). 

### Installation Options

SpikeAgent offers two ways to install and run:

#### Option 1: Pip Installation (Recommended for Development)

```bash
Install from source
git clone https://github.com/SpikeAgent/SpikeAgent.git
cd SpikeAgent
pip install -e .

Create an .env file under the SpikeAgent folder and add ONE API key:
OPENAI_API_KEY=... (required for VLM curation)
ANTHROPIC_API_KEY=...
GOOGLE_API_KEY=...

# Run the application
spikeagent
# or
python -m spikeagent.app.main
```

#### Option 2: Docker 

SpikeAgent offers two ways to run with Docker:

- **CPU Version** - Works on any computer, easiest to set up
- **GPU Version** - For systems with NVIDIA GPUs (needed for some spike sorters like Kilosort4)

#### Using Pre-built CPU Image

**Step 1: Create a `.env` file**

Create a file named `.env` in your working directory with your API keys. You need **at least one** of these:

```bash
# Create the .env file
touch .env
```

Then add your API keys to the `.env` file. Here are examples:

**Example 1: Using OpenAI (Standard)**
```bash
OPENAI_API_KEY=sk-your-actual-key-here (required for VLM curation)
```

**Example 2: Using OpenAI (Custom/Institutional Endpoint)**
```bash
OPENAI_API_KEY=your_institution_key_here
OPENAI_API_BASE=https://your-institution-endpoint.com/v1
```

**Example 3: Using Anthropic**
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

**Example 4: Using Google/Gemini**
```bash
GOOGLE_API_KEY=your-google-api-key-here
```

**You only need ONE of these options** - choose the provider you prefer!

**Notes:**
VLM curation currently requires OpenAI (OPENAI_API_KEY). Anthropic/Google can be used for other LLM features
- If using a custom or institutional OpenAI endpoint, include both `OPENAI_API_KEY` and `OPENAI_API_BASE`
- If using standard OpenAI, you only need `OPENAI_API_KEY` (no `OPENAI_API_BASE` needed)
- The `.env` file should be in the same directory where you run the Docker commands


**Step 2: Run SpikeAgent**

**Option A: Using the automated script (Easiest):**

```bash
# Run without volume mounts (if you don't need to access local data)
./run-spikeagent.sh

# Run with volume mounts (to access your data directories)
./run-spikeagent.sh /path/to/your/data /path/to/results
```

**Volume Mounts (Recommended):**

If you need SpikeAgent to access your local data files, you should mount your data directories when running the script:

```bash
# Mount a single data directory
./run-spikeagent.sh /path/to/your/raw/data

# Mount multiple directories (e.g., raw data and results folder)
./run-spikeagent.sh /path/to/raw/data /path/to/processed/results

# Mount relative paths (automatically converted to absolute)
./run-spikeagent.sh ./data ./results
```

**Why mount volumes?**
- SpikeAgent needs access to your raw electrophysiology data files
- You may want to save processed results to a specific location
- Config files (YAML) and other data should be accessible to the container

**What paths should you mount?**
- **Raw data directory**: Where your experimental data files are stored (e.g., `.rhd`, SpikeGLX files, etc.)
- **Results/output directory**: Where you want processed data and results saved
- **Config directory**: If you have YAML configuration files (optional)

The script will:
- Pull the latest image from GitHub
- Mount your specified directories (if provided)
- Start the container
- Wait for the application to be ready
- Open your browser automatically

**Adding Volume Mounts After Startup:**

If you need to access a data path that wasn't mounted when you started the container:

```bash
# Add mounts to existing container (preserves existing mounts)
./run-spikeagent.sh --add /path/to/new/data

# You can add multiple paths at once
./run-spikeagent.sh --add /path/to/data1 /path/to/data2

# Or restart with new mounts only (replaces existing mounts)
./run-spikeagent.sh --restart /path/to/data
```

The `--add` option will:
- Stop the current container
- Preserve all existing volume mounts
- Add your new paths
- Restart the container

**Note:** Docker containers cannot mount new volumes at runtime - a restart is required. 

**Option B: Manual Docker commands:**

```bash
# Pull the latest CPU image
docker pull ghcr.io/spikeagent/spikeagent-cpu:latest

# Quick start (no data mounts)
# Runs the app, but it can’t access files on your computer unless you mount them.
docker run --rm -p 8501:8501 --env-file .env ghcr.io/spikeagent/spikeagent-cpu:latest

# With data mounts (recommended)
# Mount your local data/results folders so SpikeAgent can read inputs and save outputs on your machine.
# The `.env` file should be in the same directory where you run the Docker commands
docker run --rm -p 8501:8501 --env-file .env \
  -v /path/to/your/data:/path/to/your/data \
  -v /path/to/results:/path/to/results \
  ghcr.io/spikeagent/spikeagent-cpu:latest

Once the container is running, open your browser and go to:
http://localhost:8501
```

**GPU Version (Build Locally):**

The GPU version is not yet available as a pre-built package. You need to build it locally:

```bash
# Build the GPU image
docker build -f dockerfiles/Dockerfile.gpu -t spikeagent:gpu .

# Quick start (no data mounts)
# Runs the app, but it can’t access files on your computer unless you mount them.
docker run --rm --gpus all -p 8501:8501 --env-file .env spikeagent:gpu

# With data mounts (recommended)
# Mount your local data/results folders so SpikeAgent can read inputs and save outputs on your machine.
# The `.env` file should be in the same directory where you run the Docker commands
docker run --rm --gpus all -p 8501:8501 --env-file .env \
  -v /path/to/your/data:/path/to/your/data \
  -v /path/to/results:/path/to/results \
  spikeagent:gpu
```

**Troubleshooting:**

- **Port already in use?** Make sure port 8501 is free, or stop any existing containers: `docker stop spikeagent`
- **Can't pull image?** The image is public, so no authentication needed. If you have issues, make sure Docker is running.
- **ARM64/Apple Silicon (M1/M2/M3 Mac)?** If you get "no matching manifest for linux/arm64" error, the run script will automatically detect this and build the image locally for you. The first build may take 10-20 minutes. Once multi-arch images are available, this will no longer be necessary.
- **API connection errors?** Double-check your `.env` file has the correct API keys and is in the same directory as your Docker command.

## Open Source Neural Data

You can test SpikeAgent with open datasets such as [Neuropixels 2.0 chronic recordings in mice](https://doi.org/10.5522/04/24411841.v1) and [AutoSort flexible electrode recordings](https://github.com/LiuLab-Bioelectronics-Harvard/AutoSort).

## Tutorials

tutorials/VLM_curation_tutorial.ipynb: A programmatic example for users who want to use only the VLM curation and merge analysis modules of the agent.
Demonstrates how to classify units as "Good" or "Noise" using Vision-Language Models.
Shows how to identify and resolve oversplit units through AI-driven merge analysis.
Ideal for users who want to integrate SpikeAgent's AI curation directly into their existing Python workflows without using the full chat interface.

## Project Structure

```
spikeagent/
├── src/spikeagent/                      # Main source code package
│   ├── app/                            # Application code
│   └── curation/                       # Curation and VLM analysis tools
├── dockerfiles/                        # Docker configuration files
│   ├── Dockerfile.cpu                  # CPU Docker image
│   └── Dockerfile.gpu                  # GPU Docker image
├── docs/                               # Documentation
│   └── img/                            # Documentation images
├── tutorials/                         # Jupyter notebook tutorials
│   ├── vlm_curation_and_merging_tutorial.ipynb # VLM curation and merge analysis tutorial
└── tests/                              # Test suite
```

## Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

- **[Installation Guide](docs/installation.md)**: Detailed setup and installation instructions
- **[User Guide](docs/user-guide.md)**: How to use SpikeAgent for spike sorting and curation
- **[API Reference](docs/api-reference.md)**: Programmatic API documentation

## Getting Help

For detailed setup instructions, troubleshooting, and usage information:
- Check the [User Guide](docs/user-guide.md) for workflows
- Explore the Jupyter notebook tutorials in `tutorials/`
- Ensure your `.env` file contains the required API keys

## Citation

If you find SpikeAgent useful for your work, please cite:

**SpikeAgent**:
Lin, Z., Marin-Llobet, A., Baek, J., He, Y., Lee, J., Wang, W., ... & Liu, J. (2025). Spike sorting AI agent. Preprint at bioRxiv: https://doi.org/10.1101/2025.02.11.637754

**SpikeInterface**:
Buccino, A. P., Hurwitz, C. L., Garcia, S., Magland, J., Siegle, J. H., Hurwitz, R., & Hennig, M. H. (2020). SpikeInterface, a unified framework for spike sorting. Elife, 9, e61834.
