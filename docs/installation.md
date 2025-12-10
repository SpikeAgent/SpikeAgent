# Installation Guide

This guide provides detailed instructions for installing and setting up SpikeAgent.

## Prerequisites

Before installing SpikeAgent, ensure you have:

- **Docker Desktop** installed and running
  - Download from: https://www.docker.com/products/docker-desktop/
  - Verify installation: `docker --version`
  
- **API Keys** for at least one AI provider:
  - [OpenAI API Key](https://platform.openai.com/api-keys)
  - [Anthropic API Key](https://console.anthropic.com/)
  - [Google API Key](https://makersuite.google.com/app/apikey)

- **For GPU version**: NVIDIA GPU with CUDA support
  - Verify GPU: `nvidia-smi`
  - CUDA drivers installed

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/spikeagent.git
cd spikeagent
```

### 2. Create Environment File

Create a `.env` file in the project root with your API keys:

```bash
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
```

**Important**: 
- Replace the placeholder values with your actual API keys
- No spaces around the `=` sign
- No quotes needed around the keys
- Keep this file secure and never commit it to version control

### 3. Build Docker Image

Choose the appropriate version for your system:

#### CPU Version

```bash
docker build -f dockerfiles/Dockerfile.cpu -t spikeagent:cpu .
```

#### GPU Version

```bash
docker build -f dockerfiles/Dockerfile.gpu -t spikeagent:gpu .
```

**Note**: The first build may take 10-20 minutes as it downloads and installs all dependencies.

### 4. Run the Container

#### CPU Version

```bash
docker run --rm -p 8501:8501 --env-file .env spikeagent:cpu
```

#### GPU Version

```bash
docker run --rm --gpus all -p 8501:8501 --env-file .env spikeagent:gpu
```

### 5. Access the Application

Open your web browser and navigate to:

```
http://localhost:8501
```

The SpikeAgent interface should load in your browser.

## Verification

To verify the installation is working:

1. The Docker container should start without errors
2. You should see Streamlit startup messages in the terminal
3. The web interface should load at `http://localhost:8501`
4. You should be able to select an AI provider in the sidebar

## Troubleshooting

### Docker Issues

- **Docker not running**: Ensure Docker Desktop is started
- **Port already in use**: Change the port mapping: `-p 8502:8501`
- **Permission denied**: On Linux, you may need to add your user to the docker group

### GPU Issues

- **CUDA not detected**: Verify NVIDIA drivers: `nvidia-smi`
- **GPU not accessible**: Use `--gpus all` flag in docker run command
- **CUDA version mismatch**: Check that your CUDA version matches the Docker image requirements

### API Key Issues

- **Authentication errors**: Verify your API keys are correct in the `.env` file
- **Rate limiting**: Check your API provider's rate limits and usage

## Next Steps

After successful installation:

1. Read the [User Guide](user-guide.md) to learn how to use SpikeAgent
2. Try the [Jupyter notebook tutorials](../tutorials/) for hands-on examples
3. Explore the [API Reference](api-reference.md) for detailed function documentation

## Uninstallation

To remove SpikeAgent:

```bash
# Stop running containers
docker ps -a | grep spikeagent | awk '{print $1}' | xargs docker rm -f

# Remove Docker images
docker rmi spikeagent:cpu spikeagent:gpu
```

