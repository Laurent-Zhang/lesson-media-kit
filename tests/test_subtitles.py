import unittest

from lesson_media_kit.models import Lesson
from lesson_media_kit.subtitles import render_srt, render_vtt


def timed_lesson(start_ms: int, duration_ms: int, text: str) -> Lesson:
    return Lesson.model_validate(
        {
            "version": 1,
            "metadata": {
                "title": "Timed lesson",
                "source_language": "en",
                "target_language": "zh-CN",
            },
            "segments": [
                {"id": "s1", "text": text, "start_ms": start_ms, "duration_ms": duration_ms}
            ],
        }
    )


class SubtitleTest(unittest.TestCase):
    def test_srt_formats_milliseconds(self) -> None:
        lesson = timed_lesson(61_002, 1_998, "你好\nHello")
        self.assertEqual(
            render_srt(lesson),
            "1\n00:01:01,002 --> 00:01:03,000\n你好\nHello\n",
        )

    def test_vtt_has_header_and_dot_separator(self) -> None:
        lesson = timed_lesson(0, 1_250, "Bonjour")
        self.assertTrue(render_vtt(lesson).startswith("WEBVTT\n\n00:00:00.000 --> 00:00:01.250"))
