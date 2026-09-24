from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .analysis import analyze
from .git import GitError, changed_files as git_changed_files, repo_root
from .render import to_json, to_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="changeripple", description="Trace the likely ripple effects of a code change.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("path", nargs="?", default=".", help="Repository path (default: current directory)")
    parser.add_argument("--base", help="Base git revision")
    parser.add_argument("--head", help="Head git revision (used with --base)")
    parser.add_argument("--changed", action="append", default=[], help="Changed file path; repeat to bypass git diff discovery")
    parser.add_argument("--max-depth", type=int, default=3, choices=range(1, 11), metavar="1-10")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", help="Write report to file instead of stdout")
    parser.add_argument("--fail-over", type=int, default=None, metavar="SCORE", help="Exit 2 when risk score is greater than SCORE")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    start = Path(args.path).resolve()
    try:
        root = repo_root(start)
    except GitError:
        root = start
    changed = args.changed
    if not changed:
        try:
            changed = git_changed_files(root, args.base, args.head)
        except GitError as exc:
            print(f"changeripple: {exc}", file=sys.stderr)
            return 1
    report = analyze(root, changed, base=args.base, head=args.head, max_depth=args.max_depth)
    rendered = to_json(report) if args.format == "json" else to_markdown(report)
    if args.output:
        Path(args.output).write_text(rendered + ("" if rendered.endswith("\n") else "\n"), encoding="utf-8")
    else:
        print(rendered)
    if args.fail_over is not None and report.score > args.fail_over:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
