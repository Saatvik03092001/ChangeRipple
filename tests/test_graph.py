from pathlib import Path

from changeripple.graph import (
    build_reverse_graph,
    transitive_dependents,
    transitive_dependents_with_evidence,
)

FIX = Path(__file__).parent / "fixtures"


def test_python_reverse_graph():
    root = FIX / "sample_py"
    graph = build_reverse_graph(root)
    assert "pkg/service.py" in graph["pkg/core.py"]
    assert "pkg/api.py" in graph["pkg/service.py"]
    assert "tests/test_core.py" in graph["pkg/core.py"]


def test_python_transitive_dependents():
    root = FIX / "sample_py"
    graph = build_reverse_graph(root)
    deps = transitive_dependents(graph, ["pkg/core.py"], max_depth=4)
    assert deps["pkg/service.py"] == 1
    assert deps["pkg/api.py"] == 2
    assert "tests/test_api.py" in deps


def test_transitive_dependents_preserve_import_edge_evidence():
    root = FIX / "sample_py"
    graph = build_reverse_graph(root)
    deps = transitive_dependents_with_evidence(graph, ["pkg/core.py"], max_depth=4)
    assert deps["pkg/service.py"] == (1, "pkg/core.py")
    assert deps["pkg/api.py"] == (2, "pkg/service.py")


def test_js_reverse_graph():
    root = FIX / "sample_js"
    graph = build_reverse_graph(root)
    assert "src/service.ts" in graph["src/util.ts"]
    assert "tests/service.test.ts" in graph["src/service.ts"]
