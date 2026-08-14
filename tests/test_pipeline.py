import json
import tempfile
import unittest
from pathlib import Path

from lesson_media_kit.pipeline import build_lesson
from lesson_media_kit.tts.base import ProviderError, TTSRequest
from lesson_media_kit.tts.dummy import DummyProvider

EXAMPLE = Path("examples/basic-lesson/lesson.yaml")


class FailingProvider:
    provider_id = "failing"

    def synthesize(self, request: TTSRequest):  # type: ignore[no-untyped-def]
        raise ProviderError("provider failed with secret-value")


class PipelineTest(unittest.TestCase):
    def test_offline_build_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = build_lesson(EXAMPLE, Path(directory) / "first", DummyProvider())
            second = build_lesson(EXAMPLE, Path(directory) / "second", DummyProvider())
            self.assertEqual(first.to_json(), second.to_json())
            self.assertIn("subtitles/lesson.srt", first.files)
            self.assertIn("scenes/lesson.html", first.files)

    def test_failed_provider_never_writes_success_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out"
            with self.assertRaises(ProviderError):
                build_lesson(EXAMPLE, output, FailingProvider())
            self.assertFalse((output / "manifest.json").exists())
            report = json.loads((output / "failure.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "failed")
            self.assertNotIn("secret-value", json.dumps(report))
