from pathlib import Path

from changeripple.graph import build_reverse_graph, transitive_dependents
from changeripple.parsers import parse_go_imports

FIX = Path(__file__).parent / "fixtures"


def test_go_parser_handles_single_grouped_and_aliased_imports():
    root = FIX / "sample_go"
    assert parse_go_imports(root / "internal/service/service.go") == [
        "fmt",
        "example.com/changeripple/sample/internal/core",
    ]
    assert parse_go_imports(root / "cmd/app/main.go") == [
        "example.com/changeripple/sample/internal/service"
    ]


def test_go_reverse_graph_uses_module_name_for_local_imports():
    root = FIX / "sample_go"
    graph = build_reverse_graph(root)
    assert "internal/service/service.go" in graph["internal/core/core.go"]
    assert "cmd/app/main.go" in graph["internal/service/service.go"]

    deps = transitive_dependents(graph, ["internal/core/core.go"], max_depth=3)
    assert deps["internal/service/service.go"] == 1
    assert deps["cmd/app/main.go"] == 2
