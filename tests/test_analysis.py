from pathlib import Path

from changeripple.analysis import analyze

FIX = Path(__file__).parent / "fixtures"


def test_analysis_suggests_related_tests_and_docs():
    report = analyze(FIX / "sample_py", ["pkg/core.py"], max_depth=4)
    assert "tests/test_core.py" in report.suggested_tests
    assert "tests/test_api.py" in report.suggested_tests
    assert "README.md" in report.suggested_docs
    assert report.score >= 0


def test_analysis_attaches_import_edge_evidence():
    report = analyze(FIX / "sample_py", ["pkg/core.py"], max_depth=4)
    impacts = {impact.path: impact for impact in report.affected_files}
    assert impacts["pkg/service.py"].imported_path == "pkg/core.py"
    assert impacts["pkg/api.py"].imported_path == "pkg/service.py"


def test_test_suggestions_explain_dependency_graph_matches():
    report = analyze(FIX / "sample_py", ["pkg/core.py"], max_depth=4)
    evidence = {item.path: item for item in report.test_evidence}
    assert evidence["tests/test_core.py"].reason == "dependency-graph"
    assert evidence["tests/test_core.py"].distance == 1


def test_test_suggestions_explain_name_similarity_matches(tmp_path):
    (tmp_path / "core.py").write_text("VALUE = 1\n", encoding="utf-8")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_core.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")

    report = analyze(tmp_path, ["core.py"])
    evidence = {item.path: item for item in report.test_evidence}
    assert evidence["tests/test_core.py"].reason == "name-similarity"
    assert evidence["tests/test_core.py"].related_path == "core.py"
    assert evidence["tests/test_core.py"].distance is None


def test_public_api_signal():
    report = analyze(FIX / "sample_py", ["pkg/api.py"])
    assert any(s.code == "public-surface" for s in report.risk_signals)


def test_security_signal_is_high(tmp_path):
    (tmp_path / "auth.py").write_text("TOKEN = None\n", encoding="utf-8")
    report = analyze(tmp_path, ["auth.py"])
    assert any(s.code == "security-sensitive" and s.level == "high" for s in report.risk_signals)
