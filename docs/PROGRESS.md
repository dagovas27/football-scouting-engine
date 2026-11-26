# Progress log

## 2026-11-18 — Phase 0 — Data inspection and scope definition
**Branch:** `docs/phase0-data-inspection` · **PR:** [#1](https://github.com/dagovas27/football-scouting-engine/pull/1) (merged)
**Done:**
- Read-only inspection of `~/Documents/data-sc/` (Wyscout, Transfermarkt, StatsBomb) answering the 10
  Phase 0 questions with numbers: `docs/data-inspection/phase0-report.md`.
- `docs/data-sources.md` (files, sizes, versions, licenses, citations) and `docs/scope.md` (hypotheses,
  module support, decisions).
- Inspection scripts kept outside the repository by request (not versioned).
**Decisions:** scope and D1–D9 approved on 2026-11-18 — [ADR-0001](decisions/ADR-0001-phase0-data-scope.md).
**Data/quality findings:**
- H1–H6 confirmed, H7 partially confirmed (WC 2018 needed only for the StatsBomb benchmark).
- Derived minutes match PlayeRank 99.0%; Brighton 2017/18 table passes sanity checks.
- Linking 90.8% (DOB + surname) / 96.6% (+ name tokens); Dale Stephens is the only unlinked Brighton player.
- Valuation coverage 99.9% / 97.0% / 90.6% at 2018 / 2020 / 2022.
- 1,152 Wyscout player names are double-escaped; `referees.json` is truncated.
- No salary or contract history (contract risk uses user inputs and pooled calibration).
**Blockers / open questions:** none (PR merged; manual updated locally with the confirmed scope).
**Next session starts with:** applying the approved scope to CLAUDE.md, then S1 infrastructure.
**Status:** done

## 2026-11-25 — S1 — Infrastructure: environment, PostgreSQL, raw load, minutes
**Branch:** `chore/s1-environment` → `chore/s1-postgres` → `feature/s1-raw-schema` → `feature/s1-minutes` (stacked) · **PR:** pending
**Done:**
- Python 3.11.5 + `uv` (ADR-0002, closes D9); `psycopg` 3.3.9, `pytest`, `ruff`.
- `docker-compose.yml` with `postgres:16.16` on `127.0.0.1:55432` (5432 and 5433 are taken by other
  local PostgreSQL servers); credentials only in the gitignored `.env`.
- Schemas `raw/core/analytics/app`, 6 Wyscout + 12 Transfermarkt raw tables, idempotent TRUNCATE + COPY
  loaders with `raw.load_log` (ADR-0003). Full load: 18 tables in 56 s; every row count equals Phase 0
  (e.g. 3,251,294 events, 656,301 valuations).
- `core.wy_*` with decoded names and `core.player_match_minutes` (53,791 rows, same as Phase 0).
- S1 acceptance: `sql/queries/brighton_minutes_2017_18.sql` returns the Phase 0 Brighton table exactly
  (24 players, 38 matches, Dunk and Ryan 3,420). 20/20 tests pass (14 unit + 6 database).
**Decisions:** ADR-0002 (Python/uv), ADR-0003 (raw layer and loading).
**Data/quality findings:**
- Derived vs PlayeRank minutes: 46,395 / 46,880 exact = 98.97% (Phase 0 reported it rounded as 99.0%),
  46,627 within 5 min.
**Blockers / open questions:**
- Re-running the Wyscout load (idempotency check) crashed PostgreSQL with an fsync I/O error: the Mac
  disk has 2.1 GB free (99% used). The transaction rolled back and the database recovered intact, but
  the idempotency check is not yet verified. Needs free disk space and a lighter reload (WAL).
- Schedule: S1 closes ~1 week late.
**Next session starts with:** free disk space, re-run `fse load all` twice to verify idempotency, then
push the four branches and open PRs.
**Status:** at risk
