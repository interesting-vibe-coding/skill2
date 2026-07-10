from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .lint import lint_scan
from .models import SCHEMA_VERSION, Issue, LintResult, ScanResult, Severity
from .scaffold import scaffold_skill
from .scan import scan_path

_SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"
_SARIF_LEVEL = {
    Severity.ERROR: "error",
    Severity.WARN: "warning",
    Severity.ADVICE: "note",
}


def _add_output_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", nargs="?", default="skills", help="skill dir or skills root")
    parser.add_argument(
        "--format",
        choices=("text", "json", "sarif"),
        default="text",
        help="output format (default: text)",
    )
    parser.add_argument(
        "--json",
        action="store_const",
        const="json",
        dest="format",
        help="alias for --format json",
    )


def _cmd_scaffold(args: argparse.Namespace) -> int:
    if args.kind != "skill":
        print("only `skill2 scaffold skill <name>` is implemented", file=sys.stderr)
        return 2
    created = scaffold_skill(args.name, Path(args.output_dir), args.description)
    for path in created:
        print(path)
    return 0


def _cmd_scan(args: argparse.Namespace) -> int:
    result = scan_path(Path(args.path))
    if args.format == "json":
        _print_json(result.to_dict())
    elif args.format == "sarif":
        _print_json(_to_sarif((), scan=result))
    else:
        _print_scan_text(result)
    return 0


def _cmd_lint(args: argparse.Namespace) -> int:
    result = lint_scan(scan_path(Path(args.path)))
    if args.format == "json":
        _print_json(result.to_dict())
    elif args.format == "sarif":
        _print_json(_to_sarif(result.issues))
    else:
        _print_lint_text(result)
    return 1 if result.has_errors else 0


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _print_scan_text(result: ScanResult) -> None:
    for skill in result.skills:
        print(
            f"{skill.name} {skill.path} tokens={skill.body_tokens} "
            f"references={len(skill.references)} scripts={len(skill.scripts)} "
            f"assets={len(skill.assets)} scope={skill.scope}"
        )
    print(f"scanned={len(result.skills)}")


def _print_lint_text(result: LintResult) -> None:
    for issue in result.issues:
        print(f"{issue.severity.value} {issue.rule_id} {issue.path}: {issue.message}")
    print(f"checked={result.checked} issues={len(result.issues)}")


def _to_sarif(issues: tuple[Issue, ...], *, scan: ScanResult | None = None) -> dict[str, Any]:
    rule_ids = sorted({issue.rule_id for issue in issues})
    run: dict[str, Any] = {
        "tool": {
            "driver": {
                "name": "skill2",
                "informationUri": "https://github.com/MisterBrookT/skill2",
                "rules": [{"id": rule_id} for rule_id in rule_ids],
            }
        },
        "results": [_sarif_result(issue) for issue in issues],
        "properties": {"skill2_schema_version": SCHEMA_VERSION},
    }
    if scan is not None:
        run["properties"]["scan"] = scan.to_dict()
    return {"$schema": _SARIF_SCHEMA, "version": "2.1.0", "runs": [run]}


def _sarif_result(issue: Issue) -> dict[str, Any]:
    return {
        "ruleId": issue.rule_id,
        "level": _SARIF_LEVEL[issue.severity],
        "message": {"text": issue.message},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": _path_uri(issue.path)},
                }
            }
        ],
    }


def _path_uri(value: str) -> str:
    path = Path(value)
    return path.as_uri() if path.is_absolute() else path.as_posix()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skill2")
    sub = parser.add_subparsers(dest="command", required=True)

    scaffold = sub.add_parser("scaffold", help="create skill scaffolds")
    scaffold.add_argument("kind", choices=["skill"])
    scaffold.add_argument("name")
    scaffold.add_argument("-o", "--output-dir", default="skills")
    scaffold.add_argument("--description", default=None)
    scaffold.set_defaults(func=_cmd_scaffold)

    scan = sub.add_parser("scan", help="scan skill inventory")
    _add_output_args(scan)
    scan.set_defaults(func=_cmd_scan)

    lint = sub.add_parser("lint", help="lint scanned skills")
    _add_output_args(lint)
    lint.set_defaults(func=_cmd_lint)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
