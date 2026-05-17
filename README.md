# AI Agent RAG — Customizable Knowledge Assistant

An educational project demonstrating **Retrieval-Augmented Generation (RAG)** with a **multi-tool AI agent** using LangChain, LangGraph, and LangSmith.

## What This Project Teaches

| Concept | Where It's Implemented |
|---|---|
| RAG pipeline (embed → store → retrieve) | `rag/` module + `data/ingest.py` |
| LangGraph agent (nodes + edges + state) | `agent/graph.py` |
| Tool calling (multiple tools, multiple turns) | `tools/` module |
| Short-term memory (sliding window) | `memory/conversation_memory.py` |
| Long-term memory (checkpointer) | `agent/graph.py` → `MemorySaver` |
| LangSmith tracing | `main.py` + `.env` config |
| Provider abstraction (Gemini / OpenAI) | `llm_factory.py` |

## Project Structure

```
aiagent-rag/
├── main.py                      # Entry point — interactive REPL
├── config.py                    # Centralized config from .env
├── llm_factory.py               # Creates Gemini or OpenAI LLM
│
├── agent/
│   ├── graph.py                 # LangGraph StateGraph definition
│   └── runner.py                # High-level AgentRunner class
│
├── rag/
│   ├── embeddings.py            # SentenceTransformers embedding model
│   └── vector_store.py          # ChromaDB vector store + ingestion
│
├── memory/
│   └── conversation_memory.py   # Sliding-window short-term memory
│
├── tools/
│   ├── rag_tool.py              # Tool: search the vector store
│   ├── custom_tools.py          # Custom domain-specific tools
│   └── utility_tools.py         # Tools: date, calculation, formatting
│
└── data/
    ├── ingest.py                # Run once to populate ChromaDB
    └── knowledge_base/          # Your .txt/.md files go here
        ├── your_doc_1.md
        ├── company_policies.md
        └── knowledge_base.txt
```

## Setup

### 1. Clone and activate the virtual environment
```powershell
& d:\proj\aiagent-rag\.venv\Scripts\Activate.ps1
```

### 2. Configure your API keys
```powershell
Copy-Item .env.example .env
# Edit .env and fill in your keys
```

Get your keys:
- **Google Gemini**: https://aistudio.google.com/app/apikey
- **LangSmith** (optional, for tracing): https://smith.langchain.com

### 3. Ingest the knowledge base (one-time setup)
```powershell
python data/ingest.py
```

### 4. Run the agent
```powershell
python main.py
```

## Example Queries

- `What does the documentation say about X?`
- `Summarize the guidelines from the knowledge base.`
- `Can you check the database for record 123?`
- `What is the policy for remote work?`
- `Combine the info from the vector store with current date constraints.`

## Adding Your Own Data

1. Add `.txt` or `.md` files to `data/knowledge_base/`
2. Re-run `python data/ingest.py`
3. The agent will automatically use the new data via `rag_search`

## Architecture: How the Agent Thinks

```
User Question
     │
     ▼
LLM Node (Gemini/OpenAI)
  → Reads system prompt + conversation history
  → Decides: call a tool OR answer directly
     │
     ├─── Tool Call? ──→ ToolNode
     │                     → rag_search (vector DB lookup)
     │                     → fetch_database_record (Custom Tool)
     │                     → calculate_metrics (Custom Tool)
     │                     → ... (any tool)
     │                     │
     │                     └──→ back to LLM Node (loop!)
     │
     └─── Final Answer? ──→ Return to user
```

The agent can loop through the LLM→Tool→LLM cycle **multiple times** until it has enough information to answer confidently.
