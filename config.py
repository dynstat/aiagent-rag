"""
config.py
---------
PURPOSE: Centralized configuration for the entire AI Agent RAG project.
         Loads all environment variables from .env and exposes them as
         typed Python attributes. Every other module imports from here —
         this keeps secrets out of code and in one place.
"""

import os

from dotenv import load_dotenv

# Load variables from .env file into os.environ.
# override=True ensures .env ALWAYS wins — prevents stale shell env vars
# (e.g. an empty OPENAI_API_KEY set from a previous session) from interfering.
load_dotenv(override=True)


class Config:
    """
    Holds all runtime configuration.

    DESIGN NOTE: We use a simple class (not dataclass / pydantic) so that it
    remains importable without any heavy dependencies at module-load time.
    """

    # ── LLM Provider ────────────────────────────────────────────────────────
    # "gemini"  → uses Google Gemini via langchain-google-genai
    # "openai"  → uses OpenAI-compatible endpoint (OpenCode, Zen, OpenAI itself)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")

    # ── Google Gemini ────────────────────────────────────────────────────────
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

    # Model name for Gemini.  gemini-2.0-flash is fast & cheap; swap to
    # gemini-1.5-pro for higher quality reasoning.
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # ── OpenAI / OpenCode / Zen ──────────────────────────────────────────────
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # ── Groq (High-speed Inference) ──────────────────────────────────────────
    # NOTE: Llama 3 models on Groq are sensitive to tool instructions.
    # llama3-70b-8192 is currently the most stable for agentic tool use.
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")

    # ── LangSmith Tracing ────────────────────────────────────────────────────
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "aiagent-rag")
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_ENDPOINT: str = os.getenv(
        "LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"
    )

    # ── Vector Store / RAG ───────────────────────────────────────────────────
    # Directory where ChromaDB persists its embedding database
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")

    # Collection name inside ChromaDB — think of it as a table name
    CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "technical_knowledge")

    # Sentence-Transformers model used for creating embeddings
    # all-MiniLM-L6-v2 is small (80MB) and fast — good for local dev
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Number of top relevant documents to retrieve from the vector store
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "4"))

    # ── Memory ───────────────────────────────────────────────────────────────
    # How many past conversation turns to keep in short-term (in-memory) memory
    MEMORY_WINDOW: int = int(os.getenv("MEMORY_WINDOW", "10"))

    @classmethod
    def validate(cls) -> None:
        """
        PURPOSE: Early-fail validation.  Call this at app startup so the user
                 sees a clear error (e.g. 'missing GOOGLE_API_KEY') rather than
                 a cryptic exception deep inside a LangChain call.
        """
        if cls.LLM_PROVIDER == "gemini" and not cls.GOOGLE_API_KEY:
            raise EnvironmentError(
                "GOOGLE_API_KEY is not set. Add it to your .env file.\n"
                "Get a key at: https://aistudio.google.com/app/apikey"
            )
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise EnvironmentError(
                "OPENAI_API_KEY is not set. Add it to your .env file."
            )
        if cls.LANGCHAIN_TRACING_V2 == "true" and not cls.LANGCHAIN_API_KEY:
            print(
                "[WARN] LANGCHAIN_TRACING_V2=true but LANGCHAIN_API_KEY is empty. "
                "Tracing will be disabled."
            )
