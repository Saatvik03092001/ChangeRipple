from __future__ import annotations

import ast
import re
from pathlib import Path

PY_EXT = {".py"}
JS_EXT = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}

_JS_IMPORT_RE = re.compile(
    r"(?:import(?:.|\n)*?from\s*|require\s*\(|import\s*\()\s*['\"]([^'\"]+)['\"]",
    re.MULTILINE,
)


def parse_python_imports(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
    except (OSError, UnicodeDecodeError, SyntaxError):
        return []
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            prefix = "." * node.level
            module = node.module or ""
            names.append(prefix + module)
    return names


def parse_js_imports(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    return [match.group(1) for match in _JS_IMPORT_RE.finditer(text)]
