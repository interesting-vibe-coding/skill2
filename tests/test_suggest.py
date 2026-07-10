from __future__ import annotations

import json
import unittest
from pathlib import Path

from skill2.models import ScanResult, SkillRecord, SkillSource
from skill2.suggest import build_suggestions
from skill2.usage import UsageEvent, UsageResult

FIXTURE = Path(__file__).parent / "fixtures" / "report" / "agent-search-consolidation.json"


class SuggestTest(unittest.TestCase):
    def test_consolidates_legacy_agent_search_shape(self) -> None:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        scan = _scan(*(item["name"] for item in fixture["skills"]), descriptions=fixture["skills"])
        usage = _usage(*fixture["events"])

        result = build_suggestions(scan, usage)

        self.assertEqual(result.schema_version, "1")
        self.assertIn(
            {"action": "merge", "target": "agent-search + search-strategy"},
            [{"action": item.action, "target": item.target} for item in result.suggestions],
        )
        self.assertEqual(result.to_dict()["schema_version"], "1")

    def test_low_frequency_high_value_skill_is_not_delete_candidate(self) -> None:
        scan = _scan("rare")
        usage = _usage(
            {"timestamp": "2026-07-01", "session": "s", "skill": "rare", "category": "activation"}
        )

        result = build_suggestions(
            scan, usage, ({"skill": "rare", "trials": [{"status": "pass"}]},)
        )

        actions = {item.action for item in result.suggestions if item.target == "rare"}
        self.assertIn("keep", actions)
        self.assertNotIn("delete_candidate", actions)

    def test_delete_requires_absent_usage_tests_and_explicit_owner_evidence(self) -> None:
        scan = _scan("unused", "owned", declared_scopes={"owned": "project"})
        result = build_suggestions(scan, _usage())

        self.assertIn(
            ("delete_candidate", "unused"),
            {(item.action, item.target) for item in result.suggestions},
        )
        self.assertIn(
            ("projectize", "owned"), {(item.action, item.target) for item in result.suggestions}
        )

    def test_path_derived_project_scope_is_not_projectize_evidence(self) -> None:
        scan = _scan("source-hub", scopes={"source-hub": "project"})

        result = build_suggestions(scan, _usage())

        actions = {item.action for item in result.suggestions if item.target == "source-hub"}
        self.assertNotIn("projectize", actions)
        self.assertIn("delete_candidate", actions)

    def test_downgrade_requires_mainly_broad_or_worker_reads(self) -> None:
        scan = _scan("component")
        usage = _usage(
            {"timestamp": "1", "session": "a", "skill": "component", "category": "broad_scan"},
            {"timestamp": "2", "session": "b", "skill": "component", "category": "worker_read"},
        )

        result = build_suggestions(scan, usage)

        self.assertIn(
            ("downgrade", "component"), {(item.action, item.target) for item in result.suggestions}
        )

    def test_broad_scan_cooccurrence_does_not_trigger_merge(self) -> None:
        scan = _scan(
            "agent-search",
            "search-strategy",
            descriptions=[
                {"name": "agent-search", "description": "Search and research router"},
                {"name": "search-strategy", "description": "Search strategy for research"},
            ],
        )
        usage = _usage(
            {
                "timestamp": "1",
                "session": "a",
                "skill": "agent-search",
                "category": "broad_scan",
            },
            {
                "timestamp": "2",
                "session": "a",
                "skill": "search-strategy",
                "category": "broad_scan",
            },
            {
                "timestamp": "3",
                "session": "b",
                "skill": "agent-search",
                "category": "broad_scan",
            },
            {
                "timestamp": "4",
                "session": "b",
                "skill": "search-strategy",
                "category": "broad_scan",
            },
        )

        result = build_suggestions(scan, usage)

        self.assertNotIn("merge", {item.action for item in result.suggestions})


def _scan(
    *names: str,
    descriptions: list[dict[str, str]] | None = None,
    scopes: dict[str, str] | None = None,
    declared_scopes: dict[str, str] | None = None,
) -> ScanResult:
    descriptions = descriptions or []
    description_by_name = {item["name"]: item["description"] for item in descriptions}
    scopes = scopes or {}
    declared_scopes = declared_scopes or {}
    return ScanResult(
        root="/library",
        skills=tuple(
            SkillRecord(
                name=name,
                path=f"/library/{name}/SKILL.md",
                description=description_by_name.get(name, name),
                body_tokens=10,
                references=(),
                scripts=(),
                assets=(),
                scope=scopes.get(name, "global"),
                hash="a" * 64,
                _source=SkillSource(
                    text="",
                    body="",
                    frontmatter=(
                        {"metadata": {"skill2": {"scope": declared_scopes[name]}}}
                        if name in declared_scopes
                        else {}
                    ),
                    frontmatter_error=None,
                ),
            )
            for name in names
        ),
    )


def _usage(*events: dict[str, str]) -> UsageResult:
    return UsageResult(
        events=tuple(
            UsageEvent(
                timestamp=event["timestamp"],
                harness="codex",
                session=event["session"],
                skill=event["skill"],
                source="fixture",
                confidence="medium",
                category=event["category"],  # type: ignore[arg-type]
            )
            for event in events
        ),
        summary={},
    )
