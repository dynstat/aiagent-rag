"""
rag/embeddings.py
-----------------
PURPOSE: Creates and returns the embedding model used to convert text
         into vector representations (numbers) for semantic search.

         An embedding model is the bridge between human language and
         the mathematical space where similarity is measured by distance.
         Two sentences with similar meaning will have vectors that are
         close together in that space.

         We use SentenceTransformers (HuggingFace) so embeddings are
         computed LOCALLY — no API cost, no latency for embedding calls.
"""

from langchain_community.embeddings import SentenceTransformerEmbeddings
from config import Config


def get_embeddings() -> SentenceTransformerEmbeddings:
    """
    Returns a LangChain-compatible embedding model backed by
    SentenceTransformers running locally on CPU.

    The model is downloaded once and cached in ~/.cache/huggingface.
    Subsequent calls are instant.

    Returns:
        SentenceTransformerEmbeddings — implements LangChain's Embeddings
        interface, so it can be passed directly to any LangChain vector store.
    """
    return SentenceTransformerEmbeddings(
        model_name=Config.EMBEDDING_MODEL
        # device="cuda" if you have an NVIDIA GPU; "cpu" is fine for demos
    )
