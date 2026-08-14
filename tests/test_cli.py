import unittest

from typer.testing import CliRunner

from lesson_media_kit.cli import app


class CliTest(unittest.TestCase):
    def test_version_reports_package_version(self) -> None:
        result = CliRunner().invoke(app, ["--version"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout.strip(), "lesson-media 0.1.0")
