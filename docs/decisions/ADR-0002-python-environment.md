# ADR-0002 — Python version and environment manager

**Status:** Accepted · **Date:** 2026-11-25 · **Closes:** decision D9 of [ADR-0001](ADR-0001-phase0-data-scope.md)

## Context

CLAUDE.md plans Python 3.11; the machine's default `python3` is 3.12.0, and a CPython 3.11.5 install is
also present. The project needs a reproducible environment on macOS arm64 that does not depend on
whichever interpreter is first on `PATH`.

## Decision

- **Python 3.11**, enforced by `requires-python = ">=3.11,<3.12"` and a `.python-version` file.
- **`uv`** manages the interpreter, the virtual environment (`.venv/`, not versioned) and dependencies;
  `uv.lock` is committed so every install resolves the same versions.
- Package layout `src/fse/` built with `uv_build`; one console entry point, `fse`.
- Runtime dependencies are added only when code uses them (S1: `psycopg[binary]` 3). Dev tools in the
  `dev` dependency group: `pytest`, `ruff`.
- Configuration comes from environment variables; `uv run --env-file .env …` passes the local `.env`
  (never committed) without adding a dotenv dependency.

## Alternatives considered

- **Python 3.12:** already the system default, but 3.11 is the plan's target and keeps the widest wheel
  coverage for the later stack (socceraction, CatBoost, SHAP); revisit if a dependency requires ≥ 3.12.
- **pip + venv / Poetry / conda:** no lock file by default (pip) or heavier tooling for a solo project.

## Consequences

- Every command runs through `uv run` (e.g. `uv run pytest`, `uv run fse …`).
- Moving to 3.12 later is a one-line change plus a lock refresh, recorded in a new ADR.
