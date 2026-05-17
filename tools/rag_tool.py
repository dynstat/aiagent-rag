"""
tools/rag_tool.py
-----------------
PURPOSE: Defines the RAG (Retrieval-Augmented Generation) tool that the
         agent can call to fetch relevant context from our vector store.

CONCEPT — Why a RAG tool instead of just injecting docs into every prompt?
         Injecting ALL documents into every prompt is wasteful (uses tokens)
         and confusing for the LLM (too much noise).  Instead, the agent
         decides WHEN to search and WHAT to search for, then retrieves
         only the most relevant chunks.  This is the "augmented" in RAG.

HOW IT WORKS:
         1. Agent decides it needs context → calls `rag_search`
         2. The query is embedded → finds nearest chunks in ChromaDB
         3. Retrieved text is returned to the agent as a string
         4. Agent uses that context to formulate its answer

LangChain @tool decorator:
         - Converts a plain Python function into a LangChain Tool object
         - The function's docstring becomes the tool's description
         - The LLM reads the description to decide when to call this tool
         - Type hints define the input schema (used for function calling)
"""

from langchain_core.tools import tool
from rag import get_retriever


@tool
def rag_search(query: str) -> str:
    """
    Search the internal knowledge base (vector store) for information
    relevant to the given query.

    Use this tool whenever you need factual context about:
    - Sales representatives (reps) and their profiles
    - Customer accounts, deals, or pipeline data
    - Product information, pricing, or specifications
    - Any company-specific data that was loaded into the knowledge base

    Args:
        query: A natural-language question or topic to search for.
               Be specific for better results.
               Example: "What is the territory for rep John Smith?"

    Returns:
        A string containing the top relevant document chunks from the
        knowledge base, separated by '---'.
        Returns "No relevant information found." if nothing matches.
    """
    retriever = get_retriever()

    # Retrieve top-K most semantically similar chunks
    docs = retriever.invoke(query)

    if not docs:
        return "No relevant information found in the knowledge base."

    # Format retrieved chunks into a readable string for the LLM
    results = []
    for i, doc in enumerate(docs, start=1):
        # Include metadata (source file, page, etc.) if available
        source = doc.metadata.get("source", "unknown")
        results.append(
            f"[Result {i}] (Source: {source})\n{doc.page_content}"
        )

    return "\n\n---\n\n".join(results)
