"""
llm_factory.py
--------------
PURPOSE: Single place that creates the LangChain LLM object.
         Implements a fallback mechanism to ensure reliability.
"""

import os
from typing import List, Optional

from langchain_core.language_models import BaseChatModel
from pydantic import SecretStr

from config import Config


def _get_gemini(temperature: float) -> Optional[BaseChatModel]:
    """Internal helper to create a Gemini model."""
    if not Config.GOOGLE_API_KEY:
        return None
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=Config.GEMINI_MODEL,
        google_api_key=SecretStr(Config.GOOGLE_API_KEY),
        temperature=temperature,
        convert_system_message_to_human=False,
    )


def _get_openai(temperature: float) -> Optional[BaseChatModel]:
    """Internal helper to create an OpenAI-compatible model."""
    if not Config.OPENAI_API_KEY:
        return None
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=Config.OPENAI_MODEL,
        api_key=SecretStr(Config.OPENAI_API_KEY),
        base_url=Config.OPENAI_BASE_URL,
        temperature=temperature,
        default_headers={
            "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "aiagent-rag",
        },
    )


def _get_groq(temperature: float) -> Optional[BaseChatModel]:
    """Internal helper to create a Groq model using OpenAI compatibility."""
    if not Config.GROQ_API_KEY:
        return None

    # We use ChatOpenAI instead of ChatGroq because the langchain-groq SDK
    # currently has a known bug where it allows Llama 3 models to hallucinate
    # <function> tags instead of forcing JSON schema validation.
    # Because Groq's API is OpenAI-compatible, using the OpenAI SDK provides
    # much more stable tool-calling serialization.
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=Config.GROQ_MODEL,
        api_key=SecretStr(Config.GROQ_API_KEY),
        base_url="https://api.groq.com/openai/v1",
        temperature=temperature,
    )


def get_llm(temperature: float = 0.0, tools: Optional[List] = None) -> BaseChatModel:
    """
    Standard factory with a built-in fallback chain.
    If the primary provider fails (e.g. decommissioned model),
    it automatically tries the next best alternative.

    Args:
        temperature: Controls randomness.
        tools: Optional list of tools to bind to the LLM (and all fallbacks).
    """
    provider = Config.LLM_PROVIDER.lower()

    def _prepare_model(model_getter, temp):
        model = model_getter(temp)
        if model and tools:
            # Force tool_choice="auto" which sometimes helps Groq models
            # adhere to the JSON schema rather than hallucinating tags.
            return model.bind_tools(tools, tool_choice="auto")
        return model

    # 1. Try to create the primary requested provider
    primary_llm = None
    if provider == "gemini":
        primary_llm = _prepare_model(_get_gemini, temperature)
    elif provider == "openai":
        primary_llm = _prepare_model(_get_openai, temperature)
    elif provider == "groq":
        primary_llm = _prepare_model(_get_groq, temperature)

    if not primary_llm:
        # If primary failed to initialize (e.g. missing keys), fall back immediately
        print(f"[WARN] Failed to initialize primary provider '{provider}'. Check keys.")
        fallback_llm = _prepare_model(_get_gemini, temperature) or _prepare_model(
            _get_openai, temperature
        )
        if not fallback_llm:
            raise EnvironmentError("No LLM providers could be initialized. Check .env.")
        return fallback_llm

    # 2. Wrap the primary in a fallback chain
    fallbacks: List[BaseChatModel] = []

    # Gemini is the strongest/most stable fallback
    if provider != "gemini":
        gemini = _prepare_model(_get_gemini, temperature)
        if gemini:
            fallbacks.append(gemini)

    # Standard OpenAI is a good second fallback
    if provider != "openai":
        openai = _prepare_model(_get_openai, temperature)
        if openai:
            fallbacks.append(openai)

    if not fallbacks:
        # If user only has one key, we can't provide automatic failover
        return primary_llm

    # langchain.runnables.RunnableWithFallbacks catches common API errors
    return primary_llm.with_fallbacks(fallbacks)
