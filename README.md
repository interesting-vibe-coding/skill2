# Skill2

Skills for your skills.

Skill2 is a skill pack plus optional CLI for building, testing, packaging, auditing, and pruning agent skills inside your own repos.

Skills are the product surface. CLI is scaffolding and deterministic checks used by those skills.

[中文](README.zh.md)

## Status

Design repo. CLI not shipped yet.

## Why

Agent skills are becoming package-like. They need the same maintenance loop as code:

- lint: broken frontmatter, long descriptions, missing references, unsafe scripts
- coverage: which skills actually trigger
- analytics: high-frequency, low-frequency, never-used, co-activated skills
- pruning: delete, merge, downgrade to reference, or move to project-level scope

Most existing tools stop at validation. Skill2 aims at library governance.

## Install

```bash
git clone https://github.com/MisterBrookT/skill2.git
cd skill2
./install.sh codex
```

Manual repo-local install:

```bash
cp -R skills/skill2-* /path/to/repo/.agents/skills/
```

## Skill Pack

- `skill2-build`: create or improve a skill.
- `skill2-test`: isolated activation/outcome testing.
- `skill2-package`: make a skill repo installable.
- `skill2-audit`: scan a skill library.
- `skill2-prune`: suggest keep/merge/downgrade/projectize/delete.

## Planned CLI

```bash
skill2 scan ~/workspace/my-agent-config/skills --json > skill2-scan.json
skill2 usage --codex ~/.codex --claude ~/.claude --opencode ~/.config/opencode --json > skill2-usage.json
skill2 test ./skills/agent-search --agent codex --cases cases/agent-search.yaml --isolate
skill2 report --scan skill2-scan.json --usage skill2-usage.json --out report.html
skill2 suggest --repo ~/workspace/my-agent-config
```

## Core Ideas

| Layer | Output |
| --- | --- |
| Scan | structure issues, token size, references, scripts, duplicate descriptions |
| Usage | skill activation candidates from local harness logs or hooks |
| Test | isolated scenario runs: should activate, should not activate, should satisfy assertions |
| Quality | routing tests, confusion matrix, Hit@1/Hit@5 |
| Report | dashboard for hot/cold/unused skills and risk flags |
| Suggest | keep, merge, downgrade, projectize, delete |

## First Target

Reproduce one real maintenance decision:

`search-strategy`, `smart-fetch`, and `internet-reach` should be downgraded from top-level skills into `agent-search/references/`.

## Docs

- [MVP](docs/MVP.md)
- [Product direction](docs/PRODUCT_DIRECTION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Isolated testing](docs/ISOLATED_TESTING.md)
- [Prior art](docs/PRIOR_ART.md)
- [Popular skill repo references](docs/SKILL_REPO_REFERENCES.md)

## License

MIT
