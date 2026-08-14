import unittest
from pathlib import Path

import yaml


class RepositoryPolicyTest(unittest.TestCase):
    def test_actions_are_sha_pinned_and_read_only(self) -> None:
        workflow = yaml.safe_load(Path(".github/workflows/ci.yml").read_text(encoding="utf-8"))
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        for job in workflow["jobs"].values():
            for step in job.get("steps", []):
                uses = step.get("uses")
                if uses:
                    self.assertRegex(uses, r"^[^@]+@[0-9a-f]{40}$")

    def test_workflow_runs_required_quality_commands(self) -> None:
        text = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
        for command in [
            "ruff format --check",
            "ruff check",
            "mypy src",
            "unittest discover",
            "python -m build",
            "python -m pip_audit",
        ]:
            self.assertIn(command, text)

    def test_workflow_upgrades_vulnerable_packaging_tools_before_audit(self) -> None:
        text = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
        upgrade = 'python -m pip install --upgrade "pip>=26.1.2" "setuptools>=83"'
        self.assertIn(upgrade, text)
        self.assertLess(text.index(upgrade), text.index("python -m pip_audit"))
