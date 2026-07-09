from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


_LOCAL_PATH_RE = re.compile(r"/Users/[A-Za-z0-9._-]+/|/home/[A-Za-z0-9._-]+/")
_SECRET_RE = re.compile(
    r"(sk-[A-Za-z0-9_-]{8,}|ghp_[A-Za-z0-9_]{8,}|(?:api[_-]?key|password|secret|token)\s*[:=])",
    re.I,
)


@dataclass(frozen=True)
class Issue:
    severity: str
    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"severity": self.severity, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class LintResult:
    checked: int
    issues: list[Issue]

    @property
    def has_errors(self) -> bool:
        return any(issue.severity == "ERROR" for issue in self.issues)

    def to_dict(self) -> dict[str, object]:
        return {
            "checked": self.checked,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def lint_path(path: Path) -> LintResult:
    skill_files = _find_skill_files(path)
    issues: list[Issue] = []
    for skill_file in skill_files:
        issues.extend(_lint_skill(skill_file))
    if not skill_files:
        issues.append(Issue("ERROR", str(path), "no SKILL.md found"))
    return LintResult(checked=len(skill_files), issues=issues)


def _find_skill_files(path: Path) -> list[Path]:
    if path.is_file() and path.name == "SKILL.md":
        return [path]
    if path.is_dir() and (path / "SKILL.md").exists():
        return [path / "SKILL.md"]
    if path.is_dir():
        return sorted(path.glob("*/SKILL.md"))
    return []


def _lint_skill(skill_file: Path) -> list[Issue]:
    issues: list[Issue] = []
    text = skill_file.read_text(encoding="utf-8")
    fm, body = _split_frontmatter(text)
    rel = str(skill_file)

    if fm is None:
        issues.append(Issue("ERROR", rel, "missing frontmatter"))
        return issues

    name = fm.get("name", "")
    description = fm.get("description", "")
    expected = skill_file.parent.name

    if not name:
        issues.append(Issue("ERROR", rel, "missing name"))
    elif name != expected:
        issues.append(Issue("ERROR", rel, f"name `{name}` does not match directory `{expected}`"))

    if not description:
        issues.append(Issue("ERROR", rel, "missing description"))
    elif len(description) > 140:
        issues.append(Issue("WARN", rel, "description too long"))

    if len(body.strip()) < 40:
        issues.append(Issue("WARN", rel, "body too short"))

    if _LOCAL_PATH_RE.search(body):
        issues.append(Issue("WARN", rel, "contains machine-local absolute path"))

    if _SECRET_RE.search(text):
        issues.append(Issue("ERROR", rel, "possible secret or credential text"))

    scripts_dir = skill_file.parent / "scripts"
    if scripts_dir.is_dir():
        for script in sorted(p for p in scripts_dir.iterdir() if p.is_file()):
            if script.suffix in {".sh", ".py"} and not _is_executable(script):
                issues.append(Issue("WARN", str(script), "script is not executable"))

    for ref in _markdown_links(body):
        if "://" in ref or ref.startswith("#"):
            continue
        target = (skill_file.parent / ref).resolve()
        if not target.exists():
            issues.append(Issue("ERROR", rel, f"missing reference: {ref}"))

    return issues


def _is_executable(path: Path) -> bool:
    return bool(path.stat().st_mode & 0o111)


def _split_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] == '"':
            value = value[1:-1]
        data[key.strip()] = value
    return data, body


def _markdown_links(text: str) -> list[str]:
    refs: list[str] = []
    i = 0
    while True:
        start = text.find("](", i)
        if start == -1:
            break
        end = text.find(")", start + 2)
        if end == -1:
            break
        refs.append(text[start + 2 : end].strip())
        i = end + 1
    return refs
