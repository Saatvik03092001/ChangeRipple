from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class FileImpact:
    path: str
    reason: str
    distance: int
    imported_path: str | None = None


@dataclass(slots=True)
class TestSuggestion:
    path: str
    reason: str
    related_path: str | None = None
    distance: int | None = None


@dataclass(slots=True)
class RiskSignal:
    level: str
    code: str
    message: str
    path: str | None = None


@dataclass(slots=True)
class AnalysisReport:
    root: str
    base: str | None
    head: str | None
    changed_files: list[str]
    affected_files: list[FileImpact] = field(default_factory=list)
    suggested_tests: list[str] = field(default_factory=list)
    test_evidence: list[TestSuggestion] = field(default_factory=list)
    suggested_docs: list[str] = field(default_factory=list)
    risk_signals: list[RiskSignal] = field(default_factory=list)
    score: int = 0

    def as_dict(self) -> dict:
        return asdict(self)


def normalize_paths(root: Path, paths: Iterable[Path | str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in paths:
        p = Path(item)
        if p.is_absolute():
            try:
                p = p.relative_to(root)
            except ValueError:
                continue
        value = p.as_posix().lstrip("./")
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return sorted(out)
