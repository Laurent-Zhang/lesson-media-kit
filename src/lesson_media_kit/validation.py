"""Public validation failures and semantic lesson checks."""

from pydantic import ValidationError

from lesson_media_kit.models import Lesson


class ValidationFailure(ValueError):
    """A safe, actionable input validation error."""


def _location(parts: tuple[object, ...]) -> str:
    return ".".join(str(part) for part in parts)


def from_pydantic(error: ValidationError) -> ValidationFailure:
    first = error.errors(include_url=False, include_context=False, include_input=False)[0]
    location = _location(first["loc"])
    return ValidationFailure(f"{location}: {first['msg']}")


def validate_semantics(lesson: Lesson) -> Lesson:
    seen: set[str] = set()
    previous_end = 0
    timed = False
    for index, segment in enumerate(lesson.segments):
        if segment.id in seen:
            raise ValidationFailure(f"segments.{index}.id: duplicate segment id")
        seen.add(segment.id)
        has_start = segment.start_ms is not None
        has_duration = segment.duration_ms is not None
        if has_start != has_duration:
            raise ValidationFailure(
                f"segments.{index}: start_ms and duration_ms must be provided together"
            )
        if has_start and has_duration:
            assert segment.start_ms is not None and segment.duration_ms is not None
            if timed and segment.start_ms < previous_end:
                raise ValidationFailure(f"segments.{index}.start_ms: overlaps previous segment")
            previous_end = segment.start_ms + segment.duration_ms
            timed = True
    return lesson
