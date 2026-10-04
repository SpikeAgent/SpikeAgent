# API Keys

SpikeAgent reads model-provider credentials from environment variables. The interactive app loads a local `.env` file. For local development, place it in the directory where you run SpikeAgent.

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

You need a key for the provider selected in the interactive app. The VLM examples use OpenAI vision models and require `OPENAI_API_KEY`.

For Python scripts or notebooks, load `.env` explicitly before calling `get_model`:

```python
from dotenv import load_dotenv

load_dotenv()
```

The VLM APIs accept a supplied model wrapper. It must support image inputs and
structured output; compatibility depends on the selected model and provider.

## Custom OpenAI-Compatible Endpoint

If your lab or institution provides an OpenAI-compatible endpoint, set both:

```bash
OPENAI_API_KEY=your-institution-key
OPENAI_API_BASE=https://your-institution-endpoint.example/v1
```

## Safety

Never commit `.env` files, API keys, raw recordings, generated model outputs, or large analyzer artifacts.
