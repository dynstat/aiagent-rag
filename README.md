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

This project uses [uv](https://github.com/astral-sh/uv) for extremely fast Python package and project management.

### 1. Install dependencies
```bash
uv sync
```
This automatically creates a virtual environment and installs all required packages from `pyproject.toml`.

### 2. Configure your API keys

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

**Then edit `.env` and fill in your keys.**

Get your keys:
- **Google Gemini**: https://aistudio.google.com/app/apikey
- **Groq**: https://console.groq.com/keys

### 3. Ingest your knowledge base (one-time setup)
```bash
# Add your technical documents (.pdf, .md, .txt) to data/knowledge_base/
uv run data/ingest.py
```

### 4. Run the agent
```bash
uv run main.py
```

## Project Management

### Adding new packages
If you need to add new tools or libraries:
```bash
uv add <package_name>
```

### Updating the knowledge base
Whenever you add or remove files in `data/knowledge_base/`, simply re-run the ingestion:
```bash
uv run data/ingest.py
```

## ☁️ Running in Google Colab

This project runs perfectly in Google Colab. Since Colab provides a temporary environment, follow these steps:

### 1. Set up API Keys (Secrets)
Instead of a `.env` file, use Colab's built-in **Secrets** (the key icon 🔑 in the left sidebar):
1.  Add a secret named `LLM_PROVIDER` (value: `gemini`, `openai`, or `groq`).
2.  Add your specific key (e.g., `GOOGLE_API_KEY` or `GROQ_API_KEY`).
3.  **IMPORTANT**: Toggle the blue **"Notebook access"** switch to **ON** for all keys.

### 2. Run in a Cell
Copy and paste this into a Colab cell to initialize and start the agent:

```python
# 1. Install uv and clone
!pip install uv
!git clone https://github.com/dynstat/aiagent-rag.git
%cd aiagent-rag

# 2. Fast install (using --system for Colab)
!uv pip install . --system

# 3. Inject Secrets into Environment
from google.colab import userdata
import os

try:
    os.environ["LLM_PROVIDER"] = userdata.get('LLM_PROVIDER')
    if os.environ["LLM_PROVIDER"] == "gemini":
        os.environ["GOOGLE_API_KEY"] = userdata.get('GOOGLE_API_KEY')
    elif os.environ["LLM_PROVIDER"] == "groq":
        os.environ["GROQ_API_KEY"] = userdata.get('GROQ_API_KEY')
    print(f"✅ Environment Configured: {os.environ['LLM_PROVIDER']}")
except Exception as e:
    print(f"❌ Setup Error: {e}")
    print("Ensure you added LLM_PROVIDER and your API Key to the 'Secrets' sidebar and enabled 'Notebook access'.")

# 4. Ingest Data & Run
!python data/ingest.py
!python main.py
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

> **Note for Groq Users**: Llama 3 models on Groq are highly sensitive to tool-calling instructions in the system prompt. For best results, keep the `SYSTEM_PROMPT` clean and avoid mentioning tool names directly; let the LLM use the structured tool-calling API automatically. We recommend using `llama-3.3-70b-versatile` for the best balance of speed and reasoning.

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
