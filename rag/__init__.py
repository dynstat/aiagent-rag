"""
rag/__init__.py
---------------
PURPOSE: Makes `rag` a Python package. Also re-exports the most commonly
         used symbols so callers can write `from rag import get_retriever`
         instead of the longer `from rag.vector_store import get_retriever`.
"""

from rag.vector_store import get_retriever, get_vector_store, ingest_documents
from rag.embeddings import get_embeddings

__all__ = [
    "get_retriever",
    "get_vector_store",
    "ingest_documents",
    "get_embeddings",
]
