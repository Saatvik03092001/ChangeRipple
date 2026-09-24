# Maintainer Backlog

This file tracks useful follow-up work for contributors and keeps completed MVP tasks visible so the backlog does not drift away from the actual repository state.

## Completed since the initial alpha

- [x] Resolve common TypeScript `compilerOptions.paths` aliases.
- [x] Read Python package/source roots from common `pyproject.toml` layouts.
- [x] Include deterministic import-edge evidence in JSON/Markdown reports.
- [x] Add initial Go module-local import support.
- [x] Explain why each test was suggested.

## Next contributor targets

1. **TypeScript composition/workspaces** — follow common `extends`, project-reference, and workspace-package layouts without turning resolution into a package-manager implementation.
2. **Go workspace resolution** — add focused support for `go.work`, local `replace` directives, and clearly scoped build-tag behavior.
3. **Rust MVP** — map straightforward local `mod` / `use` relationships with fixture-backed tests.
4. **Windows path fixtures** — add regressions for drive letters, separators, case behavior, and repository-relative normalization.
5. **PR ergonomics** — package the existing CLI/report behavior into a reusable GitHub Action or concise PR-summary workflow.

## Help wanted

- Real-world fixtures from Django/FastAPI/React/Vite repositories.
- Monorepo/workspace fixtures.
- False-positive and false-negative reports with tiny reproductions.
- Feedback on which report evidence saves maintainers the most review time.
