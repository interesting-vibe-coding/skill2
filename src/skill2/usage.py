from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from .scan import scan_path

SCHEMA_VERSION = "1"
Category = Literal["activation", "maintenance", "broad_scan", "worker_read", "unknown"]

_READ_RE = re.compile(r"\b(?:cat|sed|head|tail|less|more|rg|grep|awk|cut|wc|read_text|open)\b")
_WRITE_RE = re.compile(
    r"\b(?:apply_patch|patch|tee|cp|mv|rm|touch|truncate|write_text|write_bytes)\b"
)
_HISTORICAL_PARTS = {
    ".archive",
    ".history",
    "archive",
    "archives",
    "backup",
    "backups",
    "deprecated",
    "historical",
    "history",
    "legacy",
    "old",
}


@dataclass(frozen=True)
class UsageEvent:
    timestamp: str
    harness: str
    session: str
    skill: str
    source: str
    confidence: str
    category: Category

    def to_dict(self) -> dict[str, str]:
        return {
            "timestamp": self.timestamp,
            "harness": self.harness,
            "session": self.session,
            "skill": self.skill,
            "source": self.source,
            "confidence": self.confidence,
            "category": self.category,
        }


@dataclass(frozen=True)
class UsageResult:
    events: tuple[UsageEvent, ...]
    summary: dict[str, object]
    schema_version: str = field(default=SCHEMA_VERSION, init=False)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "events": [event.to_dict() for event in self.events],
            "summary": self.summary,
        }


@dataclass(frozen=True)
class _Candidate:
    timestamp: str
    session: str
    skill: str
    source: str
    action: Literal["read", "maintenance", "unknown"]
    worker: bool


def parse_codex_usage(codex_root: Path, skill_root: Path) -> UsageResult:
    """Parse local Codex JSONL command evidence without retaining transcript content."""
    skills = _canonical_skills(skill_root)
    candidates: list[_Candidate] = []
    for session_file in _session_files(codex_root):
        records = _read_jsonl(session_file)
        session = _session_id(records, session_file)
        worker = _is_worker_session(records)
        for record in records:
            timestamp = _timestamp(record)
            for source, tool_name, command in _commands(record):
                for skill in _matching_skills(command, skills):
                    candidates.append(
                        _Candidate(
                            timestamp=timestamp,
                            session=session,
                            skill=skill,
                            source=source,
                            action=_action(tool_name, command),
                            worker=worker,
                        )
                    )

    broad_sessions = {
        session for session, names in _skills_by_session(candidates).items() if len(names) >= 4
    }
    events = _deduplicate(_events(candidates, broad_sessions))
    return UsageResult(events=events, summary=_summary(events))


def _canonical_skills(skill_root: Path) -> dict[str, str]:
    aliases: dict[str, str] = {}
    home = Path.home()
    install_roots = (
        home / ".agents" / "skills",
        home / ".codex" / "skills",
        home / ".claude" / "skills",
    )
    for skill in scan_path(skill_root).skills:
        source = Path(skill.path)
        if _is_excluded_skill_path(source):
            continue
        aliases[str(source.resolve())] = skill.name
        for root in install_roots:
            aliases[str(root / skill.name / "SKILL.md")] = skill.name
    return dict(sorted(aliases.items()))


