# Contributing to ChangeRipple

Thanks for helping improve change-impact analysis for open-source maintainers.

## Setup

```bash
python -m pip install -e ".[dev]"
pytest
ruff check src tests
```

## Good first contributions

- Add a fixture that reproduces an import-resolution false positive/negative.
- Improve docs or examples.
- Add support for a common project layout.
- Add tests before changing heuristics.

## Ground rules

- Keep runtime dependencies minimal.
- Do not upload repository content or telemetry by default.
- Heuristics must be deterministic and explainable.
- Prefer a missed suggestion over a confident false claim.
- Add tests for behavioral changes.

## Pull requests

Describe: the problem, the approach, test evidence, and known limitations. Small focused PRs are easiest to review.
