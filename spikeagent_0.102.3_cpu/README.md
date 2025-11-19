# Spike Agent

A web-based AI assistant for spike sorting and neural data analysis, powered by OpenAI, Anthropic, and Google's Gemini models.

## What You Need

- **Docker Desktop** installed on your computer
  - Download from: https://www.docker.com/products/docker-desktop/
  - Make sure Docker Desktop is running before you start

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
docker build -t spikeagent:latest .
```

This will take several minutes the first time. You'll see lots of text scrolling - that's normal! Just wait until it says "Successfully built" or "DONE".

### Step 4: Run the Application

Once the build is complete, run:

```bash
docker run --rm -p 8501:8501 --env-file .env spikeagent:latest
```

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

