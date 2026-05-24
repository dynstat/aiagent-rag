"""
main.py
-------
PURPOSE: Entry point for the AI Agent RAG application.

         This file:
         1. Validates environment configuration
         2. Sets up LangSmith tracing (if configured)
         3. Runs the ingestion pipeline (if the vector store is empty)
         4. Starts an interactive REPL (Read-Eval-Print Loop) for chatting
            with the agent

HOW TO RUN:
    # 1. Copy .env.example to .env and fill in your API keys
    # 2. Activate the virtual environment
    & d:\\proj\\aiagent-rag\\.venv\\Scripts\\Activate.ps1

    # 3. Run ingestion first (one-time setup)
    python data/ingest.py

    # 4. Run the agent
    python main.py

UNDERSTANDING THE FLOW:
    User types question
        ↓
    AgentRunner.run(question)
        ↓
    LangGraph: LLM node (decides what to do)
        ↓
    If tool needed → ToolNode → back to LLM node
        ↓
    LLM produces final answer → returned to user
        ↓
    ConversationMemory updated → ready for next question
"""

import os
import sys

# ─────────────────────────────────────────────────────────────────────────────
# Load config FIRST — this reads .env and sets all env variables
# ─────────────────────────────────────────────────────────────────────────────
from config import Config

# ─────────────────────────────────────────────────────────────────────────────
# LangSmith tracing setup
# LangSmith captures every LLM call, tool invocation, and intermediate step
# so you can inspect them at https://smith.langchain.com
# ─────────────────────────────────────────────────────────────────────────────
if Config.LANGCHAIN_TRACING_V2 == "true" and Config.LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = Config.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = Config.LANGCHAIN_PROJECT
    os.environ["LANGCHAIN_ENDPOINT"] = Config.LANGCHAIN_ENDPOINT
    print(f"[LangSmith] Tracing enabled -> Project: {Config.LANGCHAIN_PROJECT}")
else:
    # Explicitly disable to avoid accidental tracing without keys
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    print(
        "[LangSmith] Tracing disabled (set LANGCHAIN_API_KEY + LANGCHAIN_TRACING_V2=true to enable)"
    )

# ── Explicitly push keys into os.environ so all libraries pick them up ────────
# Some libraries (openai SDK, langchain) read directly from os.environ rather
# than from constructor args. Setting them here guarantees they're available
# regardless of when/how each library initializes.
if Config.OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
if Config.OPENAI_BASE_URL:
    os.environ["OPENAI_BASE_URL"] = Config.OPENAI_BASE_URL

# Debug: confirm the key loaded (shows only first 8 chars — safe to display)
_key_preview = Config.OPENAI_API_KEY[:8] + "..." if Config.OPENAI_API_KEY else "NOT SET"
print(
    f"[Config] Provider={Config.LLM_PROVIDER} | Model={Config.OPENAI_MODEL} | Key={_key_preview}"
)

from agent import AgentRunner


# ─────────────────────────────────────────────────────────────────────────────
# Helper: check if the vector store already has data
# ─────────────────────────────────────────────────────────────────────────────
def vector_store_is_populated() -> bool:
    """
    PURPOSE: Quickly check whether ChromaDB already has indexed documents.
             Avoids re-running ingestion unnecessarily on every startup.
    """
    try:
        from rag import get_vector_store

        store = get_vector_store()
        # Try getting a collection count — if > 0, data exists
        count = store._collection.count()
        return count > 0
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Helper: auto-ingest if vector store is empty
# ─────────────────────────────────────────────────────────────────────────────
def maybe_ingest() -> None:
    """
    PURPOSE: On first run, automatically ingest the sample knowledge base.
             This means the user doesn't need to remember to run ingest.py.
    """
    if not vector_store_is_populated():
        print("\n[Setup] Vector store is empty. Running initial ingestion...\n")
        # Import and run the ingestion pipeline
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "data"))
        from data.ingest import run_ingestion

        run_ingestion()
    else:
        print("[Setup] Vector store already populated. Skipping ingestion.")


# ─────────────────────────────────────────────────────────────────────────────
# REPL — Interactive Chat Loop
# ─────────────────────────────────────────────────────────────────────────────
def interactive_chat(agent: AgentRunner) -> None:
    """
    PURPOSE: A simple command-line chat interface for interacting with the agent.

    Special commands:
        /history  — print the conversation history
        /new      — start a fresh session (clears memory)
        /tools    — list all available tools
        /quit     — exit the application

    Args:
        agent: The initialized AgentRunner instance.
    """
    # Determine model name for display
    if Config.LLM_PROVIDER == "gemini":
        model_name = Config.GEMINI_MODEL
    elif Config.LLM_PROVIDER == "openai":
        model_name = Config.OPENAI_MODEL
    elif Config.LLM_PROVIDER == "groq":
        model_name = Config.GROQ_MODEL
    else:
        model_name = "unknown"

    print("\n" + "=" * 60)
    print("  AI Agent RAG — Technical Knowledge Assistant")
    print("=" * 60)
    print(f"  Provider : {Config.LLM_PROVIDER.upper()} ({model_name})")
    print(f"  Thread   : {agent.thread_id[:8]}...")
    print("=" * 60)
    print("  Commands: /history | /new | /tools | /quit")
    print("=" * 60)
    print("\n  Ask questions about any technical documentation you've added.")
    print("  Try asking (if using sample data):")
    print("  • 'What is Async Rust?'")
    print("  • 'How do I create a multi-module project in CMake?'")
    print("  • 'Explain the core concepts from the provided guides.'\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! 👋")
            break

        if not user_input:
            continue

        # ── Special commands ─────────────────────────────────────────────────
        if user_input.lower() == "/quit":
            print("Goodbye! 👋")
            break

        elif user_input.lower() == "/history":
            history = agent.get_conversation_history()
            if history:
                print(f"\n{'─' * 40}")
                print("Conversation History:")
                print(f"{'─' * 40}")
                print(history)
                print(f"{'─' * 40}\n")
            else:
                print("[No conversation history yet]\n")
            continue

        elif user_input.lower() == "/new":
            agent.new_session()
            print(f"[New session started | Thread: {agent.thread_id[:8]}...]\n")
            continue

        elif user_input.lower() == "/tools":
            from tools import ALL_TOOLS

            print(f"\n{'─' * 40}")
            print(f"Available Tools ({len(ALL_TOOLS)}):")
            print(f"{'─' * 40}")
            for t in ALL_TOOLS:
                # Each LangChain tool has a .name and .description attribute
                desc_first_line = t.description.strip().split("\n")[0]
                print(f"  • {t.name}: {desc_first_line}")
            print(f"{'─' * 40}\n")
            continue

        # ── Normal query — send to agent ─────────────────────────────────────
        agent.run(user_input, verbose=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    """
    PURPOSE: Application entry point.
    1. Validate config (fail fast if API keys are missing)
    2. Auto-ingest knowledge base if needed
    3. Initialize the agent
    4. Start the interactive chat loop
    """
    # Step 1: Validate — raises EnvironmentError if keys are missing
    Config.validate()

    # Step 2: Auto-ingest knowledge base if ChromaDB is empty
    maybe_ingest()

    # Step 3: Create the agent runner (this builds the LangGraph)
    print("\n[Agent] Initializing agent...")
    agent = AgentRunner()

    # Step 4: Start interactive chat
    interactive_chat(agent)


if __name__ == "__main__":
    main()
