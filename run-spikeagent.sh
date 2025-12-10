#!/bin/bash

# Unified script to run SpikeAgent CPU Docker container
# Can start fresh or add mounts to existing container
# Uses the published image from GitHub Container Registry
#
# Usage:
#   ./run-spikeagent.sh [volume_path1] [volume_path2] ...
#   ./run-spikeagent.sh --add [volume_path1] [volume_path2] ...  # Add mounts to existing container
#   ./run-spikeagent.sh --restart [volume_path1] [volume_path2] ...  # Restart with new mounts
#
# Examples:
#   ./run-spikeagent.sh                                    # Start fresh without mounts
#   ./run-spikeagent.sh /path/to/data                     # Start fresh with mounts
#   ./run-spikeagent.sh --add /path/to/new/data           # Add mounts to existing container
#   ./run-spikeagent.sh --restart /path/to/data           # Restart with new mounts (replaces existing)
#
# Volume mounts:
#   Each path argument will be mounted as: -v {absolute_path}:{absolute_path}
#   This allows the container to access your local data directories.
#   Paths are automatically converted to absolute paths.

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
    echo "Usage: $0 [options] [volume_path1] [volume_path2] ..."
    echo ""
    echo "Options:"
    echo "  -h, --help       Show this help message"
    echo "  --add            Add mounts to existing container (preserves current mounts)"
    echo "  --restart        Restart container with new mounts (replaces existing mounts)"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Start fresh without volume mounts"
    echo "  $0 /path/to/data                     # Start fresh with mounts"
    echo "  $0 --add /path/to/new/data           # Add mounts to existing container"
    echo "  $0 --restart /path/to/data           # Restart with new mounts only"
    echo "  $0 /path/to/data1 /path/to/data2     # Mount multiple directories"
    echo ""
    echo "Volume mounts:"
    echo "  Each path argument will be mounted as: -v {absolute_path}:{absolute_path}"
    echo "  This allows the container to access your local data directories."
    echo "  Paths are automatically converted to absolute paths."
    exit 0
fi

# Parse options
MODE="fresh"  # fresh, add, or restart
PATHS=()

for arg in "$@"; do
    case "$arg" in
        --add)
            MODE="add"
            ;;
        --restart)
            MODE="restart"
            ;;
        -*)
            echo "⚠️  Unknown option: $arg"
            echo "   Use --help for usage information"
            exit 1
            ;;
        *)
            PATHS+=("$arg")
            ;;
    esac
done

# Function to parse and convert paths to volume mounts
parse_paths_to_mounts() {
    local paths=("$@")
    local mounts=()
    
    for path in "${paths[@]}"; do
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
        mounts+=("-v" "$abs_path:$abs_path")
    done
    
    echo "${mounts[@]}"
}

# Parse volume mount arguments
VOLUME_MOUNTS_STR=$(parse_paths_to_mounts "${PATHS[@]}")
read -ra VOLUME_MOUNTS <<< "$VOLUME_MOUNTS_STR"

# Check if container exists and determine mode
CONTAINER_EXISTS=false
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    CONTAINER_EXISTS=true
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        CONTAINER_RUNNING=true
    else
        CONTAINER_RUNNING=false
    fi
else
    CONTAINER_RUNNING=false
fi

