# Maintainer Backlog

These are intentionally real, scoped follow-up tasks for contributors after v0.1.0 is published.

## Good first issues

1. **TypeScript path aliases** — read `compilerOptions.paths` and resolve simple aliases.
2. **Python pyproject roots** — inspect `pyproject.toml` for package/source layout hints.
3. **Evidence in JSON** — include the import edge that caused each affected-file result.
4. **Go MVP** — parse local module imports using `go.mod` module name.
5. **Test confidence** — show why each test was suggested (graph reach vs filename similarity).

## Help wanted

- Real-world fixtures from Django/FastAPI/React/Vite repositories.
- Windows path edge cases.
- Monorepo/workspace fixtures.
- False-positive and false-negative reports with tiny reproductions.
