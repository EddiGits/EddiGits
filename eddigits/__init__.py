"""
EddiGits - AI-Powered Video Transcription & Analysis
"""

__version__ = "0.1.0"
__author__ = "EddiGits"

from .transcriber import VideoTranscriber
from .storage import VideoDatabase
from .embeddings import EmbeddingManager
from .indexer import VectorIndexer
from .query_engine import QueryEngine

__all__ = [
    "VideoTranscriber",
    "VideoDatabase",
    "EmbeddingManager",
    "VectorIndexer",
    "QueryEngine",
]
