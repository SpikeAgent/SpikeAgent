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
    has_harvard_openai = bool(os.getenv("OPENAI_API_BASE"))
    openai_base_url = os.getenv("OPENAI_API_BASE")
    
    # OpenAI models - only create when requested
    if model_name in ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "o1", "gpt-4-turbo", "gpt-3.5-turbo"]:
        # Use Harvard base URL if available, otherwise use default OpenAI endpoint
        base_url = openai_base_url if has_harvard_openai and openai_base_url else None
        
        if model_name == "gpt-4o":
            kwargs = {"model_name": "gpt-4o", "temperature": temperature}
            if base_url:
                kwargs["base_url"] = base_url
            return ChatOpenAI(**kwargs)
        elif model_name == "gpt-4o-mini":
            kwargs = {"model_name": "gpt-4o-mini", "temperature": temperature}
            if base_url:
                kwargs["base_url"] = base_url
            return ChatOpenAI(**kwargs)
        elif model_name == "gpt-4.1":
            kwargs = {"model_name": "gpt-4.1", "temperature": temperature}
            if base_url:
                kwargs["base_url"] = base_url
            return ChatOpenAI(**kwargs)
        elif model_name == "o1":
            kwargs = {"model_name": "o1"}
            if base_url:
                kwargs["base_url"] = base_url
            return ChatOpenAI(**kwargs)
        elif model_name == "gpt-4-turbo":
            kwargs = {"model_name": "gpt-4-turbo", "temperature": temperature}
            if base_url:
                kwargs["base_url"] = base_url
            return ChatOpenAI(**kwargs)
        elif model_name == "gpt-3.5-turbo":
            kwargs = {"model_name": "gpt-3.5-turbo", "temperature": temperature}
            if base_url:
                kwargs["base_url"] = base_url
            return ChatOpenAI(**kwargs)
    
    # Anthropic models - use Harvard endpoint if available, otherwise use standard Anthropic API
    if model_name in ['claude_4_sonnet', 'claude_4_opus', 'claude_3_7_sonnet', 'claude_3_5_sonnet', 'claude_3_opus', 'claude_3_haiku', 'claude_3_sonnet']:
        if has_harvard_anthropic:
            if model_name == 'claude_4_sonnet':
                return ChatAnthropic_H(model='claude-sonnet-4-20250514-v1', temperature=temperature)
            elif model_name == 'claude_4_opus':
                return ChatAnthropic_H(model='claude-opus-4-20250514-v1', temperature=temperature)
            elif model_name == 'claude_3_7_sonnet':
                return ChatAnthropic_H(model='claude-3-7-sonnet-20250219-v1', temperature=temperature)
            elif model_name == 'claude_3_5_sonnet':
                return ChatAnthropic_H(model_name="claude-3-5-sonnet-20240620-v1", temperature=temperature)
            elif model_name == 'claude_3_opus':
                return ChatAnthropic_H(model_name="claude-3-opus-20240229-v1", temperature=temperature)
            elif model_name == 'claude_3_haiku':
                return ChatAnthropic_H(model_name="claude-3-haiku-20240307-v1", temperature=temperature)
            elif model_name == 'claude_3_sonnet':
                return ChatAnthropic_H(model_name="claude-3-sonnet-20240229-v1", temperature=temperature)
        else:
            # Use standard Anthropic API with ANTHROPIC_API_KEY
            if model_name == 'claude_4_sonnet':
                return ChatAnthropic(model='claude-sonnet-4-20250514', temperature=temperature)
            elif model_name == 'claude_4_opus':
                return ChatAnthropic(model='claude-opus-4-20250514', temperature=temperature)
            elif model_name == 'claude_3_7_sonnet':
                return ChatAnthropic(model='claude-3-7-sonnet-20250219', temperature=temperature)
            elif model_name == 'claude_3_5_sonnet':
                return ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=temperature)
            elif model_name == 'claude_3_opus':
                return ChatAnthropic(model="claude-3-opus-20240229", temperature=temperature)
            elif model_name == 'claude_3_haiku':
                return ChatAnthropic(model="claude-3-haiku-20240307", temperature=temperature)
            elif model_name == 'claude_3_sonnet':
                return ChatAnthropic(model="claude-3-sonnet-20240229", temperature=temperature)
    
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
            return ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=temperature)
    elif model_name == "gemini-2.0-flash-exp":
        return ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=temperature)
    elif model_name == "gemini-1.5-flash":
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=temperature)
    elif model_name == "gemini-1.5-flash-8b":
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash-8b", temperature=temperature)
    elif model_name == "gemini-1.5-pro":
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=temperature)
    
    raise ValueError(f"Unknown model name: {model_name}")
