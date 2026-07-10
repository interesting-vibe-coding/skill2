from __future__ import annotations

from collections import Counter, defaultdict
from html import escape
from pathlib import Path
from typing import Any

from .models import ScanResult
from .suggest import SuggestionResult
from .usage import UsageResult


def render_report(
    scan: ScanResult,
    usage: UsageResult,
    suggestions: SuggestionResult,
    test_runs: tuple[dict[str, Any], ...],
    output: Path,
) -> Path:
    """Write a self-contained, read-only local HTML report."""
    events = tuple(_event(event) for event in usage.events)
    metrics = _metrics(scan, events, test_runs)
    output = output.expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(_document(scan, events, metrics, suggestions, test_runs), encoding="utf-8")
    return output


def _event(event: object) -> dict[str, str]:
    if hasattr(event, "to_dict"):
        event = event.to_dict()
    source = event if isinstance(event, dict) else {}
    return {
        "timestamp": str(source.get("timestamp", "")),
        "harness": str(source.get("harness", "")),
        "session": str(source.get("session", "")),
        "skill": str(source.get("skill", "")),
        "source": str(source.get("source", "")),
        "confidence": str(source.get("confidence", "")),
        "category": str(source.get("category", "unknown")),
    }


def _metrics(
    scan: ScanResult, events: tuple[dict[str, str], ...], test_runs: tuple[dict[str, Any], ...]
) -> dict[str, dict[str, Any]]:
    by_skill: dict[str, list[tuple[int, dict[str, str]]]] = defaultdict(list)
    for index, event in enumerate(events, 1):
        by_skill[event["skill"]].append((index, event))
    tests = _tests_by_skill(test_runs)
    metrics: dict[str, dict[str, Any]] = {}
    for index, skill in enumerate(scan.skills, 1):
        skill_events = by_skill.get(skill.name, [])
        direct_events = [
            (event_index, event)
            for event_index, event in skill_events
            if event["category"] == "activation"
        ]
        categories = Counter(event["category"] for _, event in skill_events)
        test_rows = tests.get(skill.name, [])
        metrics[skill.name] = {
            "inventory_id": index,
            "events": skill_events,
            "direct_events": direct_events,
            "frequency": len(direct_events),
            "recent": max((event["timestamp"] for _, event in direct_events), default="never"),
            "categories": categories,
            "tests": test_rows,
            "gaps": sum(row["activation_status"] == "activation_gap" for row in test_rows),
            "false_positives": sum(
                row["activation_status"] == "false_positive" for row in test_rows
            ),
        }
    return metrics


def _tests_by_skill(test_runs: tuple[dict[str, Any], ...]) -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = defaultdict(list)
    for run_index, run in enumerate(test_runs, 1):
        if not isinstance(run, dict):
            continue
        skill = str(run.get("skill") or run.get("target") or "")
        if not skill:
            continue
        trials = run.get("trials") or run.get("results") or [run]
        if not isinstance(trials, list):
            trials = [run]
        for trial_index, trial in enumerate(trials, 1):
            row = trial if isinstance(trial, dict) else {}
            result[skill].append(
                {
                    "id": f"test-{run_index}-{trial_index}",
                    "run": str(run.get("run_id") or run.get("id") or run_index),
                    "case": str(row.get("case_id") or row.get("case") or ""),
                    "status": str(row.get("status") or run.get("status") or ""),
                    "activation_status": str(
                        row.get("activation_status") or row.get("activation") or ""
                    ),
                    "outcome_status": str(row.get("outcome_status") or row.get("outcome") or ""),
                }
            )
    return result


