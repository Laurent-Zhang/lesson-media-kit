import unittest

from lesson_media_kit.composition import render_scene
from lesson_media_kit.models import Lesson


def lesson_with_text(text: str) -> Lesson:
    return Lesson.model_validate(
        {
            "version": 1,
            "metadata": {
                "title": "Offline scene",
                "source_language": "en",
                "target_language": "fr",
            },
            "segments": [{"id": "s1", "text": text}],
        }
    )


class CompositionTest(unittest.TestCase):
    def test_escapes_untrusted_lesson_html(self) -> None:
        html = render_scene(lesson_with_text('<script>fetch("https://evil.example")</script>'))
        self.assertNotIn("<script>fetch", html)
        self.assertIn("&lt;script&gt;", html)

    def test_generated_page_has_no_remote_resources(self) -> None:
        html = render_scene(lesson_with_text("Hello"))
        self.assertNotIn("http://", html)
        self.assertNotIn("https://", html)
        self.assertIn("connect-src 'none'", html)
