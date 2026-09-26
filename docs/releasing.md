# Releasing ChangeRipple

This checklist keeps the package version, runtime version, changelog, built artifact, and GitHub release aligned.

## Before tagging

1. Start from an up-to-date `main` branch with all required CI checks passing.
2. Choose the next semantic version (for the current alpha line, `0.1.x`).
3. Update `project.version` in `pyproject.toml` and `__version__` in `src/changeripple/__init__.py` to the same value.
4. Move relevant entries from `CHANGELOG.md`'s **Unreleased** section into a dated release section.
5. Run the contributor checks:

   ```bash
   python -m pip install -e ".[dev]"
   ruff check src tests --select E9,F63,F7,F82
   pytest
   ```

6. Build and test the wheel in a clean environment:

   ```bash
   rm -rf dist .venv-release-smoke
   python -m pip wheel . --no-deps --wheel-dir dist
   python -m venv .venv-release-smoke
   .venv-release-smoke/bin/python -m pip install --no-deps dist/changeripple-*.whl
   .venv-release-smoke/bin/changeripple --version
   ```

   On Windows, use `.venv-release-smoke\Scripts\python.exe` and `.venv-release-smoke\Scripts\changeripple.exe`.

7. Confirm the reported CLI version exactly matches the intended release.
8. Open a focused release PR and wait for CI to pass before merging.

## Tag and GitHub release

After the release PR is merged:

1. Tag the merge commit as `vX.Y.Z`.
2. Push the tag.
3. Create a GitHub release from that tag.
4. Use the matching changelog section as the release notes; do not claim adoption or compatibility that has not been verified.
5. Re-run the installed CLI smoke check from the released artifact if one is published.

## After release

- Confirm the GitHub release points at the intended commit and tag.
- Keep new work under **Unreleased** in `CHANGELOG.md`.
- For security fixes, follow `SECURITY.md` and avoid publishing exploit details before a fix is available.
