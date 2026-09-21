# Changelog

## Unreleased

- Read Python package-root hints from `pyproject.toml` for common setuptools, Poetry, and Hatch layouts, improving import resolution beyond the built-in repository-root and `src/` fallbacks.
- Add deterministic import-edge evidence to affected-file reports in both Markdown and JSON, making transitive impact results easier to audit in CI and maintainer workflows.
- Explain every suggested test with deterministic evidence: either dependency-graph distance or the changed file that triggered filename/module similarity, while preserving the existing `suggested_tests` path list for consumers.

## 0.1.0 - Initial alpha

- Local Git diff discovery and explicit changed-file mode.
- Python and JS/TS local import graph analysis.
- Transitive affected-file discovery.
- Related test/document suggestions.
- Explainable risk signals and 0–100 advisory score.
- Markdown/JSON output and CI threshold exit code.
