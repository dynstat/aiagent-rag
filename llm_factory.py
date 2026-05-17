"""
llm_factory.py
--------------
PURPOSE: Single place that creates the LangChain LLM object.
         The rest of the codebase never imports langchain-google-genai
         or langchain-openai directly — they just call get_llm().
         This makes it trivial to swap providers without touching agent code.
"""

from config import Config
from langchain_core.language_models import BaseChatModel


def get_llm(temperature: float = 0.0) -> BaseChatModel:
    """
    Factory function — returns the appropriate LangChain LLM based on
    the LLM_PROVIDER env variable.

    Args:
        temperature: Controls randomness.
                     0.0 = deterministic (good for tool calling / RAG).
                     0.7+ = more creative (good for summarisation).

    Returns:
        A LangChain BaseChatModel instance (Gemini or OpenAI-compatible).
    """

    provider = Config.LLM_PROVIDER.lower()

    if provider == "gemini":
        # ── Google Gemini via langchain-google-genai ─────────────────────────
        # ChatGoogleGenerativeAI wraps the Gemini REST API.
        # It supports tool/function calling which is required for our agent.
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=Config.GEMINI_MODEL,
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=temperature,
            # convert_system_message_to_human=True is needed for some Gemini
            # model versions that don't support system messages natively.
            convert_system_message_to_human=False,
        )

    elif provider == "openai":
        # ── OpenAI / OpenCode / Zen / OpenRouter (OpenAI-compatible) ─────────
        # ChatOpenAI works with any OpenAI-compatible API endpoint.
        # Point OPENAI_BASE_URL at your OpenRouter/Zen/OpenCode endpoint.
        #
        # WHY default_headers?
        # Some SDK versions don't reliably forward `api_key` as the
        # Authorization Bearer header when using a custom base_url.
        # Explicitly setting it in default_headers guarantees delivery.
        from langchain_openai import ChatOpenAI

        api_key = Config.OPENAI_API_KEY
        if not api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY is empty. Check your .env file."
            )

        return ChatOpenAI(
            model=Config.OPENAI_MODEL,
            api_key=api_key,
            base_url=Config.OPENAI_BASE_URL,
            temperature=temperature,
            # Explicit Authorization header — works around SDK/proxy quirks
            default_headers={
                "Authorization": f"Bearer {api_key}",
                # OpenRouter recommends these optional headers for attribution
                "HTTP-Referer": "http://localhost",
                "X-Title": "aiagent-rag",
            },
        )

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER='{Config.LLM_PROVIDER}'. "
            "Valid values: 'gemini', 'openai'"
        )
