from __future__ import annotations

import ast
import re
from pathlib import Path

PY_EXT = {".py"}
JS_EXT = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}
GO_EXT = {".go"}

_JS_IMPORT_RE = re.compile(
    r"(?:import(?:.|\n)*?from\s*|require\s*\(|import\s*\()\s*['\"]([^'\"]+)['\"]",
    re.MULTILINE,
)
_GO_IMPORT_VALUE_RE = re.compile(
    r'^(?:(?:[A-Za-z_]\w*|[._])\s+)?(?:"([^"]+)"|`([^`]+)`)$'
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


def _parse_go_import_value(value: str) -> str | None:
    match = _GO_IMPORT_VALUE_RE.match(value.strip())
    if match is None:
        return None
    return match.group(1) or match.group(2)


def parse_go_imports(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    # This intentionally handles the ordinary gofmt forms only. Removing block
    # comments first prevents commented-out import declarations from creating edges.
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    imports: list[str] = []
    in_block = False
    for raw_line in text.splitlines():
        line = raw_line.split("//", 1)[0].strip()
        if not line:
            continue

        if in_block:
            if line.startswith(")"):
                in_block = False
                continue
            spec = _parse_go_import_value(line.rstrip(";"))
            if spec:
                imports.append(spec)
            continue

        if not line.startswith("import"):
            continue
        rest = line[len("import"):].strip()
        if rest.startswith("("):
            in_block = True
            rest = rest[1:].strip()
            if rest and not rest.startswith(")"):
                spec = _parse_go_import_value(rest.rstrip(";"))
                if spec:
                    imports.append(spec)
            if rest.endswith(")"):
                in_block = False
            continue

        spec = _parse_go_import_value(rest.rstrip(";"))
        if spec:
            imports.append(spec)
    return imports
