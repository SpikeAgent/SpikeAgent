#!/bin/bash

# Script to run SpikeAgent CPU Docker container and open browser automatically
# Uses the published image from GitHub Container Registry
#
# Usage:
#   ./run-spikeagent.sh [volume_path1] [volume_path2] ...
#
# Examples:
#   ./run-spikeagent.sh
#   ./run-spikeagent.sh /path/to/data
#   ./run-spikeagent.sh /path/to/data1 /path/to/data2 /path/to/results
#
# Volume mounts:
#   Each argument will be mounted as: -v {path}:{path}
#   This allows the container to access your local data directories

set -e

IMAGE="ghcr.io/arnaumarin/spikeagent-cpu:latest"
URL="http://localhost:8501"
CONTAINER_NAME="spikeagent"
MAX_WAIT=60  # Maximum seconds to wait for app to be ready

# Function to kill processes on port 8501
kill_port_8501() {
    if command -v lsof > /dev/null 2>&1; then
        PIDS=$(lsof -ti:8501 2>/dev/null || true)
        if [ -n "$PIDS" ]; then
            echo "$PIDS" | xargs kill -9 2>/dev/null || true
            sleep 1
            return 0
        fi
    fi
    return 1
}

# Check for help flag
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Usage: $0 [volume_path1] [volume_path2] ..."
    echo ""
    echo "Options:"
    echo "  -h, --help    Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run without volume mounts"
    echo "  $0 /path/to/data                     # Mount a single directory"
    echo "  $0 /path/to/data1 /path/to/data2     # Mount multiple directories"
    echo "  $0 ./data ./results                  # Mount relative paths"
    echo ""
    echo "Volume mounts:"
    echo "  Each path argument will be mounted as: -v {absolute_path}:{absolute_path}"
    echo "  This allows the container to access your local data directories."
    echo "  Paths are automatically converted to absolute paths."
    exit 0
fi

