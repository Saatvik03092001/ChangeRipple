from changeripple.models import AnalysisReport, RiskSignal
from changeripple.render import to_json, to_markdown


def test_markdown_contains_score():
    report = AnalysisReport(root=".", base=None, head=None, changed_files=["a.py"], score=12)
    text = to_markdown(report)
    assert "12/100" in text
    assert "`a.py`" in text


def test_json_is_machine_readable():
    report = AnalysisReport(root=".", base=None, head=None, changed_files=["a.py"], risk_signals=[RiskSignal("medium", "x", "y")])
    text = to_json(report)
    assert '"changed_files"' in text
    assert '"code": "x"' in text
