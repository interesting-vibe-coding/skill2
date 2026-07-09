#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ONLY="${1:-all}"

copy_skills() {
  local dest="$1"
  mkdir -p "$dest"
  for skill in "$ROOT"/skills/*; do
    [ -d "$skill" ] || continue
    cp -R "$skill" "$dest/$(basename "$skill")"
  done
  printf 'installed skills -> %s\n' "$dest"
}

case "$ONLY" in
  all)
    copy_skills "$HOME/.agents/skills"
    [ -d "$HOME/.claude" ] && copy_skills "$HOME/.claude/skills"
    ;;
  codex)
    copy_skills "$HOME/.agents/skills"
    ;;
  claude)
    copy_skills "$HOME/.claude/skills"
    ;;
  *)
    printf 'usage: ./install.sh [all|codex|claude]\n' >&2
    exit 2
    ;;
esac
