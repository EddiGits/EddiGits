"""
Database storage for video metadata and transcripts
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from contextlib import contextmanager

from .config import Config
from .transcriber import Transcript, TranscriptSegment

logger = logging.getLogger(__name__)


class VideoDatabase:
    """SQLite database for storing video metadata and transcripts"""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the database

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or Config.DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Videos table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_name TEXT NOT NULL,
                    file_size INTEGER,
                    duration REAL,
                    language TEXT,
                    transcribed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Segments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS segments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL NOT NULL,
                    text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (video_id) REFERENCES videos (id) ON DELETE CASCADE
                )
            """)

            # Chunks table (for embeddings)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL NOT NULL,
                    text TEXT NOT NULL,
                    vector_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (video_id) REFERENCES videos (id) ON DELETE CASCADE
                )
            """)

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_segments_video_id
                ON segments(video_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_segments_time
                ON segments(start_time, end_time)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_video_id
                ON chunks(video_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_vector_id
                ON chunks(vector_id)
            """)

            logger.info(f"Database initialized at {self.db_path}")

    def add_video(
        self,
        file_path: str,
        file_name: str,
        file_size: Optional[int] = None,
        duration: Optional[float] = None,
        language: Optional[str] = None
    ) -> int:
        """
        Add a video to the database

        Args:
            file_path: Full path to video file
            file_name: Name of the video file
            file_size: File size in bytes
            duration: Video duration in seconds
            language: Detected language

        Returns:
            Video ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if video already exists
            cursor.execute(
                "SELECT id FROM videos WHERE file_path = ?",
                (file_path,)
            )
            existing = cursor.fetchone()

            if existing:
                logger.info(f"Video already exists: {file_name}")
                return existing[0]

            # Insert new video
            cursor.execute("""
                INSERT INTO videos (file_path, file_name, file_size, duration, language, transcribed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (file_path, file_name, file_size, duration, language, datetime.now()))

            video_id = cursor.lastrowid
            logger.info(f"Added video: {file_name} (ID: {video_id})")
            return video_id

    def add_transcript(self, transcript: Transcript) -> int:
        """
        Add a transcript to the database

        Args:
            transcript: Transcript object

        Returns:
            Video ID
        """
        file_path = Path(transcript.video_path)

        # Get file info
        file_size = file_path.stat().st_size if file_path.exists() else None
        duration = transcript.segments[-1].end if transcript.segments else None

        # Add video
        video_id = self.add_video(
            file_path=str(file_path),
            file_name=file_path.name,
            file_size=file_size,
            duration=duration,
            language=transcript.language
        )

        # Add segments
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Clear existing segments
            cursor.execute("DELETE FROM segments WHERE video_id = ?", (video_id,))

            # Insert new segments
            for segment in transcript.segments:
                cursor.execute("""
                    INSERT INTO segments (video_id, start_time, end_time, text)
                    VALUES (?, ?, ?, ?)
                """, (video_id, segment.start, segment.end, segment.text))

            logger.info(f"Added {len(transcript.segments)} segments for video ID {video_id}")

        return video_id

    def get_video(self, video_id: int) -> Optional[Dict[str, Any]]:
        """Get video by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_video_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get video by file path"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM videos WHERE file_path = ?", (file_path,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_videos(self) -> List[Dict[str, Any]]:
        """Get all videos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM videos ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_segments(self, video_id: int) -> List[Dict[str, Any]]:
        """Get all segments for a video"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM segments
                WHERE video_id = ?
                ORDER BY start_time
            """, (video_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_transcript(self, video_id: int) -> Optional[Transcript]:
        """
        Reconstruct a Transcript object from the database

        Args:
            video_id: Video ID

        Returns:
            Transcript object or None
        """
        video = self.get_video(video_id)
        if not video:
            return None

        segments_data = self.get_segments(video_id)
        segments = [
            TranscriptSegment(
                start=s["start_time"],
                end=s["end_time"],
                text=s["text"]
            )
            for s in segments_data
        ]

        full_text = " ".join(s.text for s in segments)

        return Transcript(
            video_path=video["file_path"],
            language=video["language"],
            segments=segments,
            full_text=full_text
        )

    def add_chunk(
        self,
        video_id: int,
        start_time: float,
        end_time: float,
        text: str,
        vector_id: Optional[str] = None
    ) -> int:
        """
        Add a text chunk for embedding

        Args:
            video_id: Video ID
            start_time: Start time in seconds
            end_time: End time in seconds
            text: Chunk text
            vector_id: ID in vector database

        Returns:
            Chunk ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chunks (video_id, start_time, end_time, text, vector_id)
                VALUES (?, ?, ?, ?, ?)
            """, (video_id, start_time, end_time, text, vector_id))
            return cursor.lastrowid

    def get_chunks(self, video_id: int) -> List[Dict[str, Any]]:
        """Get all chunks for a video"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM chunks
                WHERE video_id = ?
                ORDER BY start_time
            """, (video_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_chunk_by_vector_id(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Get chunk by vector ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chunks WHERE vector_id = ?", (vector_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def search_text(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Simple text search across all segments

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching segments with video info
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    s.*,
                    v.file_name,
                    v.file_path,
                    v.language
                FROM segments s
                JOIN videos v ON s.video_id = v.id
                WHERE s.text LIKE ?
                ORDER BY s.start_time
                LIMIT ?
            """, (f"%{query}%", limit))
            return [dict(row) for row in cursor.fetchall()]

    def delete_video(self, video_id: int):
        """Delete a video and all its data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
            logger.info(f"Deleted video ID {video_id}")

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM videos")
            video_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM segments")
            segment_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM chunks")
            chunk_count = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(duration) FROM videos")
            total_duration = cursor.fetchone()[0] or 0

            return {
                "videos": video_count,
                "segments": segment_count,
                "chunks": chunk_count,
                "total_duration": total_duration,
                "total_duration_formatted": self._format_duration(total_duration)
            }

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration in human-readable format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"
