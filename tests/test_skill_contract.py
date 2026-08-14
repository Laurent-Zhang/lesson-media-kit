import re
import unittest
from pathlib import Path


class SkillContractTest(unittest.TestCase):
    def test_skill_commands_are_confined_and_network_requires_approval(self) -> None:
        text = Path("skills/lesson-media/SKILL.md").read_text(encoding="utf-8")
        commands = set(re.findall(r"`lesson-media\s+([a-z-]+)", text))
        self.assertTrue(commands)
        self.assertLessEqual(
            commands,
            {"validate", "tts", "subtitles", "compose", "manifest", "build"},
        )
        lowered = text.lower()
        self.assertIn("untrusted data", lowered)
        self.assertIn("explicit user approval", lowered)
        self.assertIn("network", lowered)
        self.assertNotRegex(lowered, r"lesson-media\s+(run|exec|shell|upload)")
