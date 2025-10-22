# EddiGits Usage Guide

Complete guide to using EddiGits for video transcription and analysis.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Transcribing Videos](#transcribing-videos)
4. [Querying Videos](#querying-videos)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

1. **Python 3.8+**
   ```bash
   python --version
   ```

2. **FFmpeg** (required for audio extraction)
   ```bash
   # Ubuntu/Debian
   sudo apt install ffmpeg

   # macOS
   brew install ffmpeg

   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

### Install EddiGits

```bash
# Clone the repository
git clone https://github.com/yourusername/EddiGits.git
cd EddiGits

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### GPU Support (Optional but Recommended)

For faster transcription with GPU:

```bash
# For CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## Configuration

### 1. Create `.env` file

Copy the example configuration:

```bash
cp .env.example .env
```

### 2. Add API Keys

Edit `.env` and add your API keys:

```env
# Choose ONE or BOTH:

# Option 1: Anthropic Claude (Recommended)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Option 2: OpenAI
OPENAI_API_KEY=sk-your-key-here
```

### 3. Adjust Settings (Optional)

```env
# Whisper model size (affects accuracy vs speed)
WHISPER_MODEL=base  # Options: tiny, base, small, medium, large

# Text chunking
CHUNK_SIZE=30  # seconds per chunk
OVERLAP=5      # seconds of overlap

# Search settings
TOP_K=10             # number of results
MIN_SIMILARITY=0.5   # minimum match threshold (0-1)
```

## Transcribing Videos

### Single Video

```bash
python -m eddigits.cli transcribe /path/to/video.mp4
```

### Multiple Videos in a Folder

```bash
# Non-recursive (only current directory)
python -m eddigits.cli transcribe /path/to/videos/

# Recursive (include subdirectories)
python -m eddigits.cli transcribe /path/to/videos/ --recursive
```

### Specify Language

```bash
# Auto-detect language (default)
python -m eddigits.cli transcribe video.mp4

# Specify language (faster, more accurate)
python -m eddigits.cli transcribe video.mp4 --language en
python -m eddigits.cli transcribe video.mp4 --language es
```

### Choose Whisper Model

```bash
# Faster but less accurate
python -m eddigits.cli transcribe video.mp4 --model tiny

# Balanced (default)
python -m eddigits.cli transcribe video.mp4 --model base

# More accurate but slower
python -m eddigits.cli transcribe video.mp4 --model medium
python -m eddigits.cli transcribe video.mp4 --model large
```

### Model Comparison

| Model  | Size   | RAM    | Speed          | Accuracy |
|--------|--------|--------|----------------|----------|
| tiny   | 39 MB  | ~1 GB  | Very Fast      | Good     |
| base   | 74 MB  | ~1 GB  | Fast           | Better   |
| small  | 244 MB | ~2 GB  | Moderate       | Good     |
| medium | 769 MB | ~5 GB  | Slow           | Very Good|
| large  | 1550 MB| ~10 GB | Very Slow      | Best     |

## Querying Videos

### Basic Query

```bash
python -m eddigits.cli query "Where was productivity mentioned?"
```

### Adjust Result Count

```bash
# Get more results
python -m eddigits.cli query "machine learning" --top-k 20

# Get fewer, more focused results
python -m eddigits.cli query "machine learning" --top-k 3
```

### Adjust Similarity Threshold

```bash
# Only high-confidence matches
python -m eddigits.cli query "feedback" --min-similarity 0.7

# Include lower-confidence matches
python -m eddigits.cli query "feedback" --min-similarity 0.3
```

### Raw Results (No LLM Analysis)

```bash
# Skip LLM analysis, just show matches
python -m eddigits.cli query "project timeline" --no-llm
```

## Interactive Mode

Start an interactive query session:

```bash
python -m eddigits.cli interactive
```

Example interaction:

```
You: Where was the budget discussed?