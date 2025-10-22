"""
Video transcription using OpenAI Whisper
"""

import whisper
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import json

from .config import Config

logger = logging.getLogger(__name__)


@dataclass
class TranscriptSegment:
    """A segment of transcribed text with timing information"""
    start: float  # seconds
    end: float    # seconds
    text: str

    def to_dict(self) -> dict:
        return {
            "start": self.start,
            "end": self.end,
            "text": self.text
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TranscriptSegment":
        return cls(
            start=data["start"],
            end=data["end"],
            text=data["text"]
        )


@dataclass
class Transcript:
    """Complete transcript of a video"""
    video_path: str
    language: str
    segments: List[TranscriptSegment]
    full_text: str

    def to_dict(self) -> dict:
        return {
            "video_path": self.video_path,
            "language": self.language,
            "segments": [s.to_dict() for s in self.segments],
            "full_text": self.full_text
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transcript":
        return cls(
            video_path=data["video_path"],
            language=data["language"],
            segments=[TranscriptSegment.from_dict(s) for s in data["segments"]],
            full_text=data["full_text"]
        )

    def save_to_file(self, output_path: Union[str, Path]):
        """Save transcript to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, file_path: Union[str, Path]) -> "Transcript":
        """Load transcript from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


class VideoTranscriber:
    """Handles video transcription using Whisper"""

    def __init__(
        self,
        model_name: str = None,
        device: str = None
    ):
        """
        Initialize the transcriber

        Args:
            model_name: Whisper model to use (tiny, base, small, medium, large)
            device: Device to run on ('cpu' or 'cuda')
        """
        self.model_name = model_name or Config.WHISPER_MODEL
        self.device = device or Config.WHISPER_DEVICE
        self.model = None

        logger.info(f"Initializing Whisper model: {self.model_name} on {self.device}")

    def _load_model(self):
        """Lazy load the Whisper model"""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name, device=self.device)
            logger.info("Model loaded successfully")

    def transcribe(
        self,
        video_path: Union[str, Path],
        language: Optional[str] = None,
        verbose: bool = True
    ) -> Transcript:
        """
        Transcribe a video file

        Args:
            video_path: Path to the video file
            language: Language code (e.g., 'en', 'es'). Auto-detect if None
            verbose: Show progress information

        Returns:
            Transcript object with segments and timing
        """
        self._load_model()

        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        logger.info(f"Transcribing: {video_path.name}")

        # Transcribe with Whisper
        result = self.model.transcribe(
            str(video_path),
            language=language,
            verbose=verbose,
            word_timestamps=True  # Get word-level timestamps
        )

        # Convert to our format
        segments = []
        for segment in result["segments"]:
            segments.append(TranscriptSegment(
                start=segment["start"],
                end=segment["end"],
                text=segment["text"].strip()
            ))

        transcript = Transcript(
            video_path=str(video_path),
            language=result["language"],
            segments=segments,
            full_text=result["text"]
        )

        logger.info(
            f"Transcription complete: {len(segments)} segments, "
            f"language: {result['language']}"
        )

        return transcript

    def transcribe_batch(
        self,
        video_paths: List[Union[str, Path]],
        language: Optional[str] = None,
        verbose: bool = True
    ) -> List[Transcript]:
        """
        Transcribe multiple video files

        Args:
            video_paths: List of video file paths
            language: Language code (e.g., 'en', 'es'). Auto-detect if None
            verbose: Show progress information

        Returns:
            List of Transcript objects
        """
        transcripts = []
        total = len(video_paths)

        for i, video_path in enumerate(video_paths, 1):
            logger.info(f"Processing {i}/{total}: {Path(video_path).name}")
            try:
                transcript = self.transcribe(video_path, language, verbose)
                transcripts.append(transcript)
            except Exception as e:
                logger.error(f"Failed to transcribe {video_path}: {e}")
                continue

        return transcripts

    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """
        Convert seconds to HH:MM:SS format

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def get_segment_at_time(self, transcript: Transcript, time_seconds: float) -> Optional[TranscriptSegment]:
        """
        Find the segment at a specific time

        Args:
            transcript: Transcript object
            time_seconds: Time in seconds

        Returns:
            TranscriptSegment or None
        """
        for segment in transcript.segments:
            if segment.start <= time_seconds <= segment.end:
                return segment
        return None
