"""
Configuration management for EddiGits
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"

    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # Database paths
    DB_PATH: Path = Path(os.getenv("DB_PATH", "./data/eddigits.db"))
    VECTOR_DB_PATH: Path = Path(os.getenv("VECTOR_DB_PATH", "./data/chromadb"))

    # Whisper configuration
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    WHISPER_DEVICE: str = os.getenv("WHISPER_DEVICE", "cpu")  # or "cuda"

    # Processing configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "30"))  # seconds
    OVERLAP: int = int(os.getenv("OVERLAP", "5"))  # seconds
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "8"))

    # Embedding configuration
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    # LLM configuration
    LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-3-5-sonnet-20241022")

    # Search configuration
    TOP_K: int = int(os.getenv("TOP_K", "10"))
    MIN_SIMILARITY: float = float(os.getenv("MIN_SIMILARITY", "0.5"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        cls.VECTOR_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []

        # Check if at least one API key is present for LLM
        if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
            errors.append(
                "No API key found. Set either OPENAI_API_KEY or ANTHROPIC_API_KEY"
            )

        # Check Whisper model
        valid_models = ["tiny", "base", "small", "medium", "large"]
        if cls.WHISPER_MODEL not in valid_models:
            errors.append(
                f"Invalid WHISPER_MODEL. Must be one of: {', '.join(valid_models)}"
            )

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

        return True


# Initialize directories on import
Config.ensure_directories()
