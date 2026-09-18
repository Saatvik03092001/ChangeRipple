from __future__ import annotations

from pathlib import Path

from .graph import build_reverse_graph, transitive_dependents
from .ignore import should_ignore
from .models import AnalysisReport, FileImpact, RiskSignal, normalize_paths

DOC_NAMES = {"README.md", "CONTRIBUTING.md", "CHANGELOG.md", "SECURITY.md", "docs"}
PUBLIC_HINTS = ("api", "public", "interface", "schema", "routes", "client", "sdk")
CONFIG_NAMES = {
    "pyproject.toml", "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
    "Cargo.toml", "go.mod", "Dockerfile",
}


def _is_test(path: str) -> bool:
    low = path.lower()
    name = Path(path).name.lower()
    return (
        "/tests/" in f"/{low}" or "/test/" in f"/{low}" or
        name.startswith("test_") or ".test." in name or ".spec." in name
    )


def _test_similarity(changed: str, candidate: str) -> int:
    cstem = Path(changed).stem.replace("__init__", "")
    tstem = Path(candidate).stem
    score = 0
    if cstem and cstem.lower() in tstem.lower():
        score += 4
    if Path(changed).parent.name and Path(changed).parent.name in Path(candidate).parts:
        score += 1
    return score


def _suggest_tests(root: Path, changed: list[str], affected: dict[str, int]) -> list[str]:
    all_tests = [
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file()
        and p.suffix.lower() in {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
        and not should_ignore(p.relative_to(root))
        and _is_test(p.relative_to(root).as_posix())
    ]
    direct = {p for p in affected if _is_test(p)}
    ranked: list[tuple[int, str]] = []
    for test in all_tests:
        score = 5 if test in direct else 0
        score += max((_test_similarity(c, test) for c in changed), default=0)
        if score:
            ranked.append((score, test))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [p for _, p in ranked[:20]]


def _suggest_docs(root: Path, changed: list[str]) -> list[str]:
    docs: list[str] = []
    for p in root.rglob("*.md"):
        rel = p.relative_to(root).as_posix()
        if any(part in {".git", "node_modules", ".venv"} for part in p.parts):
            continue
        if p.name in DOC_NAMES or "docs" in p.parts:
            docs.append(rel)
    if not docs:
        return []
    if any(Path(c).name in CONFIG_NAMES or any(h in c.lower() for h in PUBLIC_HINTS) for c in changed):
        return sorted(docs)[:10]
    return [d for d in sorted(docs) if Path(d).name in {"README.md", "CHANGELOG.md"}][:5]


def _risk_signals(changed: list[str], affected: dict[str, int], suggested_tests: list[str]) -> list[RiskSignal]:
    signals: list[RiskSignal] = []
    for path in changed:
        low = path.lower()
        name = Path(path).name
        if name in CONFIG_NAMES or "/.github/workflows/" in f"/{low}":
            signals.append(RiskSignal("medium", "build-config", "Build or dependency configuration changed.", path))
        if any(h in low for h in PUBLIC_HINTS):
            signals.append(RiskSignal("medium", "public-surface", "Possible public API or integration surface changed.", path))
        if any(token in low for token in ("auth", "security", "permission", "crypto", "token")):
            signals.append(RiskSignal("high", "security-sensitive", "Security-sensitive area changed; require focused review.", path))
        if name in {"__init__.py", "index.ts", "index.js"}:
            signals.append(RiskSignal("medium", "export-surface", "Package export surface may have changed.", path))
    if len(affected) >= 10:
        signals.append(RiskSignal("high", "wide-ripple", f"Change reaches {len(affected)} dependent files."))
    elif len(affected) >= 4:
        signals.append(RiskSignal("medium", "moderate-ripple", f"Change reaches {len(affected)} dependent files."))
    if changed and not suggested_tests and not all(_is_test(p) for p in changed):
        signals.append(RiskSignal("medium", "no-tests-found", "No related tests were detected for the changed code."))
    return signals


def _score(signals: list[RiskSignal], affected_count: int) -> int:
    value = min(30, affected_count * 3)
    weights = {"low": 5, "medium": 12, "high": 25}
    value += sum(weights.get(s.level, 0) for s in signals)
    return min(100, value)


def analyze(root: Path, changed_files: list[str], base: str | None = None, head: str | None = None, max_depth: int = 3) -> AnalysisReport:
    root = root.resolve()
    changed = normalize_paths(root, changed_files)
    reverse = build_reverse_graph(root)
    affected = transitive_dependents(reverse, changed, max_depth=max_depth)
    impacts = [FileImpact(path=p, reason="imports changed code", distance=d) for p, d in sorted(affected.items(), key=lambda item: (item[1], item[0]))]
    tests = _suggest_tests(root, changed, affected)
    docs = _suggest_docs(root, changed)
    signals = _risk_signals(changed, affected, tests)
    return AnalysisReport(
        root=str(root), base=base, head=head, changed_files=changed, affected_files=impacts,
        suggested_tests=tests, suggested_docs=docs, risk_signals=signals,
        score=_score(signals, len(affected)),
    )
