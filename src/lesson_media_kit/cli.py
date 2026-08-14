"""Command-line interface."""

from pathlib import Path
from typing import Annotated

import typer

from lesson_media_kit import __version__
from lesson_media_kit.composition import render_scene
from lesson_media_kit.loading import load_lesson
from lesson_media_kit.manifest import create_manifest
from lesson_media_kit.pipeline import build_lesson
from lesson_media_kit.subtitles import render_srt, render_vtt
from lesson_media_kit.tts.base import TTSRequest
from lesson_media_kit.tts.dummy import DummyProvider
from lesson_media_kit.validation import ValidationFailure
from lesson_media_kit.workspace import OutputWorkspace, UnownedOutputError, UnsafeOutputPath

app = typer.Typer(no_args_is_help=True)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"lesson-media {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", callback=_version_callback, is_eager=True),
    ] = False,
) -> None:
    """Generate language-lesson media locally."""


def _fail(error: Exception, code: int) -> None:
    typer.echo(str(error), err=True)
    raise typer.Exit(code)


@app.command("validate")
def validate_command(lesson: Path) -> None:
    """Validate a lesson without generating media."""
    try:
        load_lesson(lesson)
    except ValidationFailure as error:
        _fail(error, 2)
    typer.echo("valid")


@app.command("tts")
def tts_command(
    lesson: Path,
    output: Annotated[Path, typer.Option("--output")],
    provider: Annotated[str, typer.Option("--provider")] = "dummy",
) -> None:
    """Generate lesson speech assets."""
    if provider != "dummy":
        _fail(ValueError("only the dummy provider is available from the CLI in v0.1.0"), 2)
    data = load_lesson(lesson)
    workspace = OutputWorkspace(output)
    tts = DummyProvider()
    for segment in data.segments:
        result = tts.synthesize(TTSRequest(segment.id, segment.text, data.metadata.target_language))
        workspace.write_bytes(f"audio/{segment.id}.wav", result.audio)
    typer.echo("audio generated")


@app.command("subtitles")
def subtitles_command(
    lesson: Path,
    output: Annotated[Path, typer.Option("--output")],
    format: Annotated[str, typer.Option("--format")] = "srt",
) -> None:
    """Generate SRT or VTT subtitles."""
    data = load_lesson(lesson)
    workspace = OutputWorkspace(output)
    if format == "srt":
        workspace.write_bytes("subtitles/lesson.srt", render_srt(data).encode("utf-8"))
    elif format == "vtt":
        workspace.write_bytes("subtitles/lesson.vtt", render_vtt(data).encode("utf-8"))
    else:
        _fail(ValueError("format must be srt or vtt"), 2)
    typer.echo("subtitles generated")


@app.command("compose")
def compose_command(
    lesson: Path,
    output: Annotated[Path, typer.Option("--output")],
    template: Annotated[str, typer.Option("--template")] = "default",
) -> None:
    """Generate trusted offline HTML scenes."""
    if template != "default":
        _fail(ValueError("only the packaged default template is supported"), 2)
    workspace = OutputWorkspace(output)
    workspace.write_bytes("scenes/lesson.html", render_scene(load_lesson(lesson)).encode("utf-8"))
    typer.echo("scene generated")


@app.command("manifest")
def manifest_command(
    lesson: Path,
    output: Annotated[Path, typer.Option("--output")],
) -> None:
    """Create a manifest for an empty validated build."""
    load_lesson(lesson)
    manifest = create_manifest(
        lesson_bytes=lesson.read_bytes(), provider="none", provider_metadata={}, files={}
    )
    OutputWorkspace(output).write_bytes("manifest.json", manifest.to_json().encode("utf-8"))
    typer.echo("manifest generated")


@app.command("build")
def build_command(
    lesson: Path,
    output: Annotated[Path, typer.Option("--output")],
    provider: Annotated[str, typer.Option("--provider")] = "dummy",
    force: Annotated[bool, typer.Option("--force")] = False,
) -> None:
    """Run the fixed offline lesson media pipeline."""
    if provider != "dummy":
        _fail(ValueError("only the dummy provider is available from the CLI in v0.1.0"), 2)
    try:
        build_lesson(lesson, output, DummyProvider(), force=force)
    except ValidationFailure as error:
        _fail(error, 2)
    except (UnsafeOutputPath, UnownedOutputError) as error:
        _fail(error, 3)
    typer.echo("build complete")
