"""
Command-line interface for EddiGits
"""

import click
import logging
from pathlib import Path
from typing import List
import sys

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.markdown import Markdown

from .config import Config
from .transcriber import VideoTranscriber
from .storage import VideoDatabase
from .indexer import VectorIndexer
from .query_engine import QueryEngine

console = Console()


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose):
    """EddiGits - AI-Powered Video Transcription & Analysis"""
    setup_logging(verbose)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--model', '-m', default=None, help='Whisper model (tiny, base, small, medium, large)')
@click.option('--language', '-l', default=None, help='Language code (e.g., en, es)')
@click.option('--recursive', '-r', is_flag=True, help='Process directory recursively')
def transcribe(path, model, language, recursive):
    """Transcribe video files"""
    path = Path(path)

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        sys.exit(1)

    # Find video files
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'}
    video_files = []

    if path.is_file():
        if path.suffix.lower() in video_extensions:
            video_files = [path]
        else:
            console.print(f"[yellow]Warning: {path.name} is not a recognized video file[/yellow]")
            return
    else:
        pattern = '**/*' if recursive else '*'
        for ext in video_extensions:
            video_files.extend(path.glob(f'{pattern}{ext}'))

    if not video_files:
        console.print("[yellow]No video files found[/yellow]")
        return

    console.print(f"[green]Found {len(video_files)} video(s) to process[/green]\n")

    # Initialize components
    transcriber = VideoTranscriber(model_name=model)
    db = VideoDatabase()
    indexer = VectorIndexer()

    # Process each video
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:

        for video_file in video_files:
            task = progress.add_task(f"Processing {video_file.name}...", total=None)

            try:
                # Check if already processed
                existing = db.get_video_by_path(str(video_file))
                if existing:
                    console.print(f"[yellow]Skipping {video_file.name} (already processed)[/yellow]")
                    progress.remove_task(task)
                    continue

                # Transcribe
                transcript = transcriber.transcribe(video_file, language=language, verbose=False)

                # Store in database
                video_id = db.add_transcript(transcript)

                # Index for search
                indexer.index_transcript(transcript, video_id)

                progress.remove_task(task)
                console.print(f"[green]✓ {video_file.name} processed successfully[/green]")

            except Exception as e:
                progress.remove_task(task)
                console.print(f"[red]✗ Failed to process {video_file.name}: {e}[/red]")
                continue

    console.print("\n[green]Processing complete![/green]")
    show_stats_internal()


@cli.command()
@click.argument('question')
@click.option('--top-k', '-k', default=None, type=int, help='Number of results')
@click.option('--min-similarity', '-s', default=None, type=float, help='Minimum similarity (0-1)')
@click.option('--no-llm', is_flag=True, help='Skip LLM analysis')
def query(question, top_k, min_similarity, no_llm):
    """Query the video library"""
    try:
        Config.validate()
    except ValueError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        sys.exit(1)

    engine = QueryEngine()

    with console.status("[bold green]Searching videos..."):
        result = engine.query(
            question,
            top_k=top_k,
            min_similarity=min_similarity,
            use_llm=not no_llm
        )

    # Display results
    console.print()
    console.print(Panel(f"[bold]{question}[/bold]", title="Question"))

    if result["answer"]:
        console.print()
        console.print(Panel(result["answer"], title="Answer", border_style="green"))

    if result["results"]:
        console.print()
        console.print("[bold]Supporting Evidence:[/bold]\n")

        for i, res in enumerate(result["results"], 1):
            table = Table(show_header=False, box=None, padding=(0, 1))
            table.add_column(style="cyan")
            table.add_column()

            table.add_row("Video:", f"[bold]{res['video_name']}[/bold]")
            table.add_row("Time:", res['timestamp_range'])
            table.add_row("Match:", f"{res['similarity']:.1%}")
            table.add_row("Content:", res['text'][:200] + "..." if len(res['text']) > 200 else res['text'])

            console.print(Panel(table, title=f"Result {i}"))
    else:
        console.print("\n[yellow]No results found[/yellow]")


