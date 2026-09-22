# ChangeRipple

**See the likely blast radius of a code change before you merge it.**

ChangeRipple is a small, local-first CLI for open-source maintainers and reviewers. It inspects changed files, follows local Python and JavaScript/TypeScript import relationships, suggests related tests and documentation, and highlights review-risk signals.

It does **not** send source code to a cloud service and it does **not** require an AI API key.

> Status: v0.1.0 alpha. ChangeRipple is advisory static analysis, not a substitute for tests or review.

## Why

A pull request may touch only two files while affecting ten more. Reviewers often have to answer the same questions manually:

- Which modules depend on this change?
- Which tests are most relevant?
- Did a public API or security-sensitive area change?
- Should README, changelog, or contributor docs be reviewed?
- Is this PR wider than it looks?

ChangeRipple turns those questions into a repeatable local/CI check.

## Why this matters for modern OSS

Open-source maintainers already carry review, issue-triage, release, security, and quality responsibilities. As AI-assisted development makes it easier to produce larger or more frequent patches, maintainers need fast, deterministic ways to understand change impact before spending scarce review time.

ChangeRipple is intentionally built as a **maintainer-side safety layer** rather than another code generator: it turns a Git diff into an explainable map of affected files, likely tests, documentation review needs, and higher-risk surfaces. It runs locally and can feed the same structured evidence to humans, CI, or coding agents without requiring a hosted source-code analysis service.

The long-term goal is simple: help small OSS teams review more confidently without increasing maintenance overhead.

## Quick start

```bash
python -m pip install -e .
changeripple . --changed src/core.py
```

Against Git history:

```bash
changeripple . --base origin/main --head HEAD
```

Machine-readable output:

```bash
changeripple . --base origin/main --head HEAD --format json --output changeripple.json
```

CI risk gate:

```bash
changeripple . --base origin/main --head HEAD --fail-over 70
```

Exit codes: `0` success, `1` operational error, `2` risk threshold exceeded.

## What v0.1 detects

- Python imports, including relative imports, common `src/` layouts, and package roots declared through common setuptools, Poetry, and Hatch `pyproject.toml` metadata
- JavaScript/TypeScript relative `import`, `require()`, and dynamic import paths
- Simple TypeScript `compilerOptions.paths` aliases from the nearest `tsconfig.json`, including exact mappings and single-wildcard patterns
- Transitive dependent files up to a configurable depth
- Test files reached through the dependency graph
- Filename/module similarity for extra test suggestions
- Build/dependency configuration changes
- Possible public API/integration surface changes
- Security-sensitive filenames
- Package export-surface changes
- Documentation that may need review

## Example report

```markdown
# ChangeRipple report

**Risk score:** 49/100

## Changed files
- `src/payments/api.py`

## Likely affected files
- `src/web/routes.py` — dependency distance 1
- `tests/test_payments_api.py` — dependency distance 1

## Risk signals
- **MEDIUM · public-surface** — Possible public API or integration surface changed.
```

## GitHub Actions

The repository includes ready-to-run CI and pull-request impact workflows under `.github/workflows/`.

## Design principles

1. **Local first** — source stays on the machine running the scan.
2. **Explainable** — every result comes from visible static relationships/heuristics.
3. **Fast enough for PRs** — no database, model download, daemon, or cloud account.
4. **Conservative** — “likely affected” is guidance, not a claim of runtime certainty.
5. **Friendly to OSS** — standard library runtime, small codebase, contribution-ready docs.

## Current limitations

- Static imports only; runtime reflection/plugin loading can escape the graph.
- TypeScript `tsconfig` `extends`, project references, and alias patterns with more than one `*` are not followed yet.
- Python namespace packages and unusual import hooks may be incomplete.
- Test recommendation is heuristic; it never claims full test coverage.
- Deleted files are listed by Git but cannot be parsed from the working tree.

See [ROADMAP.md](ROADMAP.md) for planned improvements.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
ruff check src tests
```

## Contributing

Contributions and real-world false-positive reports are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

ChangeRipple only reads repository files and Git metadata. See [SECURITY.md](SECURITY.md) for reporting security issues.

## License

MIT — see [LICENSE](LICENSE).
