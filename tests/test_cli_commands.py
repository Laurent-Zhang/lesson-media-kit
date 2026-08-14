import tempfile
import unittest
from pathlib import Path

from typer.testing import CliRunner

from lesson_media_kit.cli import app


class CliCommandsTest(unittest.TestCase):
    def test_public_commands_have_help(self) -> None:
        runner = CliRunner()
        for command in ["validate", "tts", "subtitles", "compose", "manifest", "build"]:
            with self.subTest(command=command):
                result = runner.invoke(app, [command, "--help"])
                self.assertEqual(result.exit_code, 0, result.output)

    def test_build_creates_offline_assets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "build"
            result = CliRunner().invoke(
                app,
                [
                    "build",
                    "examples/basic-lesson/lesson.yaml",
                    "--output",
                    str(output),
                    "--provider",
                    "dummy",
                ],
            )
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertTrue((output / "audio/hello.wav").is_file())
            self.assertTrue((output / "subtitles/lesson.srt").is_file())
            self.assertTrue((output / "subtitles/lesson.vtt").is_file())
            self.assertTrue((output / "scenes/lesson.html").is_file())
            self.assertTrue((output / "manifest.json").is_file())
