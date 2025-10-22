# EddiGits Examples

Practical examples of using EddiGits for video analysis.

## Example Queries

### Finding Specific Mentions

**Query:** "Where is John Smith mentioned?"

**Result:**
```
Video: team_meeting_2024.mp4
Time: 00:15:32 - 00:16:02
Match: 94%
Content: "John Smith presented the Q3 results and highlighted..."
```

### Sentiment Analysis

**Query:** "Where was I appreciated or received positive feedback?"

**Result:**
```
Video: performance_review.mp4
Time: 00:08:15 - 00:08:45
Match: 88%
Content: "I really want to thank you for your excellent work on..."

Video: team_standup.mp4
Time: 00:12:30 - 00:12:50
Match: 85%
Content: "Great job handling that difficult situation, really appreciated..."
```

### Topic Search

**Query:** "What did we discuss about the project deadline?"

**Answer:**
The project deadline was discussed in multiple videos. In project_planning.mp4 at 00:23:15, the team agreed to extend the deadline to March 15th due to scope changes. In client_call.mp4 at 00:45:30, the client confirmed they were comfortable with the new timeline.

### Finding Decisions

**Query:** "Where did we decide on the technology stack?"

**Answer:**
The technology stack decision was made in architecture_meeting.mp4 at 00:18:20 - 00:22:40. The team chose React for frontend, Node.js for backend, and PostgreSQL for the database. The decision was based on team expertise and project requirements.

## Use Cases

### 1. Meeting Notes Recovery

**Scenario:** You attended many meetings but didn't take detailed notes.

```bash
# Find where budget was discussed
eddigits query "What was said about the budget?"

# Find action items assigned to you
eddigits query "What tasks were assigned to me?"

# Find decisions made
eddigits query "What decisions were made about the product roadmap?"
```

### 2. Interview Analysis

**Scenario:** You conducted user interviews and want to find patterns.

```bash
# Find pain points
eddigits query "What problems did users mention?"

# Find feature requests
eddigits query "What features did users request?"

# Find positive feedback
eddigits query "What did users like about the product?"
```

### 3. Course/Tutorial Navigation

**Scenario:** You recorded lectures or tutorials.

```bash
# Find specific topics
eddigits query "Where is linear regression explained?"

# Find code examples
eddigits query "Where is the authentication code shown?"

# Find tips and best practices
eddigits query "What best practices were mentioned?"
```

### 4. Content Creation

**Scenario:** You have video content and want to create documentation.

```bash
# Extract key points
eddigits query "What are the main points discussed?"

# Find quotes
eddigits query "What did the expert say about climate change?"

# Create summaries
eddigits query "Summarize the discussion about AI ethics"
```

## Python API Examples

### Basic Transcription

```python
from eddigits import VideoTranscriber

# Initialize transcriber
transcriber = VideoTranscriber(model_name="base")

# Transcribe a video
transcript = transcriber.transcribe("meeting.mp4")

# Access segments
for segment in transcript.segments:
    print(f"{segment.start:.1f}s: {segment.text}")

# Save transcript
transcript.save_to_file("meeting_transcript.json")
```

### Batch Processing

```python
from eddigits import VideoTranscriber
from pathlib import Path

transcriber = VideoTranscriber()

# Get all videos in a folder
videos = list(Path("videos").glob("*.mp4"))

# Transcribe all
transcripts = transcriber.transcribe_batch(videos)

print(f"Processed {len(transcripts)} videos")
```

### Database Storage

```python
from eddigits import VideoDatabase, VideoTranscriber

transcriber = VideoTranscriber()
db = VideoDatabase()

# Transcribe and store
transcript = transcriber.transcribe("video.mp4")
video_id = db.add_transcript(transcript)

# Query database
videos = db.get_all_videos()
for video in videos:
    print(f"{video['file_name']}: {video['duration']:.1f}s")
```

### Vector Search

```python
from eddigits import VectorIndexer, VideoDatabase

db = VideoDatabase()
indexer = VectorIndexer()

# Get transcript
transcript = db.get_transcript(video_id=1)

# Index for search
indexer.index_transcript(transcript, video_id=1)

# Search
results = indexer.search("machine learning", top_k=5)
for result in results:
    print(f"Match: {result['similarity']:.1%}")
    print(f"Text: {result['text'][:100]}...")
```

