import tempfile
import unittest
from pathlib import Path

from lesson_media_kit.workspace import (
    OutputWorkspace,
    UnownedOutputError,
    UnsafeOutputPath,
)


class OutputWorkspaceTest(unittest.TestCase):
    def test_rejects_escaped_generated_paths(self) -> None:
        values = ["../secret", "a/../../secret", "C:\\secret", "\\\\server\\share", "bad\x00name"]
        with tempfile.TemporaryDirectory() as directory:
            workspace = OutputWorkspace(Path(directory) / "out")
            for value in values:
                with self.subTest(value=value), self.assertRaises(UnsafeOutputPath):
                    workspace.resolve_generated(value)

    def test_force_never_overwrites_unowned_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "out"
            root.mkdir()
            (root / "notes.txt").write_text("user data", encoding="utf-8")
            workspace = OutputWorkspace(root)

            with self.assertRaises(UnownedOutputError):
                workspace.write_bytes("notes.txt", b"generated", force=True)

            self.assertEqual((root / "notes.txt").read_text(encoding="utf-8"), "user data")

    def test_rejects_existing_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "out"
            outside = base / "outside"
            root.mkdir()
            outside.mkdir()
            link = root / "linked"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"symbolic links unavailable: {error}")
            workspace = OutputWorkspace(root)
            with self.assertRaises(UnsafeOutputPath):
                workspace.resolve_generated("linked/escape.txt")