# Parse volume mount arguments
VOLUME_MOUNTS=()
for path in "$@"; do
    # Check if path exists (warn if it doesn't, but still add it)
    if [ ! -e "$path" ]; then
        echo "⚠️  Warning: Path does not exist: $path"
        echo "   It will still be mounted, but may not be accessible."
    fi
    # Convert to absolute path
    if [[ "$path" = /* ]]; then
        # Already absolute path
        abs_path="$path"
    else
        # Relative path - convert to absolute
        abs_path="$(cd "$(dirname "$path")" 2>/dev/null && pwd)/$(basename "$path")" || abs_path="$(pwd)/$path"
    fi
    VOLUME_MOUNTS+=("-v" "$abs_path:$abs_path")
done

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
echo "🧹 Step 2: Cleaning up any existing containers and checking port availability..."

# Stop and remove any existing spikeagent containers
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "   Stopping existing ${CONTAINER_NAME} container..."
    docker stop ${CONTAINER_NAME} > /dev/null 2>&1 || true
    docker rm ${CONTAINER_NAME} > /dev/null 2>&1 || true
    echo "   ✓ Cleaned up ${CONTAINER_NAME}"
fi

# Stop ALL containers using port 8501 (not just spikeagent)
CONTAINERS_ON_PORT=$(docker ps --filter "publish=8501" --format '{{.Names}}' 2>/dev/null || true)
if [ -n "$CONTAINERS_ON_PORT" ]; then
    echo "   ⚠️  Found containers using port 8501:"
    echo "$CONTAINERS_ON_PORT" | while read -r container; do
        if [ -n "$container" ]; then
            echo "     - Stopping $container..."
            docker stop "$container" > /dev/null 2>&1 || true
            docker rm "$container" > /dev/null 2>&1 || true
        fi
    done
    sleep 2
fi

# Check if port 8501 is still in use by a non-Docker process
PORT_IN_USE=false
if command -v lsof > /dev/null 2>&1; then
    # macOS/Linux: Check if port is in use
    if lsof -ti:8501 > /dev/null 2>&1; then
        PORT_IN_USE=true
        PROCESS_INFO=$(lsof -ti:8501 | head -1)
        echo "   ⚠️  Port 8501 is in use by a local process (PID: $PROCESS_INFO)"
        echo "   Attempting to identify the process..."
        lsof -i:8501 2>/dev/null | head -2 || true
    fi
elif command -v netstat > /dev/null 2>&1; then
    # Alternative: Use netstat (Linux)
    if netstat -tuln 2>/dev/null | grep -q ':8501 '; then
        PORT_IN_USE=true
        echo "   ⚠️  Port 8501 appears to be in use (check with: netstat -tuln | grep 8501)"
    fi
fi

if [ "$PORT_IN_USE" = true ]; then
    echo ""
    echo "   ⚠️  Port 8501 is in use. Attempting to free it..."
    if kill_port_8501; then
        echo "   ✓ Port 8501 freed successfully"
        sleep 1
    else
        echo ""
        echo "   ❌ Could not automatically free port 8501!"
        echo "   Please stop the process using port 8501 manually, or use a different port."
        echo ""
        echo "   To find and kill the process:"
        if command -v lsof > /dev/null 2>&1; then
            echo "     lsof -ti:8501 | xargs kill -9"
        else
            echo "     Find the process ID and kill it manually"
        fi
        exit 1
    fi
fi

echo "   ✓ Port 8501 is available"
echo ""

# Step 3: Pull the latest image
echo "📦 Step 3: Pulling latest Docker image from GitHub Container Registry..."
echo "   Image: ${IMAGE}"

# Detect architecture
ARCH=$(uname -m)
IS_ARM64=false
if [[ "$ARCH" == "arm64" ]] || [[ "$ARCH" == "aarch64" ]]; then
    IS_ARM64=true
fi

# Try to pull the image
if docker pull "$IMAGE" 2>&1 | grep -q "no matching manifest"; then
    echo "   ⚠️  No ARM64 image available yet"
    if [ "$IS_ARM64" = true ]; then
        echo ""
        echo "   💡 Detected ARM64 architecture (Apple Silicon)"
        echo "   The pre-built image doesn't support ARM64 yet."
        echo "   Building locally instead..."
        echo ""
        
        # Check if Dockerfile exists
        if [ ! -f "docker_files/Dockerfile.cpu" ]; then
            echo "   ❌ Dockerfile not found at docker_files/Dockerfile.cpu"
            echo "   Please ensure you're in the repository root directory."
            exit 1
        fi
        
        # Build locally
        echo "   🔨 Building Docker image locally (this may take 10-20 minutes)..."
        docker build -f docker_files/Dockerfile.cpu -t ${IMAGE} . || {
            echo "   ❌ Failed to build image locally"
            echo "   Please check the error messages above."
            exit 1
        }
        echo "   ✓ Image built successfully"
    else
        echo "   ❌ Failed to pull image."
        echo "   If this is a private repository, make sure you're logged in:"
        echo "   echo YOUR_TOKEN | docker login ghcr.io -u arnaumarin --password-stdin"
        exit 1
    fi
else
    echo "   ✓ Image pulled successfully"
fi
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

# Final port check before starting
if command -v lsof > /dev/null 2>&1; then
    if lsof -ti:8501 > /dev/null 2>&1; then
        echo "   ⚠️  Port 8501 is still in use! Attempting to free it..."
        if kill_port_8501; then
            echo "   ✓ Port 8501 freed"
        else
            echo "   ❌ Could not free port 8501"
            exit 1
        fi
    fi
fi

# Clean up any leftover containers with the same name (in case of previous failed start)
docker rm -f ${CONTAINER_NAME} > /dev/null 2>&1 || true

if [ ${#VOLUME_MOUNTS[@]} -gt 0 ]; then
    echo "   Mounting volumes:"
    for ((i=0; i<${#VOLUME_MOUNTS[@]}; i+=2)); do
        echo "     - ${VOLUME_MOUNTS[i+1]}"
    done
    if ! docker run --rm -d \
        -p 8501:8501 \
        --name ${CONTAINER_NAME} \
        --env-file .env \
        "${VOLUME_MOUNTS[@]}" \
        ${IMAGE} > /dev/null 2>&1; then
        echo "   ❌ Failed to start container"
        echo "   Checking for port conflicts..."
        if command -v lsof > /dev/null 2>&1; then
            lsof -i:8501 2>/dev/null || true
        fi
        # Clean up on failure
        docker rm -f ${CONTAINER_NAME} > /dev/null 2>&1 || true
        exit 1
    fi
    echo "   ✓ Container started successfully"
else
    if ! docker run --rm -d \
        -p 8501:8501 \
        --name ${CONTAINER_NAME} \
        --env-file .env \
        ${IMAGE} > /dev/null 2>&1; then
        echo "   ❌ Failed to start container"
        echo "   Checking for port conflicts..."
        if command -v lsof > /dev/null 2>&1; then
            lsof -i:8501 2>/dev/null || true
        fi
        # Clean up on failure
        docker rm -f ${CONTAINER_NAME} > /dev/null 2>&1 || true
        exit 1
    fi
    echo "   ✓ Container started successfully"
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
if [ ${#VOLUME_MOUNTS[@]} -gt 0 ]; then
    echo "📁 Mounted volumes:"
    for ((i=0; i<${#VOLUME_MOUNTS[@]}; i+=2)); do
        echo "   ${VOLUME_MOUNTS[i+1]}"
    done
    echo ""
fi
echo "🔗 Package information:"
echo "   https://github.com/arnaumarin/SpikeAgent/pkgs/container/spikeagent-cpu"
echo ""

