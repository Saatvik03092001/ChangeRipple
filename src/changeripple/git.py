from __future__ import annotations

import subprocess
from pathlib import Path


class GitError(RuntimeError):
    pass


def _run(root: Path, args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise GitError(proc.stderr.strip() or "git command failed")
    return proc.stdout


def repo_root(path: Path) -> Path:
    out = _run(path, ["rev-parse", "--show-toplevel"]).strip()
    return Path(out).resolve()


def changed_files(root: Path, base: str | None, head: str | None) -> list[str]:
    if base and head:
        spec = f"{base}...{head}"
        out = _run(root, ["diff", "--name-only", "--diff-filter=ACMR", spec])
    elif base:
        out = _run(root, ["diff", "--name-only", "--diff-filter=ACMR", base])
    else:
        unstaged = _run(root, ["diff", "--name-only", "--diff-filter=ACMR"])
        staged = _run(root, ["diff", "--cached", "--name-only", "--diff-filter=ACMR"])
        out = unstaged + "\n" + staged
    return sorted({line.strip() for line in out.splitlines() if line.strip()})
