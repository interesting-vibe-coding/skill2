from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Final

SCHEMA_VERSION: Final = "1"


class Severity(StrEnum):
    ERROR = "ERROR"
    WARN = "WARN"
    ADVICE = "ADVICE"


@dataclass(frozen=True)
class ResourceLink:
    target: str
    kind: str
    exists: bool


@dataclass(frozen=True)
class ScriptRecord:
    path: str
    executable: bool


@dataclass(frozen=True)
class SkillSource:
    text: str
    body: str
    frontmatter: dict[str, Any] | None
    frontmatter_error: str | None
    links: tuple[ResourceLink, ...] = ()
    scripts: tuple[ScriptRecord, ...] = ()


@dataclass(frozen=True)
class SkillRecord:
    name: str
    path: str
    description: str
    body_tokens: int
    references: tuple[str, ...]
    scripts: tuple[str, ...]
    assets: tuple[str, ...]
    scope: str
    hash: str
    _source: SkillSource = field(repr=False, compare=False)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "path": self.path,
            "description": self.description,
            "body_tokens": self.body_tokens,
            "references": list(self.references),
            "scripts": list(self.scripts),
            "assets": list(self.assets),
            "scope": self.scope,
            "hash": self.hash,
        }


@dataclass(frozen=True)
class ScanResult:
    root: str
    skills: tuple[SkillRecord, ...]
    schema_version: str = field(default=SCHEMA_VERSION, init=False)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "root": self.root,
            "skills": [skill.to_dict() for skill in self.skills],
        }


@dataclass(frozen=True)
class Issue:
    severity: Severity
    path: str
    message: str
    rule_id: str

    def to_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity.value,
            "path": self.path,
            "message": self.message,
            "rule_id": self.rule_id,
        }


@dataclass(frozen=True)
class LintResult:
    root: str
    checked: int
    issues: tuple[Issue, ...]
    schema_version: str = field(default=SCHEMA_VERSION, init=False)

    @property
    def has_errors(self) -> bool:
        return any(issue.severity is Severity.ERROR for issue in self.issues)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "root": self.root,
            "checked": self.checked,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass(frozen=True)
class Case:
    name: str
    prompt: str
    expect_activation: str | None = None
    expect_not_activation: tuple[str, ...] = ()
    assertions: tuple[dict[str, Any], ...] = ()
    schema_version: str = field(default=SCHEMA_VERSION, init=False)


@dataclass(frozen=True)
class TestRun:
    case: str
    status: str
    skill_hash: str
    evidence: tuple[str, ...] = ()
    schema_version: str = field(default=SCHEMA_VERSION, init=False)


@dataclass(frozen=True)
class ActivationEvent:
    timestamp: str
    harness: str
    session: str
    skill: str
    source: str
    confidence: float
    schema_version: str = field(default=SCHEMA_VERSION, init=False)


@dataclass(frozen=True)
class Suggestion:
    action: str
    target: str
    reason: str
    evidence: tuple[str, ...]
    schema_version: str = field(default=SCHEMA_VERSION, init=False)
