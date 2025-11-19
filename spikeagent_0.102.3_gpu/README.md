# Spike Agent

A web-based AI assistant for spike sorting and neural data analysis, powered by OpenAI, Anthropic, and Google's Gemini models.

## About

**Authors:** Arnau Marin-Llobet / Zuwan Lin  
**Contact:** spikeaiagent@gmail.com  
**Version:** 0.102.3  
**License:** [Add your license here if applicable]

## What You Need

- **Docker Desktop** installed on your computer
  - Download from: https://www.docker.com/products/docker-desktop/
  - Make sure Docker Desktop is running before you start
- **NVIDIA GPU** with CUDA support (for GPU acceleration)
  - Requires NVIDIA drivers installed on your system
  - Docker Desktop must have GPU support enabled (Settings > Resources > WSL Integration or Settings > Resources > Advanced > GPU)
  - For Linux: Install nvidia-container-toolkit

## Quick Start

### Step 1: Get Your API Keys

You'll need at least one API key to use the application:

- **Anthropic API Key**
  - Get it from: https://console.anthropic.com/
- **OpenAI API Key**
  - Get it from: https://platform.openai.com/api-keys
- **Google API Key** 
  - Get it from: https://makersuite.google.com/app/apikey

### Step 2: Create a .env File

1. In the project folder, create a file named `.env` (just `.env` with no other name)
2. Open it in a text editor
3. Add your API keys like this (one per line, no spaces around the `=` sign):

```
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
```

**Important:** 
- Replace `your_XXX_key_here` with your actual API key
- No spaces before or after the `=` sign
- No quotes needed around the key

### Step 3: Build the Docker Image

Open a terminal (or command prompt) in the project folder and run:

```bash
cd /path/to/Spikeagent_0.102.3
```



This will take several minutes the first time. You'll see lots of text scrolling - that's normal! Just wait until it says "Successfully built" or "DONE".

### Step 4: Run the Application

Once the build is complete, run with GPU support:

**For Linux:**
```bash
docker run --rm --gpus all -p 8501:8501 --env-file .env spikeagent:latest
```

**For Windows/Mac with Docker Desktop:**
```bash
docker run --rm --gpus all -p 8501:8501 --env-file .env spikeagent:latest
```

**Note:** If you don't have a GPU or want to run on CPU only, you can remove the `--gpus all` flag, but some features may be slower or unavailable.

You should see a message like:
```
You can now view your Streamlit app in your browser.
URL: http://0.0.0.0:8501
```

### Step 5: Open in Your Browser

1. Open your web browser (Chrome, Firefox, Safari, etc.)
2. Go to: **http://localhost:8501**
3. The application should load!

## Using the Application

1. **Select a Provider**: In the left sidebar, choose OpenAI, Anthropic, or Gemini
2. **Select a Model**: Pick which AI model you want to use
3. **Start Chatting**: Type your question or request in the chat box at the bottom
4. **View Results**: The AI's response will appear in the chat area

## Stopping the Application

To stop the application:
1. Go back to your terminal
2. Press `Ctrl + C` (or `Cmd + C` on Mac)
3. The application will stop

## Troubleshooting

### "Port is already allocated" Error

This means the application is already running. To fix:

1. Stop any running containers:
   ```bash
   docker stop $(docker ps -q)
   ```
2. Try running again

### "Cannot connect" or "Connection refused"

1. Make sure Docker Desktop is running
2. Check that the container is running:
   ```bash
   docker ps
   ```
3. If you see a container with `spikeagent:latest`, it's running
4. Try refreshing your browser

### "API key not found" Error

1. Make sure your `.env` file exists in the project folder
2. Check that your API keys are correct (no extra spaces, no quotes)
3. Make sure you're using `--env-file .env` when running docker

### Application Won't Start

1. Make sure you built the image first (Step 3)
2. Check that Docker Desktop is running
3. Try rebuilding:
   ```bash
   docker build -t spikeagent:latest .
   ```

### GPU Not Detected

If you're having GPU issues:

1. **Verify NVIDIA drivers are installed:**
   ```bash
   nvidia-smi
   ```
   This should show your GPU information. If it doesn't work, install NVIDIA drivers first.

2. **For Linux, install nvidia-container-toolkit:**
   ```bash
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
   sudo systemctl restart docker
   ```

3. **For Docker Desktop (Windows/Mac):**
   - Go to Settings > Resources > WSL Integration (if using WSL2)
   - Or Settings > Resources > Advanced > GPU
   - Enable GPU support and restart Docker Desktop

4. **Test GPU access in container:**
   ```bash
   docker run --rm --gpus all nvidia/cuda:12.8.0-runtime-ubuntu22.04 nvidia-smi
   ```
   This should display GPU information. If it works, your GPU setup is correct.

## Need Help?

If you're stuck:
1. Check that Docker Desktop is running
2. Make sure your `.env` file is in the correct location (same folder as the Dockerfile)
3. Verify your API keys are correct
4. Try stopping and restarting Docker Desktop

## What's Next?

Once the application is running, you can:
- Ask questions about spike sorting in the Github page or Discord server
- Analyze neural data
- Get help with your research
- Explore different AI models

Enjoy using Spike Agent!

