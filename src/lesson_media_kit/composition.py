"""Trusted, offline HTML scene rendering."""

from pathlib import Path

from jinja2 import FileSystemLoader, StrictUndefined, select_autoescape
from jinja2.sandbox import SandboxedEnvironment

from lesson_media_kit.models import Lesson


def _template_directory() -> Path:
    source_tree = Path(__file__).resolve().parents[2] / "templates" / "default"
    if source_tree.is_dir():
        return source_tree
    return Path(__file__).resolve().parent / "templates" / "default"


def render_scene(lesson: Lesson) -> str:
    environment = SandboxedEnvironment(
        loader=FileSystemLoader(_template_directory()),
        autoescape=select_autoescape(default=True),
        undefined=StrictUndefined,
    )
    template = environment.get_template("scene.html.j2")
    return template.render(lesson=lesson)
