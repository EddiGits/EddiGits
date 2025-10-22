# EddiGits - AI-Powered Video Transcription & Analysis

A powerful system to transcribe videos with AI and perform intelligent searches across your video library.

## Features

- **Automatic Transcription**: Uses OpenAI Whisper for accurate speech-to-text with timestamps
- **Semantic Search**: Find content by meaning, not just keywords
- **Temporal Precision**: Get exact timestamps for every mention
- **Natural Language Queries**: Ask questions like "In which video was 'productivity' discussed?" or "Where was I appreciated?"
- **Multi-Video Analysis**: Search across your entire video library instantly

## Architecture

```
┌─────────────────┐
│  Video Files    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Whisper Engine  │ ◄── Transcription with timestamps
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQLite DB      │ ◄── Metadata & transcripts
│  + ChromaDB     │ ◄── Vector embeddings
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  RAG Pipeline   │ ◄── AI-powered query understanding
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Results       │ ◄── Video names + timestamps
└─────────────────┘
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For GPU support (optional but faster):
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Quick Start

### 1. Process Videos

```bash
# Transcribe a single video
python -m eddigits.cli transcribe path/to/video.mp4

# Transcribe all videos in a folder
python -m eddigits.cli transcribe path/to/videos/ --recursive

# Use a specific Whisper model (tiny, base, small, medium, large)
python -m eddigits.cli transcribe path/to/videos/ --model medium
```

### 2. Query Your Videos

```bash
# Ask natural language questions
python -m eddigits.cli query "Where was productivity mentioned?"

python -m eddigits.cli query "In which video was I appreciated?"

python -m eddigits.cli query "Show me all mentions of John Smith"
```

### 3. Interactive Mode

```bash
# Start interactive query session
python -m eddigits.cli interactive
```

## Configuration

Create a `.env` file in the project root:

```env
# OpenAI API Key (for embeddings and query understanding)
OPENAI_API_KEY=your_api_key_here

# Or use Anthropic Claude (recommended)
ANTHROPIC_API_KEY=your_api_key_here

# Database paths
DB_PATH=./data/eddigits.db
VECTOR_DB_PATH=./data/chromadb

# Whisper model size: tiny, base, small, medium, large
WHISPER_MODEL=base

# Processing settings
CHUNK_SIZE=30  # seconds per chunk
OVERLAP=5      # seconds of overlap between chunks
```

## How It Works

1. **Transcription**: Videos are processed through Whisper to extract text with precise timestamps
2. **Chunking**: Transcripts are split into semantic chunks with overlapping context
3. **Embedding**: Each chunk is converted to a vector embedding for semantic search
4. **Indexing**: Embeddings are stored in ChromaDB for fast retrieval
5. **Query Processing**: Your questions are converted to embeddings and matched against the database
6. **AI Analysis**: Results are analyzed by an LLM to provide accurate, contextual answers

## Requirements

- Python 3.8+
- FFmpeg (for audio extraction)
- 4GB+ RAM (8GB+ recommended for larger models)
- GPU optional but recommended for faster processing

## Examples

**Find specific mentions:**
```
Query: "Where is 'machine learning' discussed?"
Result:
  - Video: project_review_2024.mp4
    Time: 00:03:45 - 00:04:12
    Context: "...discussing the machine learning pipeline we built..."
```

**Sentiment analysis:**
```
Query: "Show me where I received positive feedback"
Result:
  - Video: team_meeting_jan.mp4
    Time: 00:15:30 - 00:15:45
    Context: "...great job on the presentation, really appreciated..."
```

## Advanced Usage

See [docs/ADVANCED.md](docs/ADVANCED.md) for:
- Custom embedding models
- Batch processing
- API server mode
- Integration with other tools

## License

MIT

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md)
