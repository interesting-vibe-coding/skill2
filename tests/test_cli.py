from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "skill2.cli", *args],
        cwd=cwd or ROOT,
        env={"PYTHONPATH": str(ROOT / "src")},
        text=True,
        capture_output=True,
        check=False,
    )


class Skill2CliTest(unittest.TestCase):
    def test_scaffold_creates_lint_clean_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_cli(
                "scaffold",
                "skill",
                "demo-skill",
                "-o",
                str(root / "skills"),
                "--description",
                "测试 demo skill",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            skill = root / "skills" / "demo-skill" / "SKILL.md"
            self.assertTrue(skill.exists())

            lint = run_cli("lint", str(root / "skills"), "--json")
            self.assertEqual(lint.returncode, 0, lint.stderr)
            payload = json.loads(lint.stdout)
            self.assertEqual(payload["checked"], 1)
            self.assertEqual(payload["issues"], [])

    def test_lint_reports_name_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skills" / "right-name"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: wrong-name
description: "bad"
---

# right-name

body long enough for lint to skip short-body warning.
""",
                encoding="utf-8",
            )
            result = run_cli("lint", str(skill_dir), "--json")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            messages = [issue["message"] for issue in payload["issues"]]
            self.assertIn("name `wrong-name` does not match directory `right-name`", messages)

    def test_lint_reports_local_path_and_secret(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skills" / "risky-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: risky-skill
description: "bad"
---

# risky-skill

Do not use /Users/alice/private.
token: sk-testtoken123456
""",
                encoding="utf-8",
            )
            result = run_cli("lint", str(skill_dir), "--json")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            messages = [issue["message"] for issue in payload["issues"]]
            self.assertIn("contains machine-local absolute path", messages)
            self.assertIn("possible secret or credential text", messages)

    def test_lint_warns_non_executable_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skills" / "script-skill"
            scripts = skill_dir / "scripts"
            scripts.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: script-skill
description: "script"
---

# script-skill

Run script when deterministic work is needed.
""",
                encoding="utf-8",
            )
            script = scripts / "run.sh"
            script.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
            result = run_cli("lint", str(skill_dir), "--json")
            self.assertEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            messages = [issue["message"] for issue in payload["issues"]]
            self.assertIn("script is not executable", messages)

    def test_scan_emits_stable_inventory(self) -> None:
        result = run_cli("scan", "skills", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["schema_version"], "1")
        self.assertEqual(len(payload["skills"]), 6)
        publish = next(skill for skill in payload["skills"] if skill["name"] == "skill2-publish")
        self.assertEqual(publish["scope"], "project")
        self.assertEqual(len(publish["hash"]), 64)
        self.assertGreater(publish["body_tokens"], 0)

    def test_scan_parses_yaml_and_markdown_resources(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skills" / "demo"
            references = skill_dir / "references"
            references.mkdir(parents=True)
            (references / "guide.md").write_text("guide\n", encoding="utf-8")
            (skill_dir / "SKILL.md").write_text(
                """---
name: demo
description: >-
  Use when multiline YAML metadata
  must parse correctly.
---

# demo

Read [guide](references/guide.md#top) before doing deterministic work.
""",
                encoding="utf-8",
            )
            result = run_cli("scan", str(skill_dir), "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            skill = payload["skills"][0]
            self.assertEqual(
                skill["description"],
                "Use when multiline YAML metadata must parse correctly.",
            )
            self.assertEqual(skill["references"], ["references/guide.md"])

    def test_lint_emits_sarif(self) -> None:
        result = run_cli("lint", "skills", "--format", "sarif")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["version"], "2.1.0")
        self.assertEqual(payload["runs"][0]["tool"]["driver"]["name"], "skill2")


if __name__ == "__main__":
    unittest.main()
