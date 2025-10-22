# EddiGits Quick Start

Get up and running with EddiGits in 5 minutes.

## Installation

```bash
# 1. Install FFmpeg
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS

# 2. Install EddiGits
git clone https://github.com/yourusername/EddiGits.git
cd EddiGits
pip install -r requirements.txt

# 3. Configure API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY or OPENAI_API_KEY
```

## Process Your First Video

```bash
# Transcribe a video
python -m eddigits.cli transcribe my_video.mp4

# Or a folder of videos
python -m eddigits.cli transcribe ./videos/ --recursive
```

## Query Your Videos

```bash
# Ask a question
python -m eddigits.cli query "Where was the deadline discussed?"

# Interactive mode
python -m eddigits.cli interactive
```

## That's It!

You now have:
- ✅ Videos transcribed with AI
- ✅ Semantic search across all content
- ✅ Natural language querying
- ✅ Precise timestamps for every mention

## What's Next?

- Read the [full usage guide](USAGE.md)
- Check out [examples](EXAMPLES.md)
- Learn about [advanced features](ADVANCED.md)

## Common Commands

```bash
# View statistics
python -m eddigits.cli stats

# List all videos
python -m eddigits.cli list-videos

# Delete a video
python -m eddigits.cli delete VIDEO_ID

# Get help
python -m eddigits.cli --help
```

## Example Queries

```bash
# Find mentions
eddigits query "Where is Sarah mentioned?"

# Find topics
eddigits query "What was said about the budget?"

# Find sentiments
eddigits query "Where did I receive positive feedback?"

# Find decisions
eddigits query "What did we decide about the launch date?"
```

## Troubleshooting

**FFmpeg not found:**
```bash
# Install FFmpeg first
sudo apt install ffmpeg
```

**API key error:**
```bash
# Make sure .env file exists and has your API key
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Out of memory:**
```bash
# Use a smaller Whisper model
python -m eddigits.cli transcribe video.mp4 --model tiny
```

**Slow transcription:**
```bash
# Use GPU if available
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Need Help?

- Check [full documentation](USAGE.md)
- See [examples](EXAMPLES.md)
- Open an issue on GitHub
