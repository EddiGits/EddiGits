"""
Setup configuration for EddiGits
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="eddigits",
    version="0.1.0",
    description="AI-Powered Video Transcription & Analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="EddiGits",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "openai-whisper>=20231117",
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
        "chromadb>=0.4.22",
        "sentence-transformers>=2.3.1",
        "openai>=1.10.0",
        "anthropic>=0.18.0",
        "sqlalchemy>=2.0.0",
        "ffmpeg-python>=0.2.0",
        "pydub>=0.25.1",
        "python-dotenv>=1.0.0",
        "tqdm>=4.66.0",
        "click>=8.1.0",
        "rich>=13.7.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "eddigits=eddigits.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="video transcription ai whisper semantic-search nlp",
)
