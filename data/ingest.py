"""
data/ingest.py
--------------
PURPOSE: One-time (or periodic) script to load your custom documents into
         the ChromaDB vector store.

         Run this script BEFORE running main.py for the first time, or
         whenever you add/update documents in data/knowledge_base/.

         WORKFLOW:
         1. Load text/markdown/PDF files from the knowledge base directory
         2. Split them into chunks (handled by ingest_documents())
         3. Embed each chunk (sentence-transformers, local)
         4. Store embeddings in ChromaDB (persisted to disk)
         5. Next time the agent calls rag_search(), it searches these embeddings

         HOW TO RUN:
             uv run data/ingest.py
"""

import os
import sys

# Ensure project root is on sys.path so imports like `from config import Config` work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from config import Config
from rag import ingest_documents

KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")


def load_documents_from_directory(directory: str) -> list[Document]:
    """
    PURPOSE: Walk the knowledge_base/ directory and load all .txt and .md files
             as LangChain Document objects.

    Each Document has:
      - .page_content: the raw text of the file
      - .metadata["source"]: the file path (used in citations)

    Args:
        directory: Path to the folder containing knowledge base files.

    Returns:
        List of Document objects ready for ingestion.
    """
    if not os.path.exists(directory):
        print(f"[Ingest] Knowledge base directory not found: {directory}")
        print("[Ingest] Creating it with sample data...")
        os.makedirs(directory, exist_ok=True)
        return []

    documents = []

    # Walk all files manually to support .txt, .md, and .pdf
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath):
            continue

        if filename.endswith((".txt", ".md")):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            documents.append(
                Document(
                    page_content=content,
                    metadata={"source": filepath, "filename": filename},
                )
            )
            print(f"[Ingest] Loaded: {filename} ({len(content)} chars)")
        elif filename.endswith(".pdf"):
            try:
                loader = PyPDFLoader(filepath)
                pdf_docs = loader.load()
                # Ensure filename is in metadata for each page
                for d in pdf_docs:
                    d.metadata["filename"] = filename
                documents.extend(pdf_docs)
                print(f"[Ingest] Loaded PDF: {filename} ({len(pdf_docs)} pages)")
            except Exception as e:
                print(f"[Ingest] Error loading PDF {filename}: {e}")

    return documents


def run_ingestion() -> None:
    """
    PURPOSE: Main ingestion pipeline.
    Loads all documents and stores them in the vector store.
    """
    print(f"\n{'=' * 60}")
    print("RAG Knowledge Base Ingestion")
    print(f"{'=' * 60}")
    print(f"Source:      {KNOWLEDGE_BASE_DIR}")
    print(f"Vector Store: {Config.CHROMA_PERSIST_DIR}")
    print(f"Collection:   {Config.CHROMA_COLLECTION}")
    print(f"Embedding:    {Config.EMBEDDING_MODEL}")
    print(f"{'=' * 60}\n")

    # Load documents
    docs = load_documents_from_directory(KNOWLEDGE_BASE_DIR)

    if not docs:
        print("[Ingest] No documents found. Add .txt or .md files to:")
        print(f"         {KNOWLEDGE_BASE_DIR}")
        return

    print(f"\n[Ingest] Found {len(docs)} document(s). Starting embedding...\n")

    # Embed and store in ChromaDB
    ingest_documents(docs)

    print(f"\n✅ Ingestion complete! {len(docs)} document(s) embedded and stored.")
    print(f"   The agent can now search this knowledge base via the rag_search tool.\n")


if __name__ == "__main__":
    run_ingestion()