@cli.command()
def interactive():
    """Start interactive query mode"""
    try:
        Config.validate()
    except ValueError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        sys.exit(1)

    engine = QueryEngine()

    console.print(Panel(
        "[bold green]EddiGits Interactive Mode[/bold green]\n\n"
        "Ask questions about your videos!\n"
        "Type 'exit' or 'quit' to leave.\n"
        "Type 'help' for tips.",
        border_style="blue"
    ))

    while True:
        try:
            question = console.input("\n[bold cyan]You:[/bold cyan] ").strip()

            if not question:
                continue

            if question.lower() in ['exit', 'quit', 'q']:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if question.lower() == 'help':
                show_help()
                continue

            # Query
            with console.status("[bold green]Thinking..."):
                result = engine.query(question)

            # Display
            if result["answer"]:
                console.print(f"\n[bold green]Assistant:[/bold green] {result['answer']}")

                if result["results"]:
                    console.print("\n[dim]Sources:[/dim]")
                    for res in result["results"][:3]:
                        console.print(
                            f"  [dim]• {res['video_name']} at {res['timestamp']} "
                            f"({res['similarity']:.0%} match)[/dim]"
                        )
            else:
                console.print("\n[yellow]No relevant information found.[/yellow]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")


def show_help():
    """Show interactive mode help"""
    help_text = """
    **Example Questions:**

    - "Where was machine learning discussed?"
    - "In which video was I appreciated?"
    - "Show me all mentions of John Smith"
    - "What did Sarah say about the project?"
    - "Where did we talk about deadlines?"

    **Tips:**

    - Be specific with names and topics
    - Ask about sentiments (positive feedback, concerns, etc.)
    - Queries work semantically, not just keyword matching
    """
    console.print(Markdown(help_text))


@cli.command()
def stats():
    """Show database statistics"""
    show_stats_internal()


def show_stats_internal():
    """Internal function to show stats"""
    db = VideoDatabase()
    indexer = VectorIndexer()

    db_stats = db.get_stats()
    vector_stats = indexer.get_stats()

    table = Table(title="EddiGits Statistics", show_header=False)
    table.add_column(style="cyan")
    table.add_column(style="green")

    table.add_row("Videos", str(db_stats["videos"]))
    table.add_row("Segments", str(db_stats["segments"]))
    table.add_row("Chunks", str(db_stats["chunks"]))
    table.add_row("Total Duration", db_stats["total_duration_formatted"])
    table.add_row("Indexed Chunks", str(vector_stats["total_chunks"]))
    table.add_row("Embedding Model", vector_stats["embedding_model"])

    console.print()
    console.print(table)
    console.print()


@cli.command()
def list_videos():
    """List all processed videos"""
    db = VideoDatabase()
    videos = db.get_all_videos()

    if not videos:
        console.print("[yellow]No videos found[/yellow]")
        return

    table = Table(title="Processed Videos")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Duration", style="magenta")
    table.add_column("Language", style="yellow")
    table.add_column("Processed", style="blue")

    for video in videos:
        duration = f"{video['duration']:.1f}s" if video['duration'] else "N/A"
        processed = video['transcribed_at'][:10] if video['transcribed_at'] else "N/A"

        table.add_row(
            str(video['id']),
            video['file_name'],
            duration,
            video['language'] or "N/A",
            processed
        )

    console.print()
    console.print(table)
    console.print()


@cli.command()
@click.argument('video_id', type=int)
def delete(video_id):
    """Delete a video and its data"""
    db = VideoDatabase()
    indexer = VectorIndexer()

    video = db.get_video(video_id)
    if not video:
        console.print(f"[red]Video {video_id} not found[/red]")
        return

    if click.confirm(f"Delete '{video['file_name']}'?"):
        db.delete_video(video_id)
        indexer.delete_video(video_id)
        console.print(f"[green]Video {video_id} deleted[/green]")


@cli.command()
def reset():
    """Reset the entire database (dangerous!)"""
    if not click.confirm(
        "This will delete ALL videos and data. Are you sure?",
        abort=True
    ):
        return

    if not click.confirm(
        "Really? This cannot be undone!",
        abort=True
    ):
        return

    db = VideoDatabase()
    indexer = VectorIndexer()

    # Delete database file
    if Config.DB_PATH.exists():
        Config.DB_PATH.unlink()
        console.print(f"[yellow]Deleted {Config.DB_PATH}[/yellow]")

    # Reset vector store
    indexer.reset()

    console.print("[green]Database reset complete[/green]")


if __name__ == '__main__':
    cli()
