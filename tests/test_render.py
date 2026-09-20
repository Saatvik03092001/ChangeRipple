from changeripple.models import AnalysisReport, FileImpact, RiskSignal, TestSuggestion
from changeripple.render import to_json, to_markdown


def test_markdown_contains_score():
    report = AnalysisReport(root=".", base=None, head=None, changed_files=["a.py"], score=12)
    text = to_markdown(report)
    assert "12/100" in text
    assert "`a.py`" in text


def test_render_includes_import_edge_evidence():
    report = AnalysisReport(
        root=".",
        base=None,
        head=None,
        changed_files=["pkg/core.py"],
        affected_files=[
            FileImpact(
                path="pkg/service.py",
                reason="imports affected dependency",
                distance=1,
                imported_path="pkg/core.py",
            )
        ],
    )
    markdown = to_markdown(report)
    json_text = to_json(report)
    assert "`pkg/service.py` — imports `pkg/core.py`; dependency distance 1" in markdown
    assert '"imported_path": "pkg/core.py"' in json_text


def test_render_includes_test_suggestion_evidence():
    report = AnalysisReport(
        root=".",
        base=None,
        head=None,
        changed_files=["pkg/core.py"],
        suggested_tests=["tests/test_core.py", "tests/test_api.py"],
        test_evidence=[
            TestSuggestion(path="tests/test_core.py", reason="dependency-graph", distance=1),
            TestSuggestion(
                path="tests/test_api.py",
                reason="name-similarity",
                related_path="pkg/api.py",
            ),
        ],
    )
    markdown = to_markdown(report)
    json_text = to_json(report)
    assert "`tests/test_core.py` — dependency graph; distance 1" in markdown
    assert "`tests/test_api.py` — filename/module similarity to `pkg/api.py`" in markdown
    assert '"reason": "dependency-graph"' in json_text
    assert '"related_path": "pkg/api.py"' in json_text


def test_json_is_machine_readable():
    report = AnalysisReport(
        root=".",
        base=None,
        head=None,
        changed_files=["a.py"],
        risk_signals=[RiskSignal("medium", "x", "y")],
    )
    text = to_json(report)
    assert '"changed_files"' in text
    assert '"code": "x"' in text
