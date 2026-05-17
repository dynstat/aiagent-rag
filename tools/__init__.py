"""
tools/__init__.py
-----------------
PURPOSE: Assembles ALL tools into a single list that the agent graph imports.
         Having one authoritative list means you only need to add a tool in
         ONE place (here) to make it available to the agent.
"""

from tools.rag_tool import rag_search
from tools.rep_tools import (
    lookup_rep_profile,
    calculate_quota_attainment,
    get_rep_deals,
    list_all_reps,
    summarize_rep_context,
)
from tools.utility_tools import (
    get_current_date_and_time,
    calculate_rep_ranking,
    format_currency,
)

# The single authoritative list of tools available to the agent.
# The LLM will see the name + docstring of each tool and decide
# which one(s) to call based on the user's query.
ALL_TOOLS = [
    # ── RAG / Knowledge Base ─────────────────────────────────────────────────
    rag_search,              # semantic search over vector store

    # ── Rep Domain ───────────────────────────────────────────────────────────
    lookup_rep_profile,      # get a rep's CRM profile
    calculate_quota_attainment,  # % of quota achieved
    get_rep_deals,           # open deals / pipeline for a rep
    list_all_reps,           # show all available rep IDs and names
    summarize_rep_context,   # all-in-one rep briefing

    # ── Utilities ────────────────────────────────────────────────────────────
    get_current_date_and_time,   # current date for time-sensitive queries
    calculate_rep_ranking,       # leaderboard by metric
    format_currency,             # pretty-print monetary values
]

__all__ = ["ALL_TOOLS"]
