# AI Agent RAG — Technical Knowledge Assistant

An educational project demonstrating **Retrieval-Augmented Generation (RAG)** with a **multi-tool AI agent** designed to help you explore and understand any technical documentation you provide.

## What This Project Teaches

| Concept | Where It's Implemented |
|---|---|
| RAG pipeline (embed → store → retrieve) | `rag/` module + `data/ingest.py` |
| LangGraph agent (nodes + edges + state) | `agent/graph.py` |
| Tool calling (multiple tools, multiple turns) | `tools/` module |
| PDF/Markdown/Text ingestion | `data/ingest.py` (via `PyPDFLoader`) |
| Short-term memory (sliding window) | `memory/conversation_memory.py` |
| Long-term memory (checkpointer) | `agent/graph.py` → `MemorySaver` |
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
│   └── utility_tools.py         # Tools: date and time utility
│
└── data/
    ├── ingest.py                # Run once to populate ChromaDB
    └── knowledge_base/          # Your PDF/MD/TXT files go here
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

### 3. Ingest your knowledge base (one-time setup)
```powershell
# Add your technical documents (.pdf, .md, .txt) to data/knowledge_base/
python data/ingest.py
```

### 4. Run the agent
```powershell
python main.py
```

## Example Queries (using sample data)

- `What is the core architecture described in the documents?`
- `How do I implement X based on the provided guides?`
- `Explain the difference between concepts A and B.`
- `Summarize the best practices from the technical documentation.`

## How to Customize for Your Own Use Case

This project is built to be a template. You can easily connect it to **any** technical documentation.

### 1. Adding Your Documentation (RAG)
1. Place your `.pdf`, `.md`, or `.txt` files in the `data/knowledge_base/` folder.
2. Run `python data/ingest.py` to embed and store them in the local ChromaDB.
3. The agent will automatically search this database whenever you ask a question related to your specific content.

### 2. Update the Agent's Persona
To change how the agent behaves or its default expertise, edit the `SYSTEM_PROMPT` inside `agent/graph.py`. Give it rules and guidelines specific to your technical domain!

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
     │                     → get_current_date_and_time (Utility)
     │                     │
     │                     └──→ back to LLM Node (loop!)
     │
     └─── Final Answer? ──→ Return to user
```
