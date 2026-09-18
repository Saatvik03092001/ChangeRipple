# Roadmap

## v0.2 — better language resolution
- Resolve Python package roots from `pyproject.toml`.
- Resolve TypeScript `paths` aliases and workspace packages.
- Add Go import support.
- Add Rust module/use support.

## v0.3 — smarter test mapping
- Learn mappings from coverage.py / pytest JSON reports when provided.
- Consume Jest/Vitest coverage maps without requiring a service.
- Show confidence/evidence per suggested test.

## v0.4 — pull-request ergonomics
- GitHub Action wrapper.
- PR summary formatter.
- Baseline snapshots to detect unexpected blast-radius growth.
- SARIF-like annotations for workflow UIs where appropriate.

## Later
- Monorepo ownership boundaries.
- Plugin API for framework-specific risk rules.
- Optional Codex/LLM adapter that receives only the structured report, never source by default.
