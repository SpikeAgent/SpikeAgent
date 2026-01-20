from .custom_class import ChatAnthropic_H
from .custom_class_gemini import ChatGoogleGenerativeAI_H
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
import os

def get_model(model_name, temperature=0):
    # Check for Harvard API keys - use Harvard endpoints if available, otherwise use standard APIs
    has_harvard_anthropic = bool(os.getenv("HARVARD_API_KEY"))
    has_harvard_google = bool(os.getenv("HARVARD_API_KEY_GOOGLE")) and bool(os.getenv("GOOGLE_BASE_URL_HARVARD"))
    
    # Prepare OpenAI kwargs - explicitly pass api_key and base_url if available
    openai_base_url = os.getenv("OPENAI_API_BASE")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_kwargs = {}
    if openai_base_url:
        openai_kwargs["base_url"] = openai_base_url
    if openai_api_key:
        openai_kwargs["api_key"] = openai_api_key
    
    # OpenAI models - only create when requested
    if model_name in ["gpt-4o", "gpt-4.1"]:
        # Check if OpenAI API key is available
        if not openai_api_key:
            raise ValueError("API key required for OpenAI API. Provide api_key parameter or set OPENAI_API_KEY environment variable.")
        
        if model_name == "gpt-4o":
            return ChatOpenAI(model="gpt-4o", temperature=temperature, **openai_kwargs)
        elif model_name == "gpt-4.1":
            return ChatOpenAI(model="gpt-4.1", temperature=temperature, **openai_kwargs)
    
    # Anthropic models - use Harvard endpoint if available, otherwise use standard Anthropic API
    if model_name in ['claude_4_sonnet', 'claude_4_opus', 'claude_3_7_sonnet']:
        if has_harvard_anthropic:
            if model_name == 'claude_4_sonnet':
                return ChatAnthropic_H(model='claude-sonnet-4-20250514-v1', temperature=temperature)
            elif model_name == 'claude_4_opus':
                return ChatAnthropic_H(model='claude-opus-4-20250514-v1', temperature=temperature)
            elif model_name == 'claude_3_7_sonnet':
                return ChatAnthropic_H(model='claude-3-7-sonnet-20250219-v1', temperature=temperature)
        else:
            # Use standard Anthropic API with ANTHROPIC_API_KEY
            anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            if not anthropic_api_key:
                raise ValueError("API key required for Anthropic API. Provide api_key parameter or set ANTHROPIC_API_KEY environment variable.")
            
            if model_name == 'claude_4_sonnet':
                return ChatAnthropic(model='claude-sonnet-4-20250514', temperature=temperature, api_key=anthropic_api_key)
            elif model_name == 'claude_4_opus':
                return ChatAnthropic(model='claude-opus-4-20250514', temperature=temperature, api_key=anthropic_api_key)
            elif model_name == 'claude_3_7_sonnet':
                return ChatAnthropic(model='claude-3-7-sonnet-20250219', temperature=temperature, api_key=anthropic_api_key)
    
    # Google/Gemini models
    if model_name == "gemini-2.5-pro":
        if has_harvard_google:
            return ChatGoogleGenerativeAI_H(
                model="gemini-2.5-pro",
                temperature=temperature,
                client_options={"api_endpoint": os.getenv("GOOGLE_BASE_URL_HARVARD")},
                google_api_key=os.getenv("HARVARD_API_KEY_GOOGLE"),
                thinking_budget=200
            )
        else:
            # Check if Google API key is available
            google_api_key = os.getenv("GOOGLE_API_KEY")
            if not google_api_key:
                raise ValueError("API key required for Gemini Developer API. Provide api_key parameter or set GOOGLE_API_KEY/GEMINI_API_KEY environment variable.")
            return ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=temperature, google_api_key=google_api_key)
    
    raise ValueError(f"Unknown model name: {model_name}")
