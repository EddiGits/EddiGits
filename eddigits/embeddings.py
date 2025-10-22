"""
Text embedding generation for semantic search
"""

import logging
from typing import List, Union, Optional
import numpy as np

from .config import Config

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages text embeddings for semantic search"""

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize the embedding manager

        Args:
            model_name: Name of the embedding model to use
        """
        self.model_name = model_name or Config.EMBEDDING_MODEL
        self.model = None
        self.dimension = None

        logger.info(f"Initializing embedding model: {self.model_name}")

    def _load_model(self):
        """Lazy load the embedding model"""
        if self.model is not None:
            return

        if self.model_name.startswith("sentence-transformers/"):
            self._load_sentence_transformer()
        elif self.model_name == "openai":
            self._load_openai()
        else:
            # Default to sentence transformers
            self._load_sentence_transformer()

    def _load_sentence_transformer(self):
        """Load a sentence-transformers model"""
        from sentence_transformers import SentenceTransformer

        logger.info(f"Loading sentence-transformers model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self.dimension}")

    def _load_openai(self):
        """Configure OpenAI embeddings"""
        import openai

        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment")

        openai.api_key = Config.OPENAI_API_KEY
        self.model = "openai"
        self.dimension = 1536  # text-embedding-ada-002 dimension
        logger.info("OpenAI embeddings configured")

    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for text

        Args:
            text: Single text string or list of texts

        Returns:
            numpy array of embeddings
        """
        self._load_model()

        if isinstance(text, str):
            text = [text]

        if self.model_name == "openai":
            return self._embed_openai(text)
        else:
            return self._embed_sentence_transformer(text)

    def _embed_sentence_transformer(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using sentence-transformers"""
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 10
        )
        return embeddings

    def _embed_openai(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using OpenAI API"""
        import openai

        embeddings = []
        for text in texts:
            response = openai.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            embeddings.append(response.data[0].embedding)

        return np.array(embeddings)

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Similarity score (0-1)
        """
        # Normalize
        embedding1 = embedding1 / np.linalg.norm(embedding1)
        embedding2 = embedding2 / np.linalg.norm(embedding2)

        # Cosine similarity
        return float(np.dot(embedding1, embedding2))

    def batch_embed(
        self,
        texts: List[str],
        batch_size: int = None
    ) -> np.ndarray:
        """
        Generate embeddings in batches

        Args:
            texts: List of texts
            batch_size: Batch size for processing

        Returns:
            numpy array of embeddings
        """
        batch_size = batch_size or Config.BATCH_SIZE
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.embed_text(batch)
            all_embeddings.append(embeddings)

            if i % (batch_size * 10) == 0:
                logger.info(f"Embedded {i}/{len(texts)} texts")

        return np.vstack(all_embeddings) if all_embeddings else np.array([])
