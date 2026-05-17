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

## ☁️ Running in Google Colab

Yes, this project runs perfectly in Google Colab! Open a new Colab notebook and run the following in the cells:

**Cell 1: Clone & Install Dependencies**
```python
!git clone https://github.com/dynstat/aiagent-rag.git
%cd aiagent-rag
!pip install .
```

**Cell 2: Set Environment Variables**
```python
import os
# Set your API keys here
os.environ["LLM_PROVIDER"] = "gemini" # or "openai"
os.environ["GOOGLE_API_KEY"] = "your_google_api_key_here"

# (Optional) If using OpenCode / Zen
# os.environ["OPENAI_API_KEY"] = "your_key"
# os.environ["OPENAI_BASE_URL"] = "https://opencode.ai/zen/v1"
# os.environ["OPENAI_MODEL"] = "minimax-m2.5-free"
```

**Cell 3: Ingest Data & Run**
```python
# Create the vector database
!python data/ingest.py

# Start the interactive agent loop
!python main.py
```
*(Note: Colab supports the `input()` function, so you can interact with the agent directly in the cell output!)*

## Example Queries

- `What does the documentation say about X?`
- `Summarize the guidelines from the knowledge base.`
- `Can you check the database for record 123?`
- `What is the policy for remote work?`
- `Combine the info from the vector store with current date constraints.`

## How to Customize for Your Own Use Case

This project is built to be a template. You can easily connect it to your own company's data, databases, and APIs.

### 1. Adding Unstructured Data (Vector Search / RAG)
If you have PDFs, markdown files, or text documents you want the agent to read:
1. Place your `.txt` or `.md` files in the `data/knowledge_base/` folder.
2. Run `python data/ingest.py` to embed and store them in the local ChromaDB.
3. The agent will automatically search this database whenever a user asks a relevant question.

### 2. Connecting to Your Own Database or APIs (Custom Tools)
If you want the agent to query a real SQL database, fetch live weather, or interact with external APIs:
1. Create a new tool function in `tools/custom_tools.py`.
2. Decorate it with `@tool` and write a **very clear docstring**. The agent reads the docstring to know *when* and *how* to use your tool.
   ```python
   from langchain_core.tools import tool

   @tool
   def query_user_database(email: str) -> str:
       """Fetches a user's account details from the MySQL database using their email."""
       # Add your SQL connection or API request logic here...
       return f"User {email} is on the Pro plan."
   ```
3. Register your new tool by adding it to the `TOOLS` list in `tools/__init__.py`.

### 3. Update the Agent's Persona
To change how the agent behaves or what instructions it follows, edit the `_get_system_prompt()` function inside `agent/runner.py`. Give it a new role, rules, and guidelines specific to your domain!

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
