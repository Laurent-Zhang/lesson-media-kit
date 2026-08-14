"""Deterministic SRT and WebVTT subtitle rendering."""

from lesson_media_kit.models import Lesson, Segment
from lesson_media_kit.validation import ValidationFailure


def _times(segment: Segment, index: int) -> tuple[int, int]:
    if segment.start_ms is None or segment.duration_ms is None:
        raise ValidationFailure(f"segments.{index}: subtitle timing is required")
    return segment.start_ms, segment.start_ms + segment.duration_ms


def _stamp(milliseconds: int, separator: str) -> str:
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, millis = divmod(remainder, 1_000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}{separator}{millis:03d}"


def _text(segment: Segment) -> str:
    values = [segment.text]
    if segment.transliteration:
        values.append(segment.transliteration)
    if segment.translation:
        values.append(segment.translation)
    return "\n".join(values)


def render_srt(lesson: Lesson) -> str:
    blocks: list[str] = []
    for index, segment in enumerate(lesson.segments):
        start, end = _times(segment, index)
        blocks.append(f"{index + 1}\n{_stamp(start, ',')} --> {_stamp(end, ',')}\n{_text(segment)}")
    return "\n\n".join(blocks) + "\n"


def render_vtt(lesson: Lesson) -> str:
    blocks: list[str] = []
    for index, segment in enumerate(lesson.segments):
        start, end = _times(segment, index)
        blocks.append(f"{_stamp(start, '.')} --> {_stamp(end, '.')}\n{_text(segment)}")
    return "WEBVTT\n\n" + "\n\n".join(blocks) + "\n"
