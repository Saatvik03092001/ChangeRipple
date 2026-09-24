import tomllib
from pathlib import Path

import pytest

from changeripple import __version__
from changeripple.cli import main

FIX = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).parents[1]


def test_cli_with_explicit_changed(capsys):
    code = main([str(FIX / "sample_py"), "--changed", "pkg/core.py", "--format", "json"])
    out = capsys.readouterr().out
    assert code == 0
    assert '"pkg/core.py"' in out


def test_cli_version_matches_project_metadata(capsys):
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert __version__ == project["project"]["version"]

    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])

    assert excinfo.value.code == 0
    assert capsys.readouterr().out.strip() == f"changeripple {__version__}"
