from pathlib import Path
from changeripple.cli import main

FIX = Path(__file__).parent / "fixtures"

def test_cli_with_explicit_changed(capsys):
    code = main([str(FIX / "sample_py"), "--changed", "pkg/core.py", "--format", "json"])
    out = capsys.readouterr().out
    assert code == 0
    assert '"pkg/core.py"' in out
