#!/bin/bash

# Script to run SpikeAgent CPU Docker container and open browser automatically
# Uses the published image from GitHub Container Registry

set -e

IMAGE="ghcr.io/arnaumarin/spikeagent-cpu:latest"
URL="http://localhost:8501"
CONTAINER_NAME="spikeagent"
MAX_WAIT=60  # Maximum seconds to wait for app to be ready

echo "🚀 Starting SpikeAgent..."
echo "=========================================="
echo ""

# Step 1: Check prerequisites
echo "📋 Step 1: Checking prerequisites..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ ERROR: Docker is not running!"
    echo "   Please start Docker Desktop and try again."
    exit 1
fi
echo "   ✓ Docker is running"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found!"
    echo "   Please create a .env file with your API keys:"
    echo "   OPENAI_API_KEY=your_key_here"
    echo "   ANTHROPIC_API_KEY=your_key_here"
    echo "   GOOGLE_API_KEY=your_key_here"
    echo "   See README.md for instructions."
    exit 1
fi
echo "   ✓ .env file exists"
echo ""

# Step 2: Clean up any existing container and check port availability
echo "🧹 Step 2: Cleaning up any existing containers..."
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "   Stopping existing container..."
    docker stop ${CONTAINER_NAME} > /dev/null 2>&1 || true
    docker rm ${CONTAINER_NAME} > /dev/null 2>&1 || true
    echo "   ✓ Cleaned up"
else
    echo "   ✓ No existing containers"
fi

# Check if port 8501 is already in use
if docker ps --format '{{.Ports}}' | grep -q ':8501->'; then
    echo "   ⚠️  Port 8501 is already in use by another container"
    echo "   Stopping containers using port 8501..."
    docker ps --filter "publish=8501" --format '{{.Names}}' | xargs -r docker stop 2>/dev/null || true
    sleep 2
fi
echo ""

# Step 3: Pull the latest image
echo "📦 Step 3: Pulling latest Docker image from GitHub Container Registry..."
echo "   Image: ${IMAGE}"
docker pull "$IMAGE" || {
    echo "❌ Failed to pull image."
    echo "   If this is a private repository, make sure you're logged in:"
    echo "   echo YOUR_TOKEN | docker login ghcr.io -u arnaumarin --password-stdin"
    exit 1
}
echo "   ✓ Image pulled successfully"
echo ""

# Step 4: Show image info
echo "📊 Step 4: Image information:"
IMAGE_DIGEST=$(docker inspect ${IMAGE} --format='{{index .RepoDigests 0}}' 2>/dev/null || echo "N/A")
IMAGE_SIZE=$(docker images ${IMAGE} --format '{{.Size}}' | head -1)
echo "   Digest: ${IMAGE_DIGEST}"
echo "   Size: ${IMAGE_SIZE}"
echo ""

# Step 5: Run the container
echo "🐳 Step 5: Starting container..."
docker run --rm -d \
    -p 8501:8501 \
    --name ${CONTAINER_NAME} \
    --env-file .env \
    ${IMAGE}

if [ $? -eq 0 ]; then
    echo "   ✓ Container started successfully"
else
    echo "   ❌ Failed to start container"
    exit 1
fi
echo ""

# Step 6: Wait for application to be ready
echo "⏳ Step 6: Waiting for application to start..."
echo "   (This may take 10-30 seconds)"
sleep 3

# Check if container is still running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "   ❌ Container stopped unexpectedly!"
    echo "   Checking logs..."
    docker logs ${CONTAINER_NAME} 2>&1 | tail -20
    exit 1
fi

# Wait for health check with timeout
echo -n "   Waiting for application to be ready"
WAIT_COUNT=0
while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    if curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        echo ""
        echo "   ✓ Application is ready!"
        break
    fi
    echo -n "."
    sleep 2
    WAIT_COUNT=$((WAIT_COUNT + 2))
done

if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
    echo ""
    echo "   ⚠️  Application may still be starting (waited ${MAX_WAIT}s)"
    echo "   Check logs if issues persist: docker logs -f ${CONTAINER_NAME}"
else
    echo ""
fi
echo ""

# Step 7: Open browser
echo "🌐 Step 7: Opening browser..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "${URL}" 2>/dev/null && echo "   ✓ Browser opened"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "${URL}" 2>/dev/null || sensible-browser "${URL}" 2>/dev/null || echo "   Please open ${URL} manually"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash)
    start "${URL}" 2>/dev/null && echo "   ✓ Browser opened"
else
    echo "   Please open ${URL} in your browser"
fi
echo ""

# Final status
echo "✅ SpikeAgent is running!"
echo "=========================================="
echo ""
echo "📍 Access the application at: ${URL}"
echo ""
echo "📝 Useful commands:"
echo "   View logs:        docker logs -f ${CONTAINER_NAME}"
echo "   Stop container:   docker stop ${CONTAINER_NAME}"
echo "   Check status:     docker ps --filter name=${CONTAINER_NAME}"
echo "   View container:   docker inspect ${CONTAINER_NAME}"
echo ""
echo "🔗 Package information:"
echo "   https://github.com/arnaumarin/SpikeAgent/pkgs/container/spikeagent-cpu"
echo ""

