from __future__ import annotations

import re
from pathlib import Path


_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def scaffold_skill(name: str, output_dir: Path, description: str | None = None) -> list[str]:
    if not _NAME_RE.match(name):
        raise SystemExit(f"invalid skill name: {name}")

    skill_dir = output_dir / name
    skill_file = skill_dir / "SKILL.md"
    if skill_file.exists():
        raise SystemExit(f"skill already exists: {skill_file}")

    skill_dir.mkdir(parents=True, exist_ok=False)
    text = _skill_template(name, description or f"Use when the user asks for {name}.")
    skill_file.write_text(text, encoding="utf-8")
    return [str(skill_file)]


def _skill_template(name: str, description: str) -> str:
    return f"""---
name: {name}
description: "{description}"
---

# {name}

目标：补一句这个 skill 让 agent 学会什么。

## 流程

1. 明确输入。
2. 执行核心步骤。
3. 校验输出。

## 质量门

- 不猜缺失信息。
- 不写无关解释。
- 需要确定性执行时用 `scripts/`。
"""
