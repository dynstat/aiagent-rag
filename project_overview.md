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
│   └── utility_tools.py         ← date and time utility
│
└── data/
    ├── ingest.py                ← Run once to populate ChromaDB (supports PDF, MD, TXT)
    ├── chroma_db/               ← Auto-created: persisted vector store
    └── knowledge_base/
        ├── Async Rust (...).pdf ← Core technical book
        ├── CMAKE.md             ← CMake reference
        └── ...                  ← Other MD/TXT technical docs
```

## Quick Start

```bash
# 1. Install dependencies (creates virtual environment)
uv sync

# 2. Configure your API keys (copy .env.example to .env and edit)
# Windows: Copy-Item .env.example .env
# Mac/Linux: cp .env.example .env

# 3. Ingest knowledge base (one-time)
uv run data/ingest.py

# 4. Run the agent
uv run main.py
```

## Available Tools

| Tool | Purpose |
|------|---------|
| `rag_search` | Semantic search over ChromaDB vector store (Rust/CMake docs) |
| `get_current_date_and_time` | Current date (for temporal context) |

## Key Concepts Demonstrated

### RAG (Multi-format)
- Documents in `data/knowledge_base/` (PDF, Markdown, Text) → split into chunks → embedded by `all-MiniLM-L6-v2` → stored in ChromaDB → retrieved by cosine similarity at query time. Supports complex PDF layouts via `PyPDFLoader`.

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
