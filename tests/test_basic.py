"""
Basic tests for EddiGits
"""

import pytest
from pathlib import Path
import tempfile
import sqlite3

from eddigits.config import Config
from eddigits.storage import VideoDatabase
from eddigits.transcriber import Transcript, TranscriptSegment


def test_config():
    """Test configuration"""
    assert Config.WHISPER_MODEL in ['tiny', 'base', 'small', 'medium', 'large']
    assert Config.CHUNK_SIZE > 0
    assert Config.OVERLAP >= 0


def test_database_init():
    """Test database initialization"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = VideoDatabase(db_path)

        # Check tables exist
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()

        assert 'videos' in tables
        assert 'segments' in tables
        assert 'chunks' in tables


def test_add_video():
    """Test adding a video"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = VideoDatabase(db_path)

        video_id = db.add_video(
            file_path="/path/to/video.mp4",
            file_name="video.mp4",
            file_size=1024,
            duration=60.0,
            language="en"
        )

        assert video_id > 0

        # Retrieve video
        video = db.get_video(video_id)
        assert video['file_name'] == "video.mp4"
        assert video['language'] == "en"


def test_transcript():
    """Test transcript creation"""
    segments = [
        TranscriptSegment(0.0, 5.0, "Hello world"),
        TranscriptSegment(5.0, 10.0, "This is a test"),
    ]

    transcript = Transcript(
        video_path="/path/to/video.mp4",
        language="en",
        segments=segments,
        full_text="Hello world This is a test"
    )

    assert len(transcript.segments) == 2
    assert transcript.language == "en"
    assert "Hello world" in transcript.full_text


def test_transcript_serialization():
    """Test transcript to/from dict"""
    segments = [
        TranscriptSegment(0.0, 5.0, "Hello"),
    ]

    transcript = Transcript(
        video_path="/path/to/video.mp4",
        language="en",
        segments=segments,
        full_text="Hello"
    )

    # To dict
    data = transcript.to_dict()
    assert data['language'] == 'en'
    assert len(data['segments']) == 1

    # From dict
    transcript2 = Transcript.from_dict(data)
    assert transcript2.language == transcript.language
    assert len(transcript2.segments) == len(transcript.segments)


def test_add_transcript():
    """Test adding transcript to database"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = VideoDatabase(db_path)

        segments = [
            TranscriptSegment(0.0, 5.0, "Hello world"),
            TranscriptSegment(5.0, 10.0, "This is a test"),
        ]

        transcript = Transcript(
            video_path="/path/to/video.mp4",
            language="en",
            segments=segments,
            full_text="Hello world This is a test"
        )

        video_id = db.add_transcript(transcript)
        assert video_id > 0

        # Retrieve segments
        segments_data = db.get_segments(video_id)
        assert len(segments_data) == 2
        assert segments_data[0]['text'] == "Hello world"


def test_get_transcript():
    """Test retrieving transcript"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = VideoDatabase(db_path)

        segments = [
            TranscriptSegment(0.0, 5.0, "Hello"),
        ]

        transcript = Transcript(
            video_path="/path/to/video.mp4",
            language="en",
            segments=segments,
            full_text="Hello"
        )

        video_id = db.add_transcript(transcript)

        # Retrieve
        retrieved = db.get_transcript(video_id)
        assert retrieved is not None
        assert retrieved.language == "en"
        assert len(retrieved.segments) == 1
        assert retrieved.segments[0].text == "Hello"


def test_search_text():
    """Test simple text search"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = VideoDatabase(db_path)

        segments = [
            TranscriptSegment(0.0, 5.0, "machine learning is great"),
            TranscriptSegment(5.0, 10.0, "deep learning too"),
        ]

        transcript = Transcript(
            video_path="/path/to/video.mp4",
            language="en",
            segments=segments,
            full_text="machine learning is great deep learning too"
        )

        db.add_transcript(transcript)

        # Search
        results = db.search_text("machine learning")
        assert len(results) > 0
        assert "machine learning" in results[0]['text']


def test_stats():
    """Test database statistics"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = VideoDatabase(db_path)

        # Empty stats
        stats = db.get_stats()
        assert stats['videos'] == 0
        assert stats['segments'] == 0

        # Add data
        segments = [TranscriptSegment(0.0, 60.0, "Test")]
        transcript = Transcript(
            video_path="/path/to/video.mp4",
            language="en",
            segments=segments,
            full_text="Test"
        )
        db.add_transcript(transcript)

        # Check stats
        stats = db.get_stats()
        assert stats['videos'] == 1
        assert stats['segments'] == 1
        assert stats['total_duration'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
