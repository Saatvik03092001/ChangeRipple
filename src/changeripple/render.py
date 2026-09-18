from __future__ import annotations

import json
from .models import AnalysisReport


def to_json(report: AnalysisReport) -> str:
    return json.dumps(report.as_dict(), indent=2, sort_keys=True)


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
    lines += [f"- `{x.path}` — dependency distance {x.distance}" for x in report.affected_files] or ["- None detected"]
    lines += ["", "## Suggested tests"]
    lines += [f"- `{p}`" for p in report.suggested_tests] or ["- No related tests detected"]
    lines += ["", "## Documentation to review"]
    lines += [f"- `{p}`" for p in report.suggested_docs] or ["- No documentation review suggested"]
    lines += ["", "## Risk signals"]
    lines += [f"- **{s.level.upper()} · {s.code}** — {s.message}" + (f" (`{s.path}`)" if s.path else "") for s in report.risk_signals] or ["- No elevated signals detected"]
    lines += ["", "_ChangeRipple is advisory static analysis. Review and tests remain authoritative._", ""]
    return "\n".join(lines)
