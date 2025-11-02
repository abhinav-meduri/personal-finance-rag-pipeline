"""
Financial Knowledge RAG Pipeline
A privacy-first, local RAG system for financial advice and information.
"""

__version__ = "1.0.0"
__author__ = "Abhinav Meduri"
__license__ = "CC BY-SA 4.0"

from src.core import hybrid_rag_pipeline, structured_rag_pipeline, rag_pipeline

__all__ = [
    "hybrid_rag_pipeline",
    "structured_rag_pipeline",
    "rag_pipeline",
]

