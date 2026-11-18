# ADR-0001 — Data scope after Phase 0

**Status:** Accepted · **Date:** 2026-11-18

## Context

Phase 0 inspected the three local data sources (Wyscout public dataset, Transfermarkt via Kaggle,
StatsBomb Open Data subset) read-only and tested hypotheses H1–H7. Evidence and numbers are in
[`../data-inspection/phase0-report.md`](../data-inspection/phase0-report.md); module-level support is in
[`../scope.md`](../scope.md).

## Decision

The scope in `docs/scope.md` is approved, with decisions D1–D9 as recommended:

1. **D1 Entity resolution:** DOB + normalised surname, then name-token tier, then a fallback (exact surname,
   DOB ± 1 year, same 2017/18 club in Transfermarkt appearances); target ≥ 97% of players with > 900 min,
   with a manual review list for the rest. Detailed design gets its own ADR in S2.
2. **D2 Minutes:** derived from `matches → teamsData` (lineups, substitutions, red-card minutes);
   `playerank.json` used only as a validation fixture.
3. **D3 Contract risk:** fee and salary are user inputs; drift and jumps pooled by age bucket × position;
   per-player volatility shrunk towards the pool; returns normalised by Δt. Detailed ADR in S6.
4. **D4 Fair value:** minimum 450 league minutes for the hedonic sample; validation on summer-2018 transfers
   with a fee; cross-validation grouped by club.
5. **D5 Scouting universe:** top-5 leagues 2017/18 only, stated explicitly in the pitch.
6. **D6 Squad analysis:** remaining contract years are a manual input; no contract data is inferred.
7. **D7 Euro 2016 / World Cup 2018:** loaded raw but excluded from all features and models; World Cup 2018
   used only for the optional StatsBomb xG benchmark.
8. **D8 `referees.json`:** ignored (truncated, not needed).
9. **D9 Python version:** decided in the S1 environment ADR (proposal: Python 3.11 pinned with `uv`).

## Alternatives considered

- Strict DOB + surname linking only (90.8%): rejected, Spain 86.3% and Italy 88.2% fall below target.
- Parsing event files for minutes: unnecessary, `teamsData` already matches PlayeRank 99.0%.
- Per-player jump-diffusion calibration: rejected, median 18 valuation snapshots per player is too few.
- Adding a data source for lower leagues or contracts: out of the time window.

## Consequences

- Module 4 (squad analysis) and module 6 (contract risk) are partially supported and depend on user inputs.
- The S2 "done when" target rises from ≥ 90% to ≥ 97% linked players.
- ETL must decode double-escaped Wyscout names and apply the point-in-time rules in `scope.md` §3.
- The backtest reports players without a 2022 valuation (9.4%) separately.
