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

See [docs/maintainer-backlog.md](docs/maintainer-backlog.md) for current contributor targets.

## Ground rules

- Keep runtime dependencies minimal.
- Do not upload repository content or telemetry by default.
- Heuristics must be deterministic and explainable.
- Prefer a missed suggestion over a confident false claim.
- Add tests for behavioral changes.

## Pull requests

Describe: the problem, the approach, test evidence, and known limitations. Small focused PRs are easiest to review. The repository PR template mirrors these fields so reviewers get consistent evidence.

## Maintainer releases

Before tagging a release, follow [docs/releasing.md](docs/releasing.md). The checklist keeps package metadata, runtime version, changelog, smoke checks, and GitHub release notes aligned.
