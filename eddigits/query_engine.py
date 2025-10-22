"""
AI-powered query engine using RAG (Retrieval Augmented Generation)
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .config import Config
from .storage import VideoDatabase
from .indexer import VectorIndexer

logger = logging.getLogger(__name__)


class QueryResult:
    """Represents a query result"""

    def __init__(
        self,
        video_name: str,
        video_path: str,
        start_time: float,
        end_time: float,
        text: str,
        similarity: float,
        context: Optional[str] = None
    ):
        self.video_name = video_name
        self.video_path = video_path
        self.start_time = start_time
        self.end_time = end_time
        self.text = text
        self.similarity = similarity
        self.context = context

    @property
    def timestamp(self) -> str:
        """Format timestamp as HH:MM:SS"""
        return self._format_time(self.start_time)

    @property
    def timestamp_range(self) -> str:
        """Format time range"""
        return f"{self._format_time(self.start_time)} - {self._format_time(self.end_time)}"

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Convert seconds to HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "video_name": self.video_name,
            "video_path": self.video_path,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "timestamp": self.timestamp,
            "timestamp_range": self.timestamp_range,
            "text": self.text,
            "similarity": self.similarity,
            "context": self.context
        }

    def __repr__(self) -> str:
        return (
            f"QueryResult(video={self.video_name}, "
            f"time={self.timestamp_range}, "
            f"similarity={self.similarity:.2f})"
        )


class QueryEngine:
    """AI-powered query engine for video transcripts"""

    def __init__(
        self,
        db_path: Optional[Path] = None,
        vector_db_path: Optional[Path] = None
    ):
        """
        Initialize the query engine

        Args:
            db_path: Path to SQLite database
            vector_db_path: Path to ChromaDB storage
        """
        self.db = VideoDatabase(db_path)
        self.indexer = VectorIndexer(vector_db_path)
        self.llm_client = None

        logger.info("Query engine initialized")

    def _init_llm(self):
        """Initialize LLM client (lazy loading)"""
        if self.llm_client is not None:
            return

        if Config.LLM_MODEL.startswith("claude"):
            self._init_claude()
        elif Config.LLM_MODEL.startswith("gpt"):
            self._init_openai()
        else:
            raise ValueError(f"Unsupported LLM model: {Config.LLM_MODEL}")

    def _init_claude(self):
        """Initialize Anthropic Claude client"""
        import anthropic

        if not Config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set")

        self.llm_client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.llm_type = "claude"
        logger.info("Claude client initialized")

    def _init_openai(self):
        """Initialize OpenAI client"""
        import openai

        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")

        openai.api_key = Config.OPENAI_API_KEY
        self.llm_client = openai
        self.llm_type = "openai"
        logger.info("OpenAI client initialized")

    def search(
        self,
        query: str,
        top_k: int = None,
        min_similarity: float = None
    ) -> List[QueryResult]:
        """
        Search for relevant video segments

        Args:
            query: Search query
            top_k: Number of results to return
            min_similarity: Minimum similarity score

        Returns:
            List of QueryResult objects
        """
        top_k = top_k or Config.TOP_K
        min_similarity = min_similarity or Config.MIN_SIMILARITY

        # Search vector database
        search_results = self.indexer.search(query, top_k=top_k * 2)

        # Convert to QueryResult objects
        query_results = []
        for result in search_results:
            # Filter by similarity
            if result["similarity"] < min_similarity:
                continue

            metadata = result["metadata"]
            video_id = int(metadata["video_id"])

            # Get video info from database
            video = self.db.get_video(video_id)
            if not video:
                continue

            query_results.append(QueryResult(
                video_name=video["file_name"],
                video_path=video["file_path"],
                start_time=metadata["start_time"],
                end_time=metadata["end_time"],
                text=result["text"],
                similarity=result["similarity"]
            ))

            if len(query_results) >= top_k:
                break

        logger.info(f"Found {len(query_results)} results for query: {query}")
        return query_results

    def query(
        self,
        question: str,
        top_k: int = None,
        min_similarity: float = None,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a natural language question about videos

        Args:
            question: Natural language question
            top_k: Number of results to consider
            min_similarity: Minimum similarity score
            use_llm: Whether to use LLM for analysis

        Returns:
            Dictionary with answer and supporting results
        """
        # Search for relevant segments
        results = self.search(question, top_k, min_similarity)

        if not results:
            return {
                "question": question,
                "answer": "No relevant information found in the video library.",
                "results": [],
                "confidence": "none"
            }

        # If not using LLM, return raw results
        if not use_llm:
            return {
                "question": question,
                "answer": None,
                "results": [r.to_dict() for r in results],
                "confidence": "n/a"
            }

        # Use LLM to analyze and answer
        try:
            self._init_llm()
            answer = self._generate_answer(question, results)

            return {
                "question": question,
                "answer": answer["text"],
                "results": [r.to_dict() for r in results],
                "confidence": answer.get("confidence", "medium")
            }
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "question": question,
                "answer": f"Error generating answer: {str(e)}",
                "results": [r.to_dict() for r in results],
                "confidence": "error"
            }

    def _generate_answer(
        self,
        question: str,
        results: List[QueryResult]
    ) -> Dict[str, Any]:
        """
        Generate an answer using LLM

        Args:
            question: User question
            results: Search results

        Returns:
            Dictionary with answer and metadata
        """
        # Build context from results
        context_parts = []
        for i, result in enumerate(results[:5], 1):  # Use top 5 results
            context_parts.append(
                f"[Result {i}]\n"
                f"Video: {result.video_name}\n"
                f"Time: {result.timestamp_range}\n"
                f"Content: {result.text}\n"
                f"Relevance: {result.similarity:.2f}\n"
            )

        context = "\n".join(context_parts)

        # Build prompt
        prompt = f"""You are analyzing video transcripts to answer user questions.
You have been given search results from a video library. Your task is to provide a clear, accurate answer based on the evidence provided.

User Question: {question}

Search Results:
{context}

Instructions:
1. Answer the question directly based on the evidence
2. Reference specific videos and timestamps
3. If multiple videos match, list them all
4. Be concise but informative
5. If the results don't clearly answer the question, say so

Provide your answer in this format:
ANSWER: [Your clear, direct answer]
CONFIDENCE: [high/medium/low based on evidence quality]
"""

        # Call LLM
        if self.llm_type == "claude":
            return self._call_claude(prompt)
        else:
            return self._call_openai(prompt)

    def _call_claude(self, prompt: str) -> Dict[str, Any]:
        """Call Claude API"""
        response = self.llm_client.messages.create(
            model=Config.LLM_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text

        # Parse response
        answer_text = text
        confidence = "medium"

        if "ANSWER:" in text:
            parts = text.split("ANSWER:", 1)[1]
            if "CONFIDENCE:" in parts:
                answer_text = parts.split("CONFIDENCE:")[0].strip()
                confidence = parts.split("CONFIDENCE:")[1].strip().lower()
            else:
                answer_text = parts.strip()

        return {
            "text": answer_text,
            "confidence": confidence
        }

    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API"""
        response = self.llm_client.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024
        )

        text = response.choices[0].message.content

        # Parse response
        answer_text = text
        confidence = "medium"

        if "ANSWER:" in text:
            parts = text.split("ANSWER:", 1)[1]
            if "CONFIDENCE:" in parts:
                answer_text = parts.split("CONFIDENCE:")[0].strip()
                confidence = parts.split("CONFIDENCE:")[1].strip().lower()
            else:
                answer_text = parts.strip()

        return {
            "text": answer_text,
            "confidence": confidence
        }

    def get_video_summary(self, video_id: int) -> Optional[str]:
        """
        Get a summary of a video

        Args:
            video_id: Video ID

        Returns:
            Summary text or None
        """
        transcript = self.db.get_transcript(video_id)
        if not transcript:
            return None

        # Get a sample of the transcript
        sample_text = transcript.full_text[:2000]

        try:
            self._init_llm()
            prompt = f"""Summarize this video transcript in 2-3 sentences:

{sample_text}

Summary:"""

            if self.llm_type == "claude":
                response = self.llm_client.messages.create(
                    model=Config.LLM_MODEL,
                    max_tokens=256,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            else:
                response = self.llm_client.chat.completions.create(
                    model=Config.LLM_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=256
                )
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return None