def _is_excluded_skill_path(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    return (
        "vendor_imports" in parts
        or bool(parts & _HISTORICAL_PARTS)
        or "plugins" in parts
        and "cache" in parts
    )


def _session_files(codex_root: Path) -> tuple[Path, ...]:
    root = codex_root.expanduser().resolve()
    sessions = root / "sessions"
    archived = root / "archived_sessions"
    files = set()
    if sessions.is_dir():
        files.update(path for path in sessions.rglob("*.jsonl") if path.is_file())
    if archived.is_dir():
        files.update(path for path in archived.glob("*.jsonl") if path.is_file())
    return tuple(sorted(files, key=lambda path: path.as_posix()))


def _read_jsonl(path: Path) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ()
    for line in lines:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return tuple(records)


def _session_id(records: Iterable[dict[str, Any]], path: Path) -> str:
    for record in records:
        if record.get("type") != "session_meta":
            continue
        payload = record.get("payload")
        if not isinstance(payload, dict):
            continue
        for key in ("id", "session_id"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
    return path.stem.removeprefix("rollout-")


def _timestamp(record: dict[str, Any]) -> str:
    value = record.get("timestamp")
    if isinstance(value, str):
        return value
    payload = record.get("payload")
    if isinstance(payload, dict) and isinstance(payload.get("timestamp"), str):
        return payload["timestamp"]
    return ""


def _is_worker_session(records: Iterable[dict[str, Any]]) -> bool:
    for record in records:
        if record.get("type") != "session_meta":
            continue
        payload = record.get("payload")
        if not isinstance(payload, dict):
            continue
        if str(payload.get("thread_source", "")).lower() in {"subagent", "worker"}:
            return True
        if str(payload.get("agent_role", "")).lower() in {"subagent", "worker"}:
            return True
        if _contains_worker_metadata(payload.get("source")):
            return True
    return False


def _contains_worker_metadata(value: object) -> bool:
    if isinstance(value, str):
        return value.lower() in {"subagent", "worker"}
    if isinstance(value, dict):
        return any(
            str(key).lower() in {"subagent", "worker"} or _contains_worker_metadata(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_worker_metadata(item) for item in value)
    return False


def _commands(record: dict[str, Any]) -> Iterable[tuple[str, str, str]]:
    item = record.get("item")
    if isinstance(item, dict) and item.get("type") == "command_execution":
        command = item.get("command")
        if isinstance(command, str):
            yield "command_execution", "command_execution", command

    payload = record.get("payload")
    if not isinstance(payload, dict):
        return
    if payload.get("type") == "function_call":
        name = payload.get("name")
        tool_name = name if isinstance(name, str) else "function_call"
        for command in _argument_strings(payload.get("arguments")):
            yield "function_call", tool_name, command
    if payload.get("type") == "command_execution":
        command = payload.get("command")
        if isinstance(command, str):
            yield "command_execution", "command_execution", command


def _argument_strings(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return (value,)
        return _argument_strings(decoded)
    if isinstance(value, dict):
        return tuple(
            item
            for key in ("cmd", "command", "input", "patch", "script")
            if isinstance((item := value.get(key)), str)
        )
    return ()


def _matching_skills(command: str, skills: dict[str, str]) -> tuple[str, ...]:
    return tuple(sorted({name for path, name in skills.items() if path in command}))


def _action(tool_name: str, command: str) -> Literal["read", "maintenance", "unknown"]:
    lowered = command.lower()
    if "apply_patch" in tool_name.lower() or _WRITE_RE.search(lowered):
        return "maintenance"
    if _READ_RE.search(lowered):
        return "read"
    return "unknown"


def _skills_by_session(candidates: Iterable[_Candidate]) -> dict[str, set[str]]:
    by_session: dict[str, set[str]] = {}
    for candidate in candidates:
        by_session.setdefault(candidate.session, set()).add(candidate.skill)
    return by_session


def _events(candidates: Iterable[_Candidate], broad_sessions: set[str]) -> Iterable[UsageEvent]:
    for candidate in candidates:
        if candidate.action == "maintenance":
            category: Category = "maintenance"
            confidence = "medium"
        elif candidate.session in broad_sessions:
            category = "broad_scan"
            confidence = "low"
        elif candidate.worker:
            category = "worker_read"
            confidence = "low"
        elif candidate.action == "read":
            category = "activation"
            confidence = "medium"
        else:
            category = "unknown"
            confidence = "low"
        yield UsageEvent(
            timestamp=candidate.timestamp,
            harness="codex",
            session=candidate.session,
            skill=candidate.skill,
            source=candidate.source,
            confidence=confidence,
            category=category,
        )


def _deduplicate(events: Iterable[UsageEvent]) -> tuple[UsageEvent, ...]:
    ordered = sorted(
        events,
        key=lambda event: (
            event.session,
            event.skill,
            event.category,
            event.source,
            event.timestamp,
        ),
    )
    seen: set[tuple[str, str, Category, str]] = set()
    unique: list[UsageEvent] = []
    for event in ordered:
        key = (event.session, event.skill, event.category, event.source)
        if key not in seen:
            seen.add(key)
            unique.append(event)
    return tuple(
        sorted(
            unique,
            key=lambda event: (
                event.timestamp,
                event.session,
                event.skill,
                event.category,
                event.source,
            ),
        )
    )


def _summary(events: Iterable[UsageEvent]) -> dict[str, object]:
    materialized = tuple(events)
    categories = Counter(event.category for event in materialized)
    skills = Counter(event.skill for event in materialized)
    return {
        "total_events": len(materialized),
        "by_category": dict(sorted(categories.items())),
        "by_skill": dict(sorted(skills.items())),
    }
