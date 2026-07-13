---
name: skill2-publish
description: "Use when publishing a skill repository, README, release, registry entry, or public install verification."
---

# Publish Skill Repositories

Make a verified package discoverable, understandable, and installable by strangers.

## Ownership

- Publish owns public presentation, release metadata, remote actions, and public reinstall verification.
- Package owns candidate construction and local installability.
- Do not rebuild package internals during release work; return blockers to Package.

## Public Surface

- State product identity and concrete value before implementation detail.
- Prefer native harness install paths first (Claude marketplace primary; Codex curated listing only when true; otherwise current `npx skills add`; manual clone/`install.sh` as fallback).
- Describe six self-contained Skills when that is the product; do not claim a global helper CLI install for users.
- List only shipped capabilities and supported environments.
- State privacy, compatibility, and known limits.
- Keep translated README installation commands byte-identical.
- Keep README, manifests, installer, changelog, and release version consistent.
- Add author/homepage/repository metadata only where the target schema accepts them.

## Preflight

Require clean package check, tests, CI state, working tree, version, changelog, artifacts, checksums, destinations, and public install plan.

## Public install smoke

After package preflight, prove strangers can install and use:

1. Run the documented public installation path(s) into a clean temporary home.
2. Confirm installed Skills are present and self-contained.
3. Run at least one Skill-owned command (`uv run --script <skill-dir>/scripts/run -- …`) without repository checkout or global CLI.

Do not claim a marketplace listing that does not exist yet.

## Remote Gate

Tag, push, release, registry, and marketplace actions require:

1. Exact dry-run.
2. Explicit user confirmation.
3. One controlled execution.
4. Honest failure reporting.
5. Reinstall from public source and verify installed version plus one Skill-owned command.

## Output

Return preflight result, planned remote writes, approval state, published URLs, and public reinstall evidence.

```bash
uv run --script <skill-dir>/scripts/run -- publish-check . --json
```
