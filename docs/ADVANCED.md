# Advanced Features

Advanced configuration and usage patterns for EddiGits.

## Custom Embedding Models

### Using Different Sentence Transformers

```env
# Fast and lightweight (default)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Better quality, slower
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2

# Multilingual support
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

### Using OpenAI Embeddings

```env
EMBEDDING_MODEL=openai
OPENAI_API_KEY=your-key-here
```

### Custom Model in Code

```python
from eddigits import EmbeddingManager

# Use custom model
embedder = EmbeddingManager(model_name="your-model-name")

# Generate embeddings
embeddings = embedder.embed_text(["text1", "text2"])
```

## Custom Chunking Strategies

### Time-Based Chunking

```python
from eddigits import VectorIndexer

indexer = VectorIndexer()

# Long chunks for context
chunks = indexer.create_chunks(
    transcript,
    chunk_size=120,  # 2 minutes
    overlap=30       # 30 seconds overlap
)

# Short chunks for precision
chunks = indexer.create_chunks(
    transcript,
    chunk_size=15,   # 15 seconds
    overlap=3        # 3 seconds overlap
)
```

### Semantic Chunking

```python
def semantic_chunk(transcript, max_words=100):
    """Chunk by sentence boundaries"""
    chunks = []
    current_chunk = []
    current_time = 0
    word_count = 0

    for segment in transcript.segments:
        words = segment.text.split()
        word_count += len(words)
        current_chunk.append(segment)

        # Chunk on sentence boundaries
        if word_count >= max_words and segment.text.rstrip().endswith(('.', '!', '?')):
            # Create chunk
            text = " ".join(s.text for s in current_chunk)
            chunks.append({
                "start": current_chunk[0].start,
                "end": current_chunk[-1].end,
                "text": text
            })

            # Reset
            current_chunk = []
            word_count = 0

    return chunks
```

## Multi-Modal Processing

### Extract Video Frames

```python
import cv2
from pathlib import Path

def extract_keyframes(video_path, interval=5):
    """Extract frames at regular intervals"""
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval)

    frames = []
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            timestamp = frame_count / fps
            frames.append({
                "timestamp": timestamp,
                "frame": frame
            })

        frame_count += 1

    cap.release()
    return frames
```

### Combine Text and Visual Search

```python
from eddigits import QueryEngine

# Text-based search
text_engine = QueryEngine()
text_results = text_engine.search("machine learning")

# Get corresponding video frames
for result in text_results:
    video_path = result.video_path
    timestamp = result.start_time

    # Extract frame at that timestamp
    frames = extract_keyframes(video_path, interval=1)
    # Process frames with vision model...
```

## Parallel Processing

### Batch Transcription with Multiprocessing

```python
from eddigits import VideoTranscriber, VideoDatabase, VectorIndexer
from pathlib import Path
from multiprocessing import Pool
import logging

def process_single_video(video_path):
    """Process a single video (runs in separate process)"""
    try:
        transcriber = VideoTranscriber()
        db = VideoDatabase()
        indexer = VectorIndexer()

        # Transcribe
        transcript = transcriber.transcribe(video_path)

        # Store and index
        video_id = db.add_transcript(transcript)
        indexer.index_transcript(transcript, video_id)

        return f"✓ {video_path.name}"
    except Exception as e:
        return f"✗ {video_path.name}: {e}"

def process_videos_parallel(video_dir, num_workers=4):
    """Process multiple videos in parallel"""
    videos = list(Path(video_dir).glob("*.mp4"))

    with Pool(processes=num_workers) as pool:
        results = pool.map(process_single_video, videos)

    for result in results:
        print(result)

# Usage
process_videos_parallel("./videos", num_workers=4)
```

## Custom Query Processing

### Multi-Step Reasoning

```python
from eddigits import QueryEngine

