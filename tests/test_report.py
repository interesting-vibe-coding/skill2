from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skill2.models import ScanResult, SkillRecord, SkillSource
from skill2.report import render_report
from skill2.suggest import SuggestionResult
from skill2.usage import UsageEvent, UsageResult


class ReportTest(unittest.TestCase):
    def test_renders_self_contained_escaped_report_with_traceable_metrics(self) -> None:
        scan = _scan("<script>alert(1)</script>")
        usage = UsageResult(
            events=(
                UsageEvent(
                    timestamp="2026-07-01T00:00:00Z",
                    harness="codex",
                    session="session-1",
                    skill="<script>alert(1)</script>",
                    source="<img src=x onerror=alert(1)>",
                    confidence="medium",
                    category="activation",
                ),
            ),
            summary={},
        )
        with tempfile.TemporaryDirectory() as tmp:
            output = render_report(
                scan,
                usage,
                SuggestionResult(()),
                (
                    {
                        "skill": "<script>alert(1)</script>",
                        "trials": [{"status": "pass", "activation_status": "activation_gap"}],
                    },
                ),
                Path(tmp) / "report.html",
            )
            html = output.read_text(encoding="utf-8")

        self.assertEqual(output.name, "report.html")
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", html)
        self.assertIn('href="#event-1"', html)
        self.assertIn('href="#test-1-1"', html)
        self.assertNotIn("https://", html)

    def test_renders_empty_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = render_report(
                ScanResult(root="/empty", skills=()),
                UsageResult(events=(), summary={}),
                SuggestionResult(()),
                (),
                Path(tmp) / "empty.html",
            )
            html = output.read_text(encoding="utf-8")

        self.assertIn("No scanned skills.", html)
        self.assertIn("No usage events.", html)
        self.assertIn("No test runs.", html)


def _scan(name: str) -> ScanResult:
    source = SkillSource(text="", body="", frontmatter={}, frontmatter_error=None)
    return ScanResult(
        root="/library",
        skills=(
            SkillRecord(
                name=name,
                path="/library/skill/SKILL.md",
                description="Test report",
                body_tokens=42,
                references=(),
                scripts=(),
                assets=(),
                scope="global",
                hash="a" * 64,
                _source=source,
            ),
        ),
    )
