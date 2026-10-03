# API Keys

SpikeAgent loads model-provider credentials from environment variables. For local development, place them in a `.env` file in the directory where you run SpikeAgent.

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

You need at least one supported provider key for the interactive app. VLM curation currently expects OpenAI-compatible vision access.

## Custom OpenAI-Compatible Endpoint

If your lab or institution provides an OpenAI-compatible endpoint, set both:

```bash
OPENAI_API_KEY=your-institution-key
OPENAI_API_BASE=https://your-institution-endpoint.example/v1
```

## Safety

Never commit `.env` files, API keys, raw recordings, generated model outputs, or large analyzer artifacts.
