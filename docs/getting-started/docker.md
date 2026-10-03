# Docker

Docker is the easiest way to run SpikeAgent without managing all local Python and system dependencies.

## CPU Image

Create a `.env` file with at least one model-provider key, then run:

```bash
docker pull ghcr.io/spikeagent/spikeagent-cpu:latest
docker run --rm -p 8501:8501 --env-file .env ghcr.io/spikeagent/spikeagent-cpu:latest
```

Open:

```text
http://localhost:8501
```

## Mount Data

Mount local data and result directories so the container can read recordings and save outputs:

```bash
docker run --rm -p 8501:8501 --env-file .env \
  -v /path/to/raw/data:/path/to/raw/data \
  -v /path/to/results:/path/to/results \
  ghcr.io/spikeagent/spikeagent-cpu:latest
```

## Helper Script

The repository includes `run-spikeagent.sh`:

```bash
./run-spikeagent.sh /path/to/raw/data /path/to/results
```

The script can pull or build the image, start the container, mount provided paths, and open the app.

## GPU Image

For NVIDIA GPU workflows, build the GPU image locally:

```bash
docker build -f dockerfiles/Dockerfile.gpu -t spikeagent:gpu .
docker run --rm --gpus all -p 8501:8501 --env-file .env spikeagent:gpu
```
