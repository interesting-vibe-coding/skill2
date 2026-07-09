# MVP

## Goal

Build the smallest loop that helps maintain one real skill library.

Target repo:

```bash
~/workspace/my-agent-config
```

## Scope

### 1. scaffold

Status: implemented.

```bash
skill2 scaffold skill my-skill --description "Use when ..."
```

Output:

- `skills/<name>/SKILL.md`

### 2. lint / scan

Status: implemented.

Input: `skills/` directory.

Output:

- skill name
- path
- description
- body token estimate
- references
- scripts
- frontmatter issues
- missing internal references
- missing markdown links
- possible secrets
- machine-local absolute paths
- non-executable scripts

### 3. usage

Status: planned.

Input:

- Codex logs: `~/.codex/archived_sessions/*.jsonl`
- later: Claude/OpenCode hooks

Rules:

- count only current hub paths: `~/workspace/my-agent-config/skills/*/SKILL.md`
- ignore `.codex/plugins/cache`
- ignore `.codex/vendor_imports`
- ignore old `workspace/My-Skills`

Initial event type:

- any target `SKILL.md` path in a session log = activation candidate

Later split:

- real invocation
- maintenance edit
- broad scan
- worker read

### 4. report

Status: planned.

Generate local HTML:

- high-frequency skills
- low-frequency skills
- never-used skills
- recently edited but unused skills
- large skills
- overlapping trigger descriptions
- missing references
- merge/downgrade candidates

### 5. test

Status: planned.

Input:

- one skill directory
- scenario cases
- target harness: `codex` first

Case zones:

- core positive: should activate
- adjacent positive: should activate
- negative: should not activate
- outcome: should produce expected response markers

Isolation:

- temp home
- temp skill root containing only target skill
- empty working directory unless fixture specified
- no user global rules
- no unrelated skills
- no hidden prior context

### 6. suggest

Status: planned.

Initial rules:

- never used + no project owner -> delete candidate
- low usage + only used through one parent -> downgrade to reference
- high co-activation + overlapping descriptions -> merge candidate
- project-specific path/name/content -> projectize candidate
- high usage + long body -> split references/scripts

## Success Criteria

- `skill2 scan ~/workspace/my-agent-config/skills` emits useful JSON.
- `skill2 scaffold skill <name>` creates valid `SKILL.md`.
- `skill2 lint skills` exits 0 on current Skill2 skills.
- `skill2 usage --codex ~/.codex` extracts at least one real skill path signal.
- `skill2 test <skill>` runs positive/negative scenarios in isolated Codex mode.
- `skill2 report` creates readable local HTML.
- `skill2 suggest` reproduces the `agent-search` consolidation decision.

## Non-Goals

- SaaS.
- Hosted telemetry.
- Replacing Codex/Claude skill discovery.
- Marketplace search.
- Automatic deletion without human review.
