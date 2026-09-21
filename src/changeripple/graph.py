from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
import tomllib
from typing import Iterable

from .ignore import should_ignore
from .parsers import JS_EXT, PY_EXT, parse_js_imports, parse_python_imports

CODE_EXT = PY_EXT | JS_EXT


def discover_code_files(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in CODE_EXT and not should_ignore(p.relative_to(root))
    )


def _configured_python_roots(root: Path) -> list[Path]:
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        return []

    try:
        with pyproject.open("rb") as file:
            config = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError):
        return []

    tool = config.get("tool")
    if not isinstance(tool, dict):
        return []

    root_specs: list[str] = []

    setuptools = tool.get("setuptools")
    if isinstance(setuptools, dict):
        package_dir = setuptools.get("package-dir")
        if isinstance(package_dir, dict):
            default_root = package_dir.get("")
            if isinstance(default_root, str):
                root_specs.append(default_root)

    poetry = tool.get("poetry")
    if isinstance(poetry, dict):
        packages = poetry.get("packages")
        if isinstance(packages, list):
            for package in packages:
                if isinstance(package, dict):
                    source_root = package.get("from")
                    if isinstance(source_root, str):
                        root_specs.append(source_root)

    hatch = tool.get("hatch")
    if isinstance(hatch, dict):
        build = hatch.get("build")
        if isinstance(build, dict):
            targets = build.get("targets")
            if isinstance(targets, dict):
                wheel = targets.get("wheel")
                if isinstance(wheel, dict):
                    packages = wheel.get("packages")
                    if isinstance(packages, list):
                        for package in packages:
                            if isinstance(package, str):
                                root_specs.append(Path(package).parent.as_posix())

    configured: list[Path] = []
    for root_spec in root_specs:
        candidate = (root / root_spec).resolve()
        if candidate.is_relative_to(root):
            configured.append(candidate)
    return configured


def _python_roots(root: Path) -> list[Path]:
    roots = [root, (root / "src").resolve(), *_configured_python_roots(root)]
    return list(dict.fromkeys(roots))


def _python_candidates(source: Path, spec: str, package_roots: Iterable[Path]) -> list[Path]:
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
    candidates: list[Path] = []
    for package_root in package_roots:
        stem = package_root.joinpath(*parts)
        candidates.extend([stem.with_suffix(".py"), stem / "__init__.py"])
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
    python_roots = _python_roots(root)
    reverse: dict[str, set[str]] = defaultdict(set)
    for source in files:
        suffix = source.suffix.lower()
        specs = parse_python_imports(source) if suffix in PY_EXT else parse_js_imports(source)
        for spec in specs:
            candidates = (
                _python_candidates(source, spec, python_roots)
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


def transitive_dependents_with_evidence(
    reverse_graph: dict[str, set[str]], changed: Iterable[str], max_depth: int = 3
) -> dict[str, tuple[int, str]]:
    """Return dependent distance plus the immediate import edge used to reach it."""
    result: dict[str, tuple[int, str]] = {}
    roots = sorted(set(changed))
    queue: deque[tuple[str, int]] = deque((p, 0) for p in roots)
    seen = set(roots)
    while queue:
        current, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for dep in sorted(reverse_graph.get(current, ())):
            if dep in seen:
                continue
            seen.add(dep)
            result[dep] = (depth + 1, current)
            queue.append((dep, depth + 1))
    return result


def transitive_dependents(
    reverse_graph: dict[str, set[str]], changed: Iterable[str], max_depth: int = 3
) -> dict[str, int]:
    evidence = transitive_dependents_with_evidence(reverse_graph, changed, max_depth=max_depth)
    return {path: distance for path, (distance, _) in evidence.items()}
