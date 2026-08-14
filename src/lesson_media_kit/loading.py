"""Safe lesson file loading."""

import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from lesson_media_kit.models import Lesson
from lesson_media_kit.validation import ValidationFailure, from_pydantic, validate_semantics


def _parse(path: Path) -> Any:
    if path.suffix.lower() not in {".json", ".yaml", ".yml"}:
        raise ValidationFailure("file: expected .json, .yaml, or .yml")
    try:
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            return json.loads(text)
        return yaml.safe_load(text)
    except (OSError, UnicodeError, json.JSONDecodeError, yaml.YAMLError) as error:
        raise ValidationFailure(f"file: invalid lesson document ({type(error).__name__})") from None


def load_lesson(path: Path) -> Lesson:
    data = _parse(path)
    try:
        lesson = Lesson.model_validate(data)
    except ValidationError as error:
        raise from_pydantic(error) from None
    return validate_semantics(lesson)
