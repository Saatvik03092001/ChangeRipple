# Architecture

ChangeRipple is deliberately small:

1. `git.py` discovers changed paths.
2. `parsers.py` extracts local import strings without executing project code.
3. `graph.py` resolves supported local imports into a reverse dependency graph.
4. `analysis.py` walks dependents, suggests tests/docs, and emits explainable risk signals.
5. `render.py` provides stable human/machine outputs.
6. `cli.py` handles filesystem/Git I/O and CI exit codes.

No source file is imported or executed by ChangeRipple during analysis.
