# fitter

Garmin FIT → run analytics (TRIMP, HR zones, ACWR, training suggestions).

## Commands

```sh
make report             # main entrypoint (run to check behaviour)
make check              # lint + typecheck + test (run to validate changes)
make format             # uv run ruff format (run after making changes)
make import             # cp FITs from Garmin mount to data/ (only run by human)
```

## Dev setup

- Python 3.12, managed via `uv` (lockfile: `uv.lock`)
- `uv sync` to install deps (including `dev` group for mypy/pytest/ruff)

## Dev workflow

- use red-green-refactor
- use type-driven design when reasonable
- repo is mounted into sandbox with limited file handles (see ulimit -n), if you run into issue with this use /tmp or /home/agent which do not suffer this limitation. One pattern you can use is creating a git worktree in /tmp or /home/agent and fast-forward merge your work onto the main branch when done

## Key facts

- `data/` is gitignored — FIT files are not in the repo. Tests that decode `.fit` files (e.g. `data/2026-07-28-12-53-43-Hike.fit`) require them on disk or will fail.
- `pytest` config sets `pythonpath = ["."]` so all top-level modules import directly.
- `mypy` runs in `--strict` mode with `ignore_missing_imports = true` (needed for `garmin_fit_sdk`).
- `ruff` uses `line-length = 100`, `target-version = "py312"`, rules `E,F,I,W,UP`.
- No README or CI.
