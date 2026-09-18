from __future__ import annotations

from pathlib import Path

DEFAULT_IGNORES = {
    ".git", ".venv", "venv", "node_modules", "dist", "build", ".next", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "coverage", ".coverage", "__pycache__",
}


def should_ignore(path: Path) -> bool:
    return any(part in DEFAULT_IGNORES for part in path.parts)
