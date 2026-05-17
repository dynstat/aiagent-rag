# AI Agent RAG — Project Overview

## Final File Structure

```
aiagent-rag/
├── .env                         ← Fill in your API keys here
├── .env.example                 ← Template / reference
├── config.py                    ← All config loaded from .env
├── llm_factory.py               ← Swap between Gemini / OpenAI
├── main.py                      ← Entry point + interactive REPL
├── README.md
│
├── agent/
│   ├── __init__.py
│   ├── graph.py                 ← LangGraph StateGraph (core agent loop)
│   └── runner.py                ← AgentRunner: session management + streaming
│
├── rag/
│   ├── __init__.py
│   ├── embeddings.py            ← SentenceTransformers (local, no API cost)
│   └── vector_store.py          ← ChromaDB: store + retrieve + ingest pipeline
│
├── memory/
│   ├── __init__.py
│   └── conversation_memory.py   ← Sliding-window short-term memory
│
├── tools/
│   ├── __init__.py              ← ALL_TOOLS registry (single list)
│   ├── rag_tool.py              ← rag_search: semantic search tool
│   ├── rep_tools.py             ← 5 CRM-style rep tools
│   └── utility_tools.py         ← date, ranking, formatting tools
│
└── data/
    ├── ingest.py                ← Run once to populate ChromaDB
    ├── chroma_db/               ← Auto-created: persisted vector store
    └── knowledge_base/
        ├── rep_guidelines.md    ← Sample: territory + quota policies
        ├── product_catalog.md   ← Sample: product/pricing + objections
        └── coaching_notes.md    ← Sample: rep-specific coaching notes
```

## Quick Start

```powershell
# 1. Activate venv
& d:\proj\aiagent-rag\.venv\Scripts\Activate.ps1

# 2. Edit .env — add your GOOGLE_API_KEY at minimum
notepad .env

# 3. Ingest knowledge base (one-time)
python data/ingest.py

# 4. Run the agent
python main.py
```

## Available Tools (9 total)

| Tool | Purpose |
|------|---------|
| `rag_search` | Semantic search over ChromaDB vector store |
| `lookup_rep_profile` | Get a rep's CRM profile by rep ID |
| `calculate_quota_attainment` | % of annual quota achieved |
| `get_rep_deals` | Open deals / pipeline for a rep |
| `list_all_reps` | Show all rep IDs and names |
| `summarize_rep_context` | All-in-one rep briefing (aggregates profile + deals + perf) |
| `get_current_date_and_time` | Current date (for time-relative queries) |
| `calculate_rep_ranking` | Leaderboard by metric (attainment / YTD / tenure) |
| `format_currency` | Pretty-print monetary values |

## Key Concepts Demonstrated

### RAG
- Documents in `data/knowledge_base/` → split into 500-char chunks → embedded by `all-MiniLM-L6-v2` → stored in ChromaDB → retrieved by cosine similarity at query time

### LangGraph Agent Loop
```
User → LLM node → [tool call?] → ToolNode → LLM node → ... → Final Answer
```
The loop repeats as many times as needed (multi-step reasoning).

### Memory (Two Layers)
1. **LangGraph MemorySaver** (checkpointer): full state per thread_id — survives multi-turn
2. **ConversationMemory** (our class): sliding window of N turns for display + logging

### LangSmith Tracing
Set `LANGCHAIN_TRACING_V2=true` + `LANGCHAIN_API_KEY=...` in `.env` to see every LLM call, tool invocation, and token count at https://smith.langchain.com