def _document(
    scan: ScanResult,
    events: tuple[dict[str, str], ...],
    metrics: dict[str, dict[str, Any]],
    suggestions: SuggestionResult,
    test_runs: tuple[dict[str, Any], ...],
) -> str:
    ordered_skills = sorted(
        scan.skills,
        key=lambda skill: (-metrics[skill.name]["frequency"], skill.name),
    )
    max_frequency = max((metric["frequency"] for metric in metrics.values()), default=0)
    rows = "".join(
        _skill_row(skill, metrics[skill.name], max_frequency) for skill in ordered_skills
    )
    event_rows = "".join(_event_row(index, event) for index, event in enumerate(events, 1))
    test_rows = "".join(
        _test_row(skill.name, row) for skill in scan.skills for row in metrics[skill.name]["tests"]
    )
    suggestion_rows = "".join(_suggestion_row(item) for item in suggestions.suggestions)
    return "\n".join(
        (
            "<!doctype html>",
            '<html lang="en"><head><meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            """<title>Skill2 Report</title><style>
:root {
  --ink:#171b1f; --muted:#667079; --line:#dfe3e6;
  --soft:#f6f7f7; --yellow:#f5a000; --teal:#25bdb2;
}
* { box-sizing:border-box; }
body {
  font:14px/1.45 Inter,ui-sans-serif,system-ui,sans-serif;
  margin:0; color:var(--ink); background:#fff; letter-spacing:0;
}
main { max-width:1320px; margin:auto; padding:40px 32px 72px; }
.hero {
  display:flex; align-items:center; gap:16px;
  border-bottom:1px solid var(--line); padding-bottom:24px;
}
.mark {
  display:inline-flex; align-items:flex-start; color:var(--yellow);
  font-weight:800; font-size:42px; line-height:1;
}
.mark sup { color:var(--teal); font-size:15px; margin:0 0 0 2px; }
h1 { font-size:26px; line-height:1.15; margin:0; }
h2 { font-size:17px; margin:0 0 12px; }
.sub { color:var(--muted); margin:4px 0 0; }
.summary {
  display:grid; grid-template-columns:repeat(5,minmax(110px,1fr));
  border-bottom:1px solid var(--line);
}
.stat { padding:18px 12px 18px 0; }
.stat strong { display:block; font-size:22px; }
.stat span { color:var(--muted); font-size:12px; text-transform:uppercase; }
section { margin:34px 0; }
.table-wrap {
  overflow-x:auto; border-top:1px solid var(--ink);
  border-bottom:1px solid var(--line);
}
table { width:100%; border-collapse:collapse; background:#fff; min-width:880px; }
th,td {
  padding:10px 12px; text-align:left;
  border-bottom:1px solid var(--line); vertical-align:top;
}
th {
  background:var(--soft); font-size:11px; text-transform:uppercase;
  color:var(--muted); white-space:nowrap;
}
tbody tr:hover { background:#fffaf0; }
a { color:#006d68; text-decoration:none; }
a:hover { text-decoration:underline; }
.meter {
  display:inline-block; width:72px; height:5px; background:#eceff0;
  margin-left:8px; vertical-align:middle;
}
.meter i { display:block; height:100%; background:var(--yellow); }
.zero { color:#9a4b00; }
.ok { color:#397047; }
.muted,.empty { color:var(--muted); }
.empty { padding:16px; }
ul { margin:0; padding-left:18px; }
@media(max-width:700px) {
  main { padding:24px 16px 48px; }
  .summary { grid-template-columns:repeat(2,1fr); }
  .hero { align-items:flex-start; }
}
</style></head><body><main>
<header class="hero"><span class="mark">S<sup>2</sup></span><div>
<h1>Skill Library Report</h1>
<p class="sub">Local evidence. Direct calls separated from scan noise.</p>
</div></header>""",
            _summary_line(scan, events, suggestions, test_runs),
            _section(
                "inventory",
                "Skill Inventory",
                (
                    "Skill",
                    "Direct calls",
                    "Last direct call",
                    "Zero direct calls",
                    "Body tokens",
                    "Categories",
                    "Activation gaps",
                    "False positives",
                ),
                rows or _empty_row(8, "No scanned skills."),
            ),
            _section(
                "suggestions",
                "Suggestions",
                ("Action", "Target", "Reason", "Evidence"),
                suggestion_rows or _empty_row(4, "No conservative suggestion met the threshold."),
            ),
            _section(
                "events",
                "Event Evidence",
                ("Timestamp", "Skill", "Session", "Category", "Confidence", "Source"),
                event_rows or _empty_row(6, "No usage events."),
            ),
            _section(
                "tests",
                "Test Evidence",
                ("Skill", "Run", "Case", "Status", "Activation", "Outcome"),
                test_rows or _empty_row(6, "No test runs."),
            ),
            "</main></body></html>",
        )
    )


def _summary_line(
    scan: ScanResult,
    events: tuple[dict[str, str], ...],
    suggestions: SuggestionResult,
    test_runs: tuple[dict[str, Any], ...],
) -> str:
    direct = sum(event["category"] == "activation" for event in events)
    known = {skill.name for skill in scan.skills}
    called = {
        event["skill"]
        for event in events
        if event["category"] == "activation" and event["skill"] in known
    }
    zero = len(scan.skills) - len(called)
    return (
        '<nav class="summary">'
        f'<a class="stat" href="#inventory"><strong>{len(scan.skills)}</strong>'
        "<span>Skills</span></a>"
        f'<a class="stat" href="#events"><strong>{direct}</strong><span>Direct calls</span></a>'
        f'<a class="stat" href="#inventory"><strong>{zero}</strong><span>Zero direct</span></a>'
        f'<a class="stat" href="#tests"><strong>{len(test_runs)}</strong><span>Test runs</span></a>'
        f'<a class="stat" href="#suggestions"><strong>{len(suggestions.suggestions)}</strong>'
        "<span>Suggestions</span></a>"
        "</nav>"
    )


def _section(identifier: str, title: str, headers: tuple[str, ...], body: str) -> str:
    header_cells = "".join(f"<th>{escape(header)}</th>" for header in headers)
    return (
        f'<section id="{escape(identifier)}"><h2>{escape(title)}</h2><div class="table-wrap">'
        f"<table><thead><tr>{header_cells}</tr></thead><tbody>{body}</tbody></table></div></section>"
    )


def _skill_row(skill: Any, metric: dict[str, Any], max_frequency: int) -> str:
    test_links = _links("test", [row["id"].removeprefix("test-") for row in metric["tests"]])
    categories = (
        ", ".join(
            f"{escape(category)}: {count}"
            for category, count in sorted(metric["categories"].items())
        )
        or "none"
    )
    recent = metric["recent"]
    recent_label = recent[:10] if recent != "never" else recent
    recent_link = (
        f'<a href="#event-{metric["direct_events"][-1][0]}" '
        f'title="{escape(recent)}">{escape(recent_label)}</a>'
        if metric["direct_events"]
        else "never"
    )
    frequency = metric["frequency"]
    frequency_link = (
        f'<a href="#event-{metric["direct_events"][0][0]}">{frequency}</a>'
        if metric["direct_events"]
        else "0"
    )
    width = round(100 * frequency / max_frequency) if max_frequency else 0
    frequency_cell = f'{frequency_link}<span class="meter"><i style="width:{width}%"></i></span>'
    zero = (
        '<span class="zero">yes</span>'
        if not metric["direct_events"]
        else '<span class="ok">no</span>'
    )
    return (
        "<tr>"
        + "".join(
            (
                f"<td>{escape(skill.name)}</td>",
                f"<td>{frequency_cell}</td>",
                f"<td>{recent_link}</td>",
                f"<td>{zero}</td>",
                f"<td>{skill.body_tokens}</td>",
                f"<td>{categories}</td>",
                f"<td>{_number_link(metric['gaps'], test_links)}</td>",
                f"<td>{_number_link(metric['false_positives'], test_links)}</td>",
            )
        )
        + "</tr>"
    )


def _links(prefix: str, values: list[Any]) -> str:
    return " ".join(f'<a href="#{prefix}-{escape(str(value))}">1</a>' for value in values)


def _number_link(value: int, test_links: str) -> str:
    return f"{value} {test_links}" if value else "0"


def _event_row(index: int, event: dict[str, str]) -> str:
    return (
        f'<tr id="event-{index}">'
        + "".join(
            f"<td>{escape(event[key])}</td>"
            for key in ("timestamp", "skill", "session", "category", "confidence", "source")
        )
        + "</tr>"
    )


def _test_row(skill: str, row: dict[str, str]) -> str:
    return (
        f'<tr id="{escape(row["id"])}">'
        + "".join(
            f"<td>{escape(value)}</td>"
            for value in (
                skill,
                row["run"],
                row["case"],
                row["status"],
                row["activation_status"],
                row["outcome_status"],
            )
        )
        + "</tr>"
    )


def _suggestion_row(suggestion: Any) -> str:
    evidence = "".join(f"<li>{escape(item)}</li>" for item in suggestion.evidence)
    cells = (
        f"<td>{escape(suggestion.action)}</td>",
        f"<td>{escape(suggestion.target)}</td>",
        f"<td>{escape(suggestion.reason)}</td>",
        f"<td><ul>{evidence}</ul></td>",
    )
    return "<tr>" + "".join(cells) + "</tr>"


def _empty_row(columns: int, message: str) -> str:
    return f'<tr><td class="empty" colspan="{columns}">{escape(message)}</td></tr>'
