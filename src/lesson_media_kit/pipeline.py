"""Fixed-order lesson media build pipeline."""

import json
from pathlib import Path

from lesson_media_kit.composition import render_scene
from lesson_media_kit.loading import load_lesson
from lesson_media_kit.manifest import BuildManifest, create_manifest
from lesson_media_kit.subtitles import render_srt, render_vtt
from lesson_media_kit.tts.base import ProviderError, TTSProvider, TTSRequest
from lesson_media_kit.workspace import OutputWorkspace


def build_lesson(
    lesson_path: Path,
    output: Path,
    provider: TTSProvider,
    *,
    force: bool = False,
) -> BuildManifest:
    lesson = load_lesson(lesson_path)
    workspace = OutputWorkspace(output)
    generated: dict[str, bytes] = {}
    metadata: dict[str, str] = {}
    try:
        for segment in lesson.segments:
            result = provider.synthesize(
                TTSRequest(
                    segment_id=segment.id,
                    text=segment.text,
                    language=lesson.metadata.target_language,
                )
            )
            extension = "wav" if result.media_type == "audio/wav" else "mp3"
            path = f"audio/{segment.id}.{extension}"
            generated[path] = result.audio
            metadata.update(result.provider_metadata)
        generated["subtitles/lesson.srt"] = render_srt(lesson).encode("utf-8")
        generated["subtitles/lesson.vtt"] = render_vtt(lesson).encode("utf-8")
        generated["scenes/lesson.html"] = render_scene(lesson).encode("utf-8")
        manifest = create_manifest(
            lesson_bytes=lesson_path.read_bytes(),
            provider=provider.provider_id,
            provider_metadata=metadata,
            files=generated,
        )
        for path, data in generated.items():
            workspace.write_bytes(path, data, force=force)
        workspace.write_bytes("manifest.json", manifest.to_json().encode("utf-8"), force=force)
        return manifest
    except ProviderError:
        failure = (
            json.dumps(
                {"status": "failed", "stage": "tts", "category": "provider_error"},
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        workspace.write_bytes("failure.json", failure.encode("utf-8"), force=force)
        raise
