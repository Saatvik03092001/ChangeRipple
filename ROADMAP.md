# Roadmap

## v0.2 — better language resolution
- [x] Resolve Python package roots from `pyproject.toml`.
- [x] Resolve common TypeScript `paths` aliases.
- [x] Add initial Go module-local import support.
- [ ] Resolve TypeScript workspace packages and deeper `tsconfig` composition.
- [ ] Add Go workspace/replace/build-tag awareness.
- [ ] Add Rust module/use support.

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
