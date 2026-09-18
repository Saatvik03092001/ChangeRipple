# AGENTS.md

## Purpose
ChangeRipple is a local-first Python CLI for change-impact analysis.

## Commands
- Tests: `pytest`
- Lint: `ruff check src tests`
- CLI smoke: `python -m changeripple tests/fixtures/sample_py --changed pkg/core.py`

## Contribution rules
- Keep runtime code compatible with Python 3.11+.
- Do not add network calls to normal analysis.
- Never print file contents as a “security finding.” Paths/evidence only.
- New heuristics need regression tests.
- Preserve deterministic ordering in JSON/Markdown outputs.
