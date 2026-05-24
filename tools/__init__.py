"""
tools/__init__.py
-----------------
PURPOSE: Assembles ALL tools into a single list that the agent graph imports.
         Having one authoritative list means you only need to add a tool in
         ONE place (here) to make it available to the agent.
"""

from tools.rag_tool import rag_search
from tools.utility_tools import (
    get_current_date_and_time,
)

# The single authoritative list of tools available to the agent.
# The LLM will see the name + docstring of each tool and decide
# which one(s) to call based on the user's query.
ALL_TOOLS = [
    # ── RAG / Knowledge Base ─────────────────────────────────────────────────
    rag_search,  # semantic search over vector store
    # ── Utilities ────────────────────────────────────────────────────────────
    get_current_date_and_time,  # current date for time-sensitive queries
]

__all__ = ["ALL_TOOLS"]
