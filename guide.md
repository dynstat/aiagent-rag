# 🚀 Comprehensive Guide: AI Agent & RAG Architecture

Welcome to the definitive guide for understanding, configuring, and modifying this AI Agent project. This guide is designed for developers who want to deeply understand how modern AI Agents, RAG (Retrieval-Augmented Generation), and Tool-Calling loops work under the hood using **LangGraph** and **LangChain**.

---

## 📖 Table of Contents
1. [Core Concepts](#1-core-concepts-what-are-we-building)
2. [Setup & Configuration (.env Demystified)](#2-setup--configuration-env-demystified)
3. [File-by-File Breakdown](#3-file-by-file-breakdown)
4. [Understanding the Agent Loop (LangGraph)](#4-understanding-the-agent-loop-langgraph)
5. [Understanding RAG](#5-understanding-rag-retrieval-augmented-generation)
6. [Modifying for Your Use Case](#6-modifying-for-your-use-case)

---

## 1. Core Concepts: What are we building?

Before diving into code, let's understand the three pillars of this project:

*   **RAG (Retrieval-Augmented Generation):** LLMs are frozen in time and don't know your private data. RAG solves this by converting your text documents into numbers (Embeddings), storing them in a database, and performing a "similarity search" when a user asks a question. The relevant text is then fed to the LLM as context.
*   **Tool Calling:** Standard LLMs just generate text. A "Tool-Calling" LLM can decide to execute Python functions. You provide the LLM a list of tools (like `calculate_metrics` or `search_database`), and the LLM responds with a JSON payload telling your code *which tool to run* and *with what arguments*.
*   **AI Agent (The Loop):** An Agent is an LLM running in a continuous feedback loop. It thinks: *"What should I do next? Do I have the answer? No? Let me call a tool."* It runs the tool, sees the result, and thinks again. This is powered by **LangGraph**.

---

## 2. Setup & Configuration (.env Demystified)

This project uses `llm_factory.py` to seamlessly switch between different AI providers without changing your core agent logic.

Here is exactly how to configure your `.env` for different scenarios:

### Scenario A: Using Google Gemini Natively
If you want to use Google's free Gemini API directly:
```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=AIzaSy...your_key...
# (You can leave the OPENAI variables empty or commented out)
```

### Scenario B: Using Standard OpenAI (ChatGPT)
If you have an OpenAI account and want to use GPT-4o:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...your_key...
OPENAI_MODEL=gpt-4o
# (You must delete or comment out OPENAI_BASE_URL so it defaults to OpenAI's real servers)
```

### Scenario C: Using OpenCode, Zen, or OpenRouter (OpenAI-Compatible Endpoints)
Many services provide free/cheaper models using OpenAI's exact API format. This is what we are using!
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-zen-or-opencode-key
OPENAI_BASE_URL=https://opencode.ai/zen/v1   # The custom endpoint!
OPENAI_MODEL=minimax-m2.5-free               # The model name provided by your service
```
*Why this works:* The LangChain `ChatOpenAI` client will send requests to `OPENAI_BASE_URL` instead of OpenAI's servers, allowing you to use open-source or third-party models seamlessly.

---

## 3. File-by-File Breakdown

Here is what every file does in the system:

*   **`main.py`**: The entry point. It sets up environment variables, initializes the Agent, and runs the interactive `You: / Agent:` chat loop in your terminal.
*   **`config.py`**: Reads your `.env` file and strictly validates it. If you are missing a required key for your chosen provider, it crashes early with a clear error.
*   **`llm_factory.py`**: The adapter. Depending on your `.env`, it creates either a `ChatGoogleGenerativeAI` object or a `ChatOpenAI` object. 
*   **`agent/graph.py`**: The heart of the agent. This defines the **LangGraph StateGraph** (the flow chart of the agent's brain) and handles long-term memory via the `MemorySaver` checkpointer.
*   **`agent/runner.py`**: A clean wrapper class that hides the complexity of LangGraph. It provides the `_get_system_prompt()` (the Agent's persona) and the `.run()` method to stream outputs to the terminal.
*   **`rag/embeddings.py`**: Uses `SentenceTransformers` to convert text into numbers (vectors) locally on your CPU for free, without needing API calls.
*   **`rag/vector_store.py`**: Manages `ChromaDB`, a local database that stores your embedded vectors and performs the similarity searches.
*   **`data/ingest.py`**: A script you run manually once. It reads `.md` files, chunks them into small paragraphs, and saves them into ChromaDB.
*   **`tools/rag_tool.py`**: The bridge between RAG and the Agent. It wraps the ChromaDB search inside an `@tool` decorator so the LLM can trigger it autonomously.

---

## 4. Understanding the Agent Loop (LangGraph)

If you look inside `agent/graph.py`, you will see we define a `StateGraph`. Think of this as a state machine:

1.  **START**: User asks "What is the policy?"
2.  **LLM Node (`call_model`)**: The LLM looks at the question and its available tools. It realizes it doesn't know the policy. It outputs a `tool_call` request for `rag_search`.
3.  **Conditional Edge (`should_continue`)**: LangGraph intercepts the LLM's response. It says: *"Did the LLM ask for a tool? Yes? Route to the Tool Node. No? Route to END."*
4.  **Tool Node (`tools`)**: Python executes `rag_search(query="policy")` and gets the text from the database. It attaches this text to the conversation history as a "Tool Message".
5.  **Back to LLM Node**: LangGraph routes back to step 2. The LLM now sees the user's question *and* the database results. It synthesizes a final answer and outputs plain text.
6.  **END**: The conditional edge sees no tool calls, routes to END, and the answer is printed to the user.

---

## 5. Understanding RAG (Retrieval-Augmented Generation)

When you run `python data/ingest.py`, here is what happens:
1.  **Load**: `TextLoader` reads your markdown files.
2.  **Chunk**: `RecursiveCharacterTextSplitter` breaks the long document into ~1000-character chunks. (LLMs have context limits, and vector searches are more accurate on smaller chunks).
3.  **Embed**: The `all-MiniLM-L6-v2` AI model converts the text of each chunk into a 384-dimensional array of floats (a vector). 
4.  **Store**: These arrays are saved into the `chroma_db` folder.

When the agent uses `rag_search("remote work policy")`:
1. It embeds the query "remote work policy" into a 384-dimensional vector.
2. It asks ChromaDB: *"Which stored vectors are mathematically closest to this query vector?"*
3. ChromaDB returns the original text chunks, which are fed to the LLM.

---

## 6. Modifying for Your Use Case

To make this project your own, follow these 3 steps:

### A. Change the Agent's Persona
Open `agent/runner.py`. Find `_get_system_prompt()`. Rewrite it completely!
*"You are a highly strictly customer support bot for Company X. Never apologize. Always check the knowledge base before answering..."*

### B. Add Your Own Knowledge
1. Delete the dummy files in `data/knowledge_base/`.
2. Add your company's PDFs, TXT, or MD files. (You may need to update `ingest.py` to use `PyPDFLoader` if using PDFs).
3. Delete the `chroma_db/` folder to clear old memory.
4. Run `python data/ingest.py`.

### C. Build Custom Tools
Want your agent to do real things? Create a tool in `tools/custom_tools.py`:
```python
from langchain_core.tools import tool
import requests

@tool
def trigger_webhook(user_id: str, action: str) -> str:
    """Use this tool to trigger a server action for a specific user ID."""
    # Your python code here
    requests.post("https://your-api.com/trigger", json={"id": user_id, "action": action})
    return "Webhook triggered successfully."
```
Add `trigger_webhook` to the `TOOLS` list in `tools/__init__.py`. The LLM will now read your docstring and use the tool whenever a user asks to trigger an action!
