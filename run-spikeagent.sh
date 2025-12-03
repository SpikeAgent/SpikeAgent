#!/bin/bash

# Script to run SpikeAgent CPU Docker container and open browser automatically

set -e

IMAGE="ghcr.io/arnaumarin/spikeagent-cpu:latest"
URL="http://localhost:8501"

echo "🚀 Starting SpikeAgent..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your API keys first."
    echo "See README.md for instructions."
    exit 1
fi

# Pull the latest image from GitHub Container Registry
echo "📦 Pulling Docker image from GitHub Container Registry..."
docker pull "$IMAGE" || {
    echo "❌ Failed to pull image. Make sure you're logged in to GitHub Container Registry."
    echo "You can login with: echo YOUR_TOKEN | docker login ghcr.io -u USERNAME --password-stdin"
    exit 1
}
echo "✓ Image pulled successfully"

# Run container in background
echo "🐳 Starting container..."
docker run --rm -d -p 8501:8501 --name spikeagent --env-file .env "$IMAGE"

# Wait for container to be ready
echo "⏳ Waiting for application to start..."
sleep 5

# Check if container is running
if ! docker ps | grep -q spikeagent; then
    echo "❌ Container failed to start. Check logs with: docker logs spikeagent"
    exit 1
fi

# Open browser
echo "🌐 Opening browser..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "$URL"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "$URL" 2>/dev/null || sensible-browser "$URL" 2>/dev/null || echo "Please open $URL in your browser"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash)
    start "$URL"
else
    echo "Please open $URL in your browser"
fi

echo ""
echo " SpikeAgent is running!"
echo " Access it at: $URL"
echo ""
echo "To stop the container, run: docker stop spikeagent"
echo "To view logs, run: docker logs -f spikeagent"

