# Model Utilities

## Model Selection

::: spikeagent.app.tool.utils.llm_model.get_model

## Supported Providers

`get_model` creates chat model wrappers for supported OpenAI, Anthropic, and Google Gemini model names. Configure credentials through environment variables or a local `.env` file.

Python scripts and notebooks must load `.env` explicitly, for example with
`dotenv.load_dotenv()`, before calling `get_model`.
