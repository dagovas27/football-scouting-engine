# ADR-0003 — Raw layer design and idempotent loading

**Status:** Accepted · **Date:** 2026-11-25

## Context

S1 must load Wyscout (JSON, ~0.9 GB) and Transfermarkt (12 CSVs, ~0.9 GB) into PostgreSQL so that later
layers can be rebuilt from the database. Phase 0 showed the sources are clean enough to parse (0 malformed
CSV rows) but have quirks: double-escaped Wyscout names, mixed `null` markers, snapshot columns.

## Decision

- **`raw` is a faithful copy.** No cleaning, renaming of values or deduplication; quirks are fixed in `core`.
  - Transfermarkt: one table per CSV (`raw.tm_<file>`), every column `TEXT`, column order identical to the
    header. Loaded with `COPY … (FORMAT csv, HEADER MATCH)`, so the server rejects a changed header.
  - Wyscout: one table per entity (`raw.wy_*`); top-level fields typed, nested structures (`teamsData`,
    `positions`, `tags`, areas, role) stored as `jsonb`; names stored exactly as parsed.
  - No primary keys in `raw`: uniqueness is enforced when building `core`.
  - Not loaded: `coaches.json`, `referees.json` (D8), StatsBomb (optional, S3).
- **Idempotent loads.** Each table is replaced inside one transaction (`TRUNCATE` + `COPY`); a failed load
  leaves the previous content intact. Every load appends a row to `raw.load_log` (file, size, mtime, rows).
- **Client-side streaming.** Files are read by the Python loader and streamed over the connection; the data
  folder is never mounted into the container and never modified.

## Alternatives considered

- Typed Transfermarkt columns in `raw`: couples the faithful layer to cleaning rules (e.g. fees as
  `'0.000'`, dates with time); rejected.
- One `jsonb` document per Wyscout record: simpler loader but ~2× storage for 3.25 M events and every
  query needs JSON extraction; rejected for events.
- Incremental/upsert loads: the sources are static snapshots, so full replacement is simpler and safe.

## Consequences

- `core` must cast Transfermarkt text columns and decode Wyscout names.
- Re-running `fse load all` always yields the same row counts; changes in a source show up in `load_log`.
