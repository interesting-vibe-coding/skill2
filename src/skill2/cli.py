from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .lint import lint_path
from .scaffold import scaffold_skill


def _add_lint_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", nargs="?", default="skills", help="skill dir or skills root")
    parser.add_argument("--json", action="store_true", help="emit JSON")


def _cmd_scaffold(args: argparse.Namespace) -> int:
    if args.kind != "skill":
        print("only `skill2 scaffold skill <name>` is implemented", file=sys.stderr)
        return 2
    created = scaffold_skill(args.name, Path(args.output_dir), args.description)
    for path in created:
        print(path)
    return 0


def _cmd_lint(args: argparse.Namespace) -> int:
    result = lint_path(Path(args.path))
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        for issue in result.issues:
            print(f"{issue.severity} {issue.path}: {issue.message}")
        print(f"checked={result.checked} issues={len(result.issues)}")
    return 1 if result.has_errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skill2")
    sub = parser.add_subparsers(dest="command", required=True)

    scaffold = sub.add_parser("scaffold", help="create skill scaffolds")
    scaffold.add_argument("kind", choices=["skill"])
    scaffold.add_argument("name")
    scaffold.add_argument("-o", "--output-dir", default="skills")
    scaffold.add_argument("--description", default=None)
    scaffold.set_defaults(func=_cmd_scaffold)

    lint = sub.add_parser("lint", help="lint skills")
    _add_lint_args(lint)
    lint.set_defaults(func=_cmd_lint)

    scan = sub.add_parser("scan", help="alias for lint")
    _add_lint_args(scan)
    scan.set_defaults(func=_cmd_lint)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