### Full Query Pipeline

```python
from eddigits import QueryEngine

# Initialize engine
engine = QueryEngine()

# Ask questions
result = engine.query("Where was the budget discussed?")

print(f"Question: {result['question']}")
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']}")

# Show supporting evidence
for evidence in result['results']:
    print(f"\nVideo: {evidence['video_name']}")
    print(f"Time: {evidence['timestamp_range']}")
    print(f"Content: {evidence['text'][:200]}")
```

### Custom Processing Pipeline

```python
from eddigits import (
    VideoTranscriber,
    VideoDatabase,
    VectorIndexer,
    QueryEngine
)
from pathlib import Path

def process_video_library(video_dir: Path):
    """Process all videos in a directory"""
    # Initialize components
    transcriber = VideoTranscriber(model_name="medium")
    db = VideoDatabase()
    indexer = VectorIndexer()

    # Find videos
    videos = list(video_dir.glob("*.mp4"))

    for video in videos:
        print(f"Processing {video.name}...")

        # Transcribe
        transcript = transcriber.transcribe(video)

        # Store
        video_id = db.add_transcript(transcript)

        # Index
        indexer.index_transcript(transcript, video_id)

        print(f"✓ {video.name} complete")

    # Now query
    engine = QueryEngine()
    result = engine.query("What are the main topics discussed?")
    print(f"\nAnswer: {result['answer']}")

# Run pipeline
process_video_library(Path("./my_videos"))
```

### Advanced: Custom Chunking

```python
from eddigits import VectorIndexer, VideoDatabase

indexer = VectorIndexer()
db = VideoDatabase()

transcript = db.get_transcript(video_id=1)

# Custom chunk size and overlap
chunks = indexer.create_chunks(
    transcript,
    chunk_size=60,  # 1 minute chunks
    overlap=10      # 10 seconds overlap
)

print(f"Created {len(chunks)} chunks")

# Index with custom settings
indexer.index_transcript(
    transcript,
    video_id=1,
    chunk_size=60,
    overlap=10
)
```

### Advanced: Direct LLM Integration

```python
from eddigits import QueryEngine

engine = QueryEngine()

# Get video summary
video_id = 1
summary = engine.get_video_summary(video_id)
print(f"Summary: {summary}")

# Search without LLM analysis
result = engine.query(
    "machine learning",
    use_llm=False  # Just return raw matches
)

# Process results yourself
for match in result['results']:
    print(f"{match['video_name']}: {match['text'][:100]}")
```

## Tips for Best Results

### 1. Be Specific

❌ Bad: "Find something about the project"
✅ Good: "What did we decide about the project timeline?"

### 2. Use Natural Language

❌ Bad: "deadline date meeting"
✅ Good: "When is the project deadline?"

### 3. Ask About Sentiments

✅ "Where was I praised?"
✅ "What concerns were raised?"
✅ "What feedback did the client give?"

### 4. Temporal Queries

✅ "What happened after we discussed the budget?"
✅ "What was mentioned before the break?"

### 5. Multi-Part Questions

✅ "Who attended and what did they say about the proposal?"
✅ "What features were requested and why?"

## Performance Tips

### Speed Up Transcription

1. Use smaller Whisper models for drafts
2. Use GPU if available
3. Specify language to skip detection
4. Process videos in parallel

```python
# Use tiny model for quick drafts
transcriber = VideoTranscriber(model_name="tiny")

# Use GPU
transcriber = VideoTranscriber(device="cuda")

# Specify language
transcript = transcriber.transcribe("video.mp4", language="en")
```

### Optimize Search

1. Adjust `MIN_SIMILARITY` threshold
2. Use smaller `TOP_K` for focused results
3. Use `--no-llm` for faster searches

```bash
# Faster, more focused
eddigits query "topic" --top-k 3 --min-similarity 0.7 --no-llm
```

### Save Costs

1. Use Claude instead of GPT-4 (cheaper, same quality)
2. Use local embeddings (sentence-transformers)
3. Skip LLM for simple searches

```env
# In .env
LLM_MODEL=claude-3-5-sonnet-20241022
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```
