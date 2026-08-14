"""Strict normalized lesson data model."""

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LessonMetadata(StrictModel):
    title: str = Field(min_length=1, max_length=200)
    source_language: str = Field(min_length=2, max_length=35)
    target_language: str = Field(min_length=2, max_length=35)


class Segment(StrictModel):
    id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
    text: str = Field(min_length=1, max_length=2_000)
    transliteration: str | None = Field(default=None, max_length=2_000)
    translation: str | None = Field(default=None, max_length=2_000)
    start_ms: int | None = Field(default=None, ge=0)
    duration_ms: int | None = Field(default=None, gt=0)


class Lesson(StrictModel):
    version: int = Field(ge=1, le=1)
    metadata: LessonMetadata
    segments: list[Segment] = Field(min_length=1, max_length=500)
