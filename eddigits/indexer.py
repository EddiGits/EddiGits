"""
Vector indexing using ChromaDB for semantic search
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings

from .config import Config
from .embeddings import EmbeddingManager
from .transcriber import Transcript

logger = logging.getLogger(__name__)


class VectorIndexer:
    """Manages vector indexing for semantic search"""

    def __init__(
        self,
        db_path: Optional[Path] = None,
        collection_name: str = "video_transcripts"
    ):
        """
        Initialize the vector indexer

        Args:
            db_path: Path to ChromaDB storage
            collection_name: Name of the collection
        """
        self.db_path = db_path or Config.VECTOR_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.collection_name = collection_name
        self.embedding_manager = EmbeddingManager()

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Video transcript embeddings"}
        )

        logger.info(f"ChromaDB initialized at {self.db_path}")

    def create_chunks(
        self,
        transcript: Transcript,
        chunk_size: int = None,
        overlap: int = None
    ) -> List[Dict[str, Any]]:
        """
        Split transcript into chunks with overlap

        Args:
            transcript: Transcript object
            chunk_size: Size of each chunk in seconds
            overlap: Overlap between chunks in seconds

        Returns:
            List of chunk dictionaries
        """
        chunk_size = chunk_size or Config.CHUNK_SIZE
        overlap = overlap or Config.OVERLAP

        chunks = []
        current_time = 0
        duration = transcript.segments[-1].end if transcript.segments else 0

        while current_time < duration:
            chunk_end = min(current_time + chunk_size, duration)

            # Get segments in this time range
            chunk_segments = [
                s for s in transcript.segments
                if s.start < chunk_end and s.end > current_time
            ]

            if chunk_segments:
                chunk_text = " ".join(s.text for s in chunk_segments)
                chunks.append({
                    "start": current_time,
                    "end": chunk_end,
                    "text": chunk_text,
                    "video_path": transcript.video_path
                })

            # Move to next chunk with overlap
            current_time += (chunk_size - overlap)

        logger.info(f"Created {len(chunks)} chunks from transcript")
        return chunks

    def index_transcript(
        self,
        transcript: Transcript,
        video_id: int,
        chunk_size: int = None,
        overlap: int = None
    ) -> List[str]:
        """
        Index a transcript for semantic search

        Args:
            transcript: Transcript object
            video_id: Database video ID
            chunk_size: Size of each chunk in seconds
            overlap: Overlap between chunks in seconds

        Returns:
            List of chunk IDs
        """
        # Create chunks
        chunks = self.create_chunks(transcript, chunk_size, overlap)

        if not chunks:
            logger.warning(f"No chunks created for video {video_id}")
            return []

        # Extract texts and metadata
        texts = [chunk["text"] for chunk in chunks]
        metadatas = []
        ids = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"video_{video_id}_chunk_{i}"
            ids.append(chunk_id)
            metadatas.append({
                "video_id": str(video_id),
                "video_path": chunk["video_path"],
                "start_time": chunk["start"],
                "end_time": chunk["end"],
                "chunk_index": i
            })

        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} chunks")
        embeddings = self.embedding_manager.embed_text(texts)

        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas
        )

        logger.info(f"Indexed {len(chunks)} chunks for video {video_id}")
        return ids

    def search(
        self,
        query: str,
        top_k: int = None,
        video_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks

        Args:
            query: Search query
            top_k: Number of results to return
            video_id: Filter by video ID (optional)

        Returns:
            List of search results with metadata
        """
        top_k = top_k or Config.TOP_K

        # Generate query embedding
        query_embedding = self.embedding_manager.embed_text(query)

        # Build where filter if video_id specified
        where_filter = None
        if video_id is not None:
            where_filter = {"video_id": str(video_id)}

        # Search
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=top_k,
            where=where_filter
        )

        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                    "similarity": 1 - results["distances"][0][i] if "distances" in results else None
                })

        logger.info(f"Found {len(formatted_results)} results for query: {query[:50]}...")
        return formatted_results

    def delete_video(self, video_id: int):
        """
        Delete all chunks for a video

        Args:
            video_id: Video ID to delete
        """
        # Get all chunks for this video
        results = self.collection.get(
            where={"video_id": str(video_id)}
        )

        if results["ids"]:
            self.collection.delete(ids=results["ids"])
            logger.info(f"Deleted {len(results['ids'])} chunks for video {video_id}")

    def get_stats(self) -> Dict[str, Any]:
        """Get indexer statistics"""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": self.collection_name,
            "embedding_model": self.embedding_manager.model_name,
            "embedding_dimension": self.embedding_manager.dimension
        }

    def reset(self):
        """Reset the entire collection (use with caution!)"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Video transcript embeddings"}
        )
        logger.warning("Collection has been reset!")
