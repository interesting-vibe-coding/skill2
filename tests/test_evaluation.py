from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skill2.cases import load_case_suite
from skill2.codex_runner import ExecutionResult, detect_activations
from skill2.tester import evaluate_assertions, run_test_suite

ROOT = Path(__file__).resolve().parents[1]


class EvaluationTest(unittest.TestCase):
    def test_load_case_suite_normalizes_legacy_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.yaml"
            path.write_text(
                """skill: demo
agent: codex
defaults:
  repetitions: 3
cases:
  - name: Core trigger
    prompt: Build a demo skill
    expect_activation: demo
    assertions:
      - type: contains
        value: SKILL.md
""",
                encoding="utf-8",
            )
            suite = load_case_suite(path)
            self.assertEqual(suite.skill, "demo")
            self.assertEqual(suite.cases[0].id, "core-trigger")
            self.assertEqual(suite.cases[0].repetitions, 3)

    def test_detect_activation_from_exact_skill_path(self) -> None:
        skill_file = Path("/tmp/isolated/skills/demo/SKILL.md")
        events = (
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": f"sed -n 1,200p {skill_file}",
                },
            },
        )
        activations, evidence = detect_activations(events, {"demo": skill_file})
        self.assertEqual(activations, {"demo": "medium"})
        self.assertIn("exact SKILL.md read: demo", evidence)

    def test_scan_output_is_not_activation(self) -> None:
        skill_file = Path("/tmp/isolated/skills/demo/SKILL.md")
        events = (
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "find /tmp/isolated/skills -name SKILL.md",
                    "aggregated_output": str(skill_file),
                },
            },
        )
        activations, _ = detect_activations(events, {"demo": skill_file})
        self.assertEqual(activations, {})

    def test_assertions_use_output_workspace_and_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "result.txt").write_text("ready", encoding="utf-8")
            execution = ExecutionResult(
                exit_code=0,
                duration_ms=1,
                final_message="隔离 activation ready",
                events=(),
                commands=("skill2 lint skills",),
                activations={},
                evidence=(),
                workspace=str(workspace),
                changed_files=("result.txt",),
            )
            assertions = (
                {"type": "contains", "value": "activation"},
                {"type": "contains_all", "values": ["隔离", "ready"]},
                {"type": "contains_groups", "groups": [["隔离", "isolate"], ["ready"]]},
                {"type": "file_contains", "path": "result.txt", "value": "ready"},
                {"type": "tool_contains", "value": "skill2 lint"},
                {"type": "no_remote_write"},
            )
            results = evaluate_assertions(assertions, execution)
            self.assertTrue(all(item["passed"] for item in results), json.dumps(results))

    def test_all_repository_case_files_parse(self) -> None:
        suites = [load_case_suite(path) for path in sorted((ROOT / "cases").glob("*.yaml"))]
        self.assertEqual(len(suites), 8)
        self.assertEqual(sum(len(suite.cases) for suite in suites), 35)

    def test_runner_checkpoints_and_skips_completed_trials_on_resume(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = _write_demo_skill(root)
            suite = _write_demo_suite(root, repetitions=2)
            calls = []

            def runner(**kwargs):
                calls.append(kwargs["artifact_dir"])
                workspace = kwargs["artifact_dir"] / "workspace"
                workspace.mkdir(parents=True)
                return ExecutionResult(
                    exit_code=0,
                    duration_ms=1,
                    final_message="ready",
                    events=(),
                    commands=(),
                    activations={"demo": "medium"},
                    evidence=(),
                    workspace=str(workspace),
                    changed_files=(),
                )

            first = run_test_suite(
                target=skill,
                suite=suite,
                output_root=root / "runs",
                pack=False,
                baseline=False,
                trials_override=None,
                timeout=1,
                model=None,
                runner=runner,
            )
            run_dir = root / "runs" / first.run_id
            self.assertEqual(len(first.trials), 2)
            self.assertTrue((run_dir / "run.json").is_file())

            resumed = run_test_suite(
                target=skill,
                suite=suite,
                output_root=root / "runs",
                pack=False,
                baseline=False,
                trials_override=None,
                timeout=1,
                model=None,
                resume=run_dir,
                runner=runner,
            )

            self.assertEqual(len(resumed.trials), 2)
            self.assertEqual(len(calls), 2)

            another = run_test_suite(
                target=skill,
                suite=suite,
                output_root=root / "runs",
                pack=False,
                baseline=False,
                trials_override=1,
                timeout=1,
                model=None,
                runner=runner,
            )
            self.assertNotEqual(first.run_id, another.run_id)

    def test_runner_stops_after_failure_rate_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = _write_demo_skill(root)
            suite = _write_demo_suite(root, repetitions=3)

            def runner(**kwargs):
                workspace = kwargs["artifact_dir"] / "workspace"
                workspace.mkdir(parents=True)
                return ExecutionResult(
                    exit_code=0,
                    duration_ms=1,
                    final_message="missed",
                    events=(),
                    commands=(),
                    activations={},
                    evidence=(),
                    workspace=str(workspace),
                    changed_files=(),
                )

            result = run_test_suite(
                target=skill,
                suite=suite,
                output_root=root / "runs",
                pack=False,
                baseline=False,
                trials_override=None,
                timeout=1,
                model=None,
                max_failure_rate=0.5,
                min_trials_before_stop=1,
                runner=runner,
            )

            self.assertEqual(len(result.trials), 1)
            self.assertEqual(result.trials[0].status, "fail")
            self.assertFalse(result.complete)
            self.assertTrue(result.stopped_early)


def _write_demo_skill(root: Path) -> Path:
    skill = root / "skills" / "demo"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        """---
name: demo
description: "Use when testing demo behavior."
---

# Demo

Return ready after reading this skill.
""",
        encoding="utf-8",
    )
    return skill


def _write_demo_suite(root: Path, repetitions: int):
    path = root / "cases.yaml"
    path.write_text(
        f"""schema_version: "1"
skill: demo
agent: codex
defaults:
  repetitions: {repetitions}
cases:
  - id: core
    prompt: "Run demo."
    expect_activation: demo
""",
        encoding="utf-8",
    )
    return load_case_suite(path)


if __name__ == "__main__":
    unittest.main()
