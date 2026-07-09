# Architecture

## Shape

```text
skill2
  scan      read skill files
  usage     read local logs / hook events
  report    build dashboard
  suggest   produce maintenance actions
```

## Data Model

```json
{
  "skill": {
    "name": "agent-search",
    "path": "/repo/skills/agent-search/SKILL.md",
    "description": "Search/read router",
    "body_tokens": 1200,
    "references": ["references/search-strategy.md"],
    "scripts": ["scripts/internet-reach-doctor.sh"],
    "scope": "global"
  }
}
```

```json
{
  "activation": {
    "timestamp": "2026-07-09T21:00:00Z",
    "harness": "codex",
    "session": "rollout-...",
    "skill": "agent-search",
    "source": "log-path-match",
    "confidence": 0.45
  }
}
```

```json
{
  "suggestion": {
    "action": "downgrade_to_reference",
    "target": "smart-fetch",
    "parent": "agent-search",
    "reason": "component skill mostly used through parent search router",
    "evidence": ["low direct usage", "parent references it"]
  }
}
```

## Pipeline

1. Parse skill tree.
2. Parse usage events.
3. Join by normalized skill name and canonical path.
4. Compute metrics.
5. Run suggestion rules.
6. Render HTML + JSON.

## Event Confidence

Use conservative labels.

| Signal | Confidence |
| --- | --- |
| explicit skill invocation event | high |
| system skill list only | ignore |
| `Read` tool on exact hub `SKILL.md` | medium |
| path string appears in old transcript | low |
| edit to skill file | maintenance, not activation |

## Hook Route

Logs may be incomplete. Add optional hook recorder:

```json
{"ts":"...","harness":"codex","event":"skill_read","skill":"agent-search","path":"..."}
```

Store locally:

```text
~/.skill2/events.jsonl
```

No network. No hosted telemetry.
