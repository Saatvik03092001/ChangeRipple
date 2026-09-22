from __future__ import annotations

from collections import defaultdict, deque
import json
from pathlib import Path
import tomllib
from typing import Iterable

from .ignore import should_ignore
from .parsers import JS_EXT, PY_EXT, parse_js_imports, parse_python_imports

CODE_EXT = PY_EXT | JS_EXT
JS_RESOLVE_EXTS = [".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"]


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


def _strip_jsonc(text: str) -> str:
    without_comments: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(text):
        char = text[index]
        if in_string:
            without_comments.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            without_comments.append(char)
            index += 1
            continue
        if char == "/" and index + 1 < len(text) and text[index + 1] == "/":
            index += 2
            while index < len(text) and text[index] not in "\r\n":
                index += 1
            continue
        if char == "/" and index + 1 < len(text) and text[index + 1] == "*":
            index += 2
            while index + 1 < len(text) and text[index : index + 2] != "*/":
                index += 1
            index += 2
            continue
        without_comments.append(char)
        index += 1

    cleaned = "".join(without_comments)
    without_trailing_commas: list[str] = []
    index = 0
    in_string = False
    escaped = False
    while index < len(cleaned):
        char = cleaned[index]
        if in_string:
            without_trailing_commas.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            without_trailing_commas.append(char)
            index += 1
            continue
        if char == ",":
            lookahead = index + 1
            while lookahead < len(cleaned) and cleaned[lookahead].isspace():
                lookahead += 1
            if lookahead < len(cleaned) and cleaned[lookahead] in "}]":
                index += 1
                continue
        without_trailing_commas.append(char)
        index += 1
    return "".join(without_trailing_commas)


def _read_tsconfig(path: Path) -> dict[str, object] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    try:
        config = json.loads(text)
    except json.JSONDecodeError:
        try:
            config = json.loads(_strip_jsonc(text))
        except json.JSONDecodeError:
            return None
    return config if isinstance(config, dict) else None


def _nearest_tsconfig(root: Path, source: Path) -> Path | None:
    current = source.parent.resolve()
    while current.is_relative_to(root):
        candidate = current / "tsconfig.json"
        if candidate.is_file():
            return candidate
        if current == root:
            break
        current = current.parent
    return None


def _js_stem_candidates(stem: Path) -> list[Path]:
    candidates = [stem]
    candidates.extend(stem.with_suffix(ext) for ext in JS_RESOLVE_EXTS)
    candidates.extend(stem / f"index{ext}" for ext in JS_RESOLVE_EXTS)
    return candidates


def _match_ts_path(pattern: str, spec: str) -> str | None:
    if "*" not in pattern:
        return "" if pattern == spec else None
    if pattern.count("*") != 1:
        return None
    prefix, suffix = pattern.split("*", 1)
    if not spec.startswith(prefix) or not spec.endswith(suffix):
        return None
    end = len(spec) - len(suffix) if suffix else len(spec)
    if end < len(prefix):
        return None
    return spec[len(prefix):end]


def _tsconfig_alias_candidates(
    root: Path,
    source: Path,
    spec: str,
    cache: dict[Path, dict[str, object] | None],
) -> list[Path]:
    tsconfig = _nearest_tsconfig(root, source)
    if tsconfig is None:
        return []
    if tsconfig not in cache:
        cache[tsconfig] = _read_tsconfig(tsconfig)
    config = cache[tsconfig]
    if not isinstance(config, dict):
        return []

    compiler_options = config.get("compilerOptions")
    if not isinstance(compiler_options, dict):
        return []
    paths = compiler_options.get("paths")
    if not isinstance(paths, dict):
        return []

    base_url = compiler_options.get("baseUrl")
    base = tsconfig.parent
    if isinstance(base_url, str):
        base = base / base_url
    base = base.resolve()

    entries = sorted(
        paths.items(),
        key=lambda item: ("*" in item[0], -len(item[0].replace("*", "")), item[0]),
    )
    for pattern, targets in entries:
        if not isinstance(pattern, str) or not isinstance(targets, list):
            continue
        captured = _match_ts_path(pattern, spec)
        if captured is None:
            continue

        candidates: list[Path] = []
        for target in targets:
            if not isinstance(target, str) or target.count("*") > 1:
                continue
            mapped = target.replace("*", captured) if "*" in target else target
            candidates.extend(_js_stem_candidates((base / mapped).resolve()))
        return candidates
    return []


def _js_candidates(
    root: Path,
    source: Path,
    spec: str,
    tsconfig_cache: dict[Path, dict[str, object] | None],
) -> list[Path]:
    if spec.startswith("."):
        return _js_stem_candidates((source.parent / spec).resolve())
    return _tsconfig_alias_candidates(root, source, spec, tsconfig_cache)


def build_reverse_graph(root: Path, files: Iterable[Path] | None = None) -> dict[str, set[str]]:
    root = root.resolve()
    files = list(files or discover_code_files(root))
    existing = {p.resolve() for p in files}
    python_roots = _python_roots(root)
    tsconfig_cache: dict[Path, dict[str, object] | None] = {}
    reverse: dict[str, set[str]] = defaultdict(set)
    for source in files:
        suffix = source.suffix.lower()
        specs = parse_python_imports(source) if suffix in PY_EXT else parse_js_imports(source)
        for spec in specs:
            candidates = (
                _python_candidates(source, spec, python_roots)
                if suffix in PY_EXT
                else _js_candidates(root, source, spec, tsconfig_cache)
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
