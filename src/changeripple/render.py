from __future__ import annotations

import json

from .models import AnalysisReport


def to_json(report: AnalysisReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True)


def _render_test_suggestion(report: AnalysisReport, path: str) -> str:
    evidence = next((item for item in report.test_evidence if item.path == path), None)
    if evidence is None:
        return f"- `{path}`"
    if evidence.reason == "dependency-graph" and evidence.distance is not None:
        return f"- `{path}` — dependency graph; distance {evidence.distance}"
    if evidence.reason == "name-similarity" and evidence.related_path:
        return f"- `{path}` — filename/module similarity to `{evidence.related_path}`"
    return f"- `{path}` — {evidence.reason}"


def to_markdown(report: AnalysisReport) -> str:
    lines = [
        "# ChangeRipple report",
        "",
        f"**Risk score:** {report.score}/100",
        "",
        "## Changed files",
    ]
    lines += [f"- `{p}`" for p in report.changed_files] or ["- None detected"]
    lines += ["", "## Likely affected files"]
    lines += [
        f"- `{impact.path}` — imports `{impact.imported_path}`; dependency distance {impact.distance}"
        if impact.imported_path
        else f"- `{impact.path}` — dependency distance {impact.distance}"
        for impact in report.affected_files
    ] or ["- None detected"]
    lines += ["", "## Suggested tests"]
    lines += [_render_test_suggestion(report, p) for p in report.suggested_tests] or ["- No related tests detected"]
    lines += ["", "## Documentation to review"]
    lines += [f"- `{p}`" for p in report.suggested_docs] or ["- No documentation review suggested"]
    lines += ["", "## Risk signals"]
    lines += [
        f"- **{s.level.upper()} · {s.code}** — {s.message}"
        + (f" (`{s.path}`)" if s.path else "")
        for s in report.risk_signals
    ] or ["- No elevated signals detected"]
    lines += ["", "_ChangeRipple is advisory static analysis. Review and tests remain authoritative._", ""]
    return "\n".join(lines)
