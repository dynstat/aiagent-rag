"""
rag/vector_store.py
-------------------
PURPOSE: Manages the ChromaDB vector store — the "long-term memory" of
         retrieved knowledge.

         HOW RAG WORKS (simplified):
         1. You provide documents (text files, PDFs, notes, etc.)
         2. Each document is split into small chunks (≈ 500 tokens each).
         3. Each chunk is converted to a vector via the embedding model.
         4. Vectors are stored in ChromaDB on disk.
         5. At query time: the question is also embedded, and the K nearest
            vectors are retrieved — these are the "relevant context" chunks
            that get injected into the LLM prompt.

         ChromaDB persists to disk so your indexed documents survive restarts.
"""

import os
from typing import List

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import Config
from rag.embeddings import get_embeddings


def get_vector_store() -> Chroma:
    """
    Returns (or creates) the ChromaDB vector store.

    If the persist directory already contains data, the existing store is
    loaded — no re-indexing needed.  Otherwise, a fresh empty store is
    created and will be populated when you call ingest_documents().

    Returns:
        Chroma — LangChain's wrapper around ChromaDB with retriever support.
    """
    # Ensure the storage directory exists before ChromaDB tries to open it
    os.makedirs(Config.CHROMA_PERSIST_DIR, exist_ok=True)

    return Chroma(
        collection_name=Config.CHROMA_COLLECTION,
        embedding_function=get_embeddings(),
        persist_directory=Config.CHROMA_PERSIST_DIR,
    )


def ingest_documents(documents: List[Document]) -> Chroma:
    """
    PURPOSE: Takes raw LangChain Document objects, splits them into chunks,
             embeds each chunk, and stores them in ChromaDB.

    This is the "indexing pipeline" — run it once whenever you add new data.
    The agent never calls this; it's called from data/ingest.py.

    Args:
        documents: List of LangChain Document objects.
                   Each Document has .page_content (text) and .metadata (dict).

    Returns:
        The populated Chroma vector store.
    """
    # ── Step 1: Split documents into small overlapping chunks ────────────────
    # WHY SPLIT? LLMs have limited context windows. Splitting ensures each
    # chunk is small enough to be useful context without overwhelming the LLM.
    # Overlap (100 chars) prevents important info from being cut at boundaries.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,       # characters per chunk
        chunk_overlap=100,    # how much adjacent chunks share
        length_function=len,
    )
    chunks = splitter.split_documents(documents)
    print(f"[Ingest] Split {len(documents)} document(s) into {len(chunks)} chunk(s).")

    # ── Step 2: Embed chunks and store in ChromaDB ───────────────────────────
    # Chroma.from_documents() calls the embedding model on each chunk and
    # persists the resulting vectors to disk.
    os.makedirs(Config.CHROMA_PERSIST_DIR, exist_ok=True)
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        collection_name=Config.CHROMA_COLLECTION,
        persist_directory=Config.CHROMA_PERSIST_DIR,
    )
    print(f"[Ingest] Stored {len(chunks)} chunk(s) in ChromaDB at '{Config.CHROMA_PERSIST_DIR}'.")
    return vector_store


def get_retriever():
    """
    PURPOSE: Returns a LangChain retriever backed by our ChromaDB store.

    A retriever has a single method: .invoke(query) → List[Document].
    LangGraph tools and chains use retrievers so they don't need to know
    whether the backend is ChromaDB, FAISS, Pinecone, etc.

    Returns:
        VectorStoreRetriever configured for top-K semantic search.
    """
    store = get_vector_store()
    return store.as_retriever(
        search_type="similarity",          # cosine similarity (default)
        search_kwargs={"k": Config.RAG_TOP_K},
    )