class AdvancedQueryEngine(QueryEngine):
    def multi_step_query(self, question):
        """Break down complex questions"""
        # Step 1: Identify sub-questions
        sub_questions = self._decompose_question(question)

        # Step 2: Query each sub-question
        all_results = []
        for sub_q in sub_questions:
            results = self.search(sub_q)
            all_results.extend(results)

        # Step 3: Synthesize final answer
        return self._synthesize_answer(question, all_results)

    def _decompose_question(self, question):
        """Use LLM to break down complex questions"""
        prompt = f"""Break down this question into simpler sub-questions:

Question: {question}

Sub-questions:
1."""

        # Call LLM to get sub-questions
        # ...
        return sub_questions

    def _synthesize_answer(self, question, results):
        """Synthesize answer from multiple results"""
        # Combine and analyze results
        # ...
        return final_answer
```

### Conversational Context

```python
class ConversationalQueryEngine(QueryEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation_history = []

    def query_with_context(self, question):
        """Query with conversation context"""
        # Add context from previous questions
        context = "\n".join(self.conversation_history[-3:])

        augmented_question = f"""Previous context:
{context}

Current question: {question}"""

        result = self.query(augmented_question)

        # Store in history
        self.conversation_history.append(
            f"Q: {question}\nA: {result['answer']}"
        )

        return result
```

## Custom Storage Backends

### PostgreSQL Instead of SQLite

```python
from sqlalchemy import create_engine
from eddigits.storage import VideoDatabase

class PostgreSQLVideoDatabase(VideoDatabase):
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self._init_database()

    # Override methods to use PostgreSQL
    # ...

# Usage
db = PostgreSQLVideoDatabase(
    "postgresql://user:password@localhost/eddigits"
)
```

### Cloud Storage for Videos

```python
import boto3
from pathlib import Path

class S3VideoProcessor:
    def __init__(self, bucket_name):
        self.s3 = boto3.client('s3')
        self.bucket = bucket_name

    def process_s3_video(self, s3_key):
        """Download, process, and cleanup"""
        # Download from S3
        local_path = f"/tmp/{Path(s3_key).name}"
        self.s3.download_file(self.bucket, s3_key, local_path)

        # Process
        transcriber = VideoTranscriber()
        transcript = transcriber.transcribe(local_path)

        # Cleanup
        Path(local_path).unlink()

        return transcript
```

## API Server Mode

### Flask REST API

```python
from flask import Flask, request, jsonify
from eddigits import QueryEngine, VideoTranscriber
from pathlib import Path

app = Flask(__name__)
engine = QueryEngine()
transcriber = VideoTranscriber()

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Transcribe a video"""
    video_file = request.files['video']
    temp_path = f"/tmp/{video_file.filename}"

    video_file.save(temp_path)
    transcript = transcriber.transcribe(temp_path)
    Path(temp_path).unlink()

    return jsonify(transcript.to_dict())

@app.route('/query', methods=['POST'])
def query():
    """Query the video library"""
    data = request.json
    result = engine.query(data['question'])
    return jsonify(result)

@app.route('/search', methods=['POST'])
def search():
    """Search videos"""
    data = request.json
    results = engine.search(
        data['query'],
        top_k=data.get('top_k', 10)
    )
    return jsonify([r.to_dict() for r in results])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### FastAPI with Async

```python
from fastapi import FastAPI, UploadFile, File
from eddigits import QueryEngine
import asyncio

app = FastAPI()
engine = QueryEngine()

@app.post("/query")
async def query(question: str):
    """Query endpoint"""
    result = await asyncio.to_thread(
        engine.query,
        question
    )
    return result

@app.get("/videos")
async def list_videos():
    """List all videos"""
    videos = await asyncio.to_thread(
        engine.db.get_all_videos
    )
    return videos
```

## Monitoring and Analytics

### Track Query Performance

```python
import time
from functools import wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper

class MonitoredQueryEngine(QueryEngine):
    @timing_decorator
    def query(self, *args, **kwargs):
        return super().query(*args, **kwargs)

    @timing_decorator
    def search(self, *args, **kwargs):
        return super().search(*args, **kwargs)
```

### Usage Analytics

```python
import json
from datetime import datetime

class AnalyticsQueryEngine(QueryEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.analytics_file = "query_analytics.json"

    def query(self, question, *args, **kwargs):
        # Execute query
        start = time.time()
        result = super().query(question, *args, **kwargs)
        elapsed = time.time() - start

        # Log analytics
        self._log_query(question, result, elapsed)

        return result

    def _log_query(self, question, result, elapsed):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "num_results": len(result['results']),
            "elapsed_time": elapsed,
            "confidence": result['confidence']
        }

        # Append to file
        with open(self.analytics_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
```

## Integration Examples

### Slack Bot

```python
from slack_bolt import App
from eddigits import QueryEngine

app = App(token="YOUR_TOKEN")
engine = QueryEngine()

@app.message("search:")
def handle_search(message, say):
    query = message['text'].replace("search:", "").strip()
    result = engine.query(query)

    say(f"*Answer:* {result['answer']}\n\n*Sources:*")
    for res in result['results'][:3]:
        say(f"• {res['video_name']} at {res['timestamp']}")

app.start(port=3000)
```

### Discord Bot

```python
import discord
from eddigits import QueryEngine

client = discord.Client()
engine = QueryEngine()

@client.event
async def on_message(message):
    if message.content.startswith('!search'):
        query = message.content[8:].strip()
        result = engine.query(query)

        await message.channel.send(f"**Answer:** {result['answer']}")

client.run('YOUR_TOKEN')
```

### VS Code Extension

```javascript
// extension.js
const vscode = require('vscode');
const { exec } = require('child_process');

function activate(context) {
    let disposable = vscode.commands.registerCommand(
        'eddigits.query',
        async function () {
            const query = await vscode.window.showInputBox({
                prompt: 'Enter your search query'
            });

            if (query) {
                exec(
                    `python -m eddigits.cli query "${query}"`,
                    (error, stdout, stderr) => {
                        if (error) {
                            vscode.window.showErrorMessage(stderr);
                        } else {
                            vscode.window.showInformationMessage(stdout);
                        }
                    }
                );
            }
        }
    );

    context.subscriptions.push(disposable);
}

module.exports = { activate };
```

## Performance Optimization

### Caching

```python
from functools import lru_cache
from eddigits import QueryEngine

class CachedQueryEngine(QueryEngine):
    @lru_cache(maxsize=100)
    def search(self, query, top_k=10, **kwargs):
        return super().search(query, top_k)

    def clear_cache(self):
        self.search.cache_clear()
```

### Batch Embedding

```python
# Process in larger batches
embedder = EmbeddingManager()
texts = ["text1", "text2", ...]  # 1000s of texts

# Batch embed
embeddings = embedder.batch_embed(texts, batch_size=64)
```

### GPU Acceleration

```python
# Use GPU for Whisper
transcriber = VideoTranscriber(device="cuda")

# Use GPU for embeddings
import torch
embedder = EmbeddingManager()
embedder.model = embedder.model.to('cuda')
```

## Security Best Practices

### Sanitize User Input

```python
import re

def sanitize_query(query):
    """Prevent injection attacks"""
    # Remove SQL special characters
    query = re.sub(r'[;\'"\\]', '', query)
    # Limit length
    query = query[:500]
    return query.strip()

result = engine.query(sanitize_query(user_input))
```

### Rate Limiting

```python
from time import time
from collections import defaultdict

class RateLimitedQueryEngine(QueryEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requests = defaultdict(list)
        self.limit = 10  # requests per minute

    def query(self, question, user_id=None):
        if user_id and not self._check_rate_limit(user_id):
            raise Exception("Rate limit exceeded")

        return super().query(question)

    def _check_rate_limit(self, user_id):
        now = time()
        # Remove old requests
        self.requests[user_id] = [
            t for t in self.requests[user_id]
            if now - t < 60
        ]
        # Check limit
        if len(self.requests[user_id]) >= self.limit:
            return False
        # Add new request
        self.requests[user_id].append(now)
        return True
```