# Auto-detect mode if not explicitly set
if [ "$MODE" == "fresh" ] && [ "$CONTAINER_EXISTS" == true ] && [ ${#PATHS[@]} -gt 0 ]; then
    if [ "$CONTAINER_RUNNING" == true ]; then
        echo "ℹ️  Container is already running."
        echo "   Use --add to add mounts to existing container, or --restart to replace mounts."
        echo "   Proceeding with --add mode..."
        MODE="add"
    fi
fi

if [ "$MODE" == "add" ] || [ "$MODE" == "restart" ]; then
    if [ "$CONTAINER_EXISTS" != true ]; then
        echo "❌ Container '${CONTAINER_NAME}' not found."
        echo "   Starting fresh instead..."
        MODE="fresh"
    elif [ ${#PATHS[@]} -eq 0 ]; then
        echo "❌ No paths provided for $MODE mode."
        echo "   Please provide at least one path to mount."
        exit 1
    fi
fi

if [ "$MODE" == "add" ] || [ "$MODE" == "restart" ]; then
    echo "🔄 Restarting SpikeAgent with additional mounts..."
    echo "=========================================="
    echo ""
    
    # Get existing volume mounts from the running container
    if [ "$MODE" == "add" ]; then
        echo "🔍 Checking existing volume mounts..."
        EXISTING_MOUNTS=()
        while IFS= read -r mount; do
            if [[ -n "$mount" ]]; then
                # Extract source path from mount (format: /host/path:/container/path)
                source_path=$(echo "$mount" | cut -d':' -f1)
                if [[ "$source_path" == /* ]]; then
                    EXISTING_MOUNTS+=("$mount")
                fi
            fi
        done < <(docker inspect ${CONTAINER_NAME} --format='{{range .Mounts}}{{.Source}}:{{.Destination}} {{end}}' 2>/dev/null || true)
        
        # Combine existing and new mounts
        ALL_MOUNTS=()
        for mount in "${EXISTING_MOUNTS[@]}"; do
            source_path=$(echo "$mount" | cut -d':' -f1)
            dest_path=$(echo "$mount" | cut -d':' -f2)
            ALL_MOUNTS+=("-v" "$source_path:$dest_path")
        done
        ALL_MOUNTS+=("${VOLUME_MOUNTS[@]}")
        
        echo "   Existing mounts: ${#EXISTING_MOUNTS[@]}"
        echo "   New mounts: ${#PATHS[@]}"
        echo ""
        
        # Get the image name from the current container
        IMAGE=$(docker inspect ${CONTAINER_NAME} --format='{{.Config.Image}}' 2>/dev/null || echo "ghcr.io/arnaumarin/spikeagent-cpu:latest")
        
        # Stop and remove existing container
        echo "🛑 Stopping existing container..."
        docker stop ${CONTAINER_NAME} > /dev/null 2>&1 || true
        docker rm ${CONTAINER_NAME} > /dev/null 2>&1 || true
        
        # Start new container with all mounts
        echo "🚀 Starting container with all mounts..."
        if [ ${#ALL_MOUNTS[@]} -gt 0 ]; then
            echo "   Mounting volumes:"
            for ((i=0; i<${#ALL_MOUNTS[@]}; i+=2)); do
                echo "     - ${ALL_MOUNTS[i+1]}"
            done
        fi
        
        if ! docker run --rm -d \
            -p 8501:8501 \
            --name ${CONTAINER_NAME} \
            --env-file .env \
            "${ALL_MOUNTS[@]}" \
            ${IMAGE} > /dev/null 2>&1; then
            echo "   ❌ Failed to start container"
            exit 1
        fi
        
        echo "   ✓ Container restarted successfully!"
        echo ""
        echo "📍 Access the application at: ${URL}"
        echo ""
        echo "📝 Useful commands:"
        echo "   View logs:        docker logs -f ${CONTAINER_NAME}"
        echo "   Stop container:   docker stop ${CONTAINER_NAME}"
        echo ""
        exit 0
    else
        # --restart mode: replace all mounts
        echo "🔄 Restarting with new mounts (replacing existing)..."
        echo "   New mounts: ${#PATHS[@]}"
        echo ""
        
        # Get the image name from the current container
        IMAGE=$(docker inspect ${CONTAINER_NAME} --format='{{.Config.Image}}' 2>/dev/null || echo "ghcr.io/arnaumarin/spikeagent-cpu:latest")
        
        # Stop and remove existing container
        echo "🛑 Stopping existing container..."
        docker stop ${CONTAINER_NAME} > /dev/null 2>&1 || true
        docker rm ${CONTAINER_NAME} > /dev/null 2>&1 || true
        
        # Continue with fresh start flow below (MODE is already "fresh" from earlier)
    fi
fi

# Fresh start mode (default or after --restart)
if [ "$MODE" == "fresh" ]; then

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
        if [ ! -f "dockerfiles/Dockerfile.cpu" ]; then
            echo "   ❌ Dockerfile not found at dockerfiles/Dockerfile.cpu"
            echo "   Please ensure you're in the repository root directory."
            exit 1
        fi
        
        # Build locally
        echo "   🔨 Building Docker image locally (this may take 10-20 minutes)..."
        docker build -f dockerfiles/Dockerfile.cpu -t ${IMAGE} . || {
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
fi  # End of fresh start mode

