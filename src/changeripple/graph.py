from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
from typing import Iterable

from .ignore import should_ignore
from .parsers import JS_EXT, PY_EXT, parse_js_imports, parse_python_imports

CODE_EXT = PY_EXT | JS_EXT


def discover_code_files(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in CODE_EXT and not should_ignore(p.relative_to(root))
    )


def _python_candidates(root: Path, source: Path, spec: str) -> list[Path]:
    if not spec:
        return []
    if spec.startswith("."):
        dots = len(spec) - len(spec.lstrip("."))
        module = spec[dots:]
        base = source.parent
        for _ in range(max(0, dots - 1)):
            base = base.parent
        parts = [p for p in module.split(".") if p]
        stem = base.joinpath(*parts) if parts else base
        return [stem.with_suffix(".py"), stem / "__init__.py"]
    parts = spec.split(".")
    stem = root.joinpath(*parts)
    candidates = [stem.with_suffix(".py"), stem / "__init__.py"]
    stem2 = root / "src" / Path(*parts)
    candidates += [stem2.with_suffix(".py"), stem2 / "__init__.py"]
    return candidates


def _js_candidates(source: Path, spec: str) -> list[Path]:
    if not spec.startswith("."):
        return []
    stem = (source.parent / spec).resolve()
    exts = [".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"]
    candidates = [stem]
    candidates.extend(stem.with_suffix(ext) for ext in exts)
    candidates.extend(stem / f"index{ext}" for ext in exts)
    return candidates


def build_reverse_graph(root: Path, files: Iterable[Path] | None = None) -> dict[str, set[str]]:
    root = root.resolve()
    files = list(files or discover_code_files(root))
    existing = {p.resolve() for p in files}
    reverse: dict[str, set[str]] = defaultdict(set)
    for source in files:
        suffix = source.suffix.lower()
        specs = parse_python_imports(source) if suffix in PY_EXT else parse_js_imports(source)
        for spec in specs:
            candidates = (
                _python_candidates(root, source, spec)
                if suffix in PY_EXT
                else _js_candidates(source, spec)
            )
            for candidate in candidates:
                resolved = candidate.resolve()
                if resolved in existing:
                    imported = resolved.relative_to(root).as_posix()
                    importer = source.resolve().relative_to(root).as_posix()
                    reverse[imported].add(importer)
                    break
    return dict(reverse)


def transitive_dependents(
    reverse_graph: dict[str, set[str]], changed: Iterable[str], max_depth: int = 3
) -> dict[str, int]:
    distance: dict[str, int] = {}
    queue: deque[tuple[str, int]] = deque((p, 0) for p in changed)
    seen = set(changed)
    while queue:
        current, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for dep in sorted(reverse_graph.get(current, ())):
            if dep in seen:
                continue
            seen.add(dep)
            distance[dep] = depth + 1
            queue.append((dep, depth + 1))
    return distance
