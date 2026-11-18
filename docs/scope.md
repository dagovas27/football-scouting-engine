# Scope — what the data supports

**Status:** approved by the product owner on 2026-11-18, including decisions D1–D9 as recommended
([ADR-0001](decisions/ADR-0001-phase0-data-scope.md)) · **Date:** 2026-11-18 · **Evidence:**
[`data-inspection/phase0-report.md`](data-inspection/phase0-report.md) (section numbers Qn below).

## 1. Hypotheses

| # | Hypothesis | Verdict | Evidence |
|---|---|---|---|
| H1 | Core runs on Wyscout + Transfermarkt alone | **Confirmed** | All modules and the backtest are covered by these two sources (table below); StatsBomb is only used for the benchmark. |
| H2 | StatsBomb only for external xG validation; optional | **Confirmed** | 205/205 sha256 OK; 100/100 matches pair with Wyscout (97 automatic + 3 via one alias "South Korea" ↔ "Korea Republic") (Q9). |
| H3 | No salaries or historical contracts | **Confirmed** | No salary/wage column in any CSV; `contract_expiration_date` is a current snapshot, 37.0% null; no contract history (Q4). |
| H4 | Minutes can be derived from `teamsData` | **Confirmed** | 99.0% exact match vs `playerank.minutesPlayed` on 46,880 player-matches, mean abs. diff 0.19 min; Brighton 38 matches, max 3,420, GK Ryan at max (Q3). |
| H5 | ≥ 90% of > 900-min players link by DOB + name | **Confirmed (barely)** | DOB + surname: 1,478/1,628 = 90.8% overall but Spain 86.3%, Italy 88.2%. Adding a name-token tier: 96.6% (Q5). |
| H6 | Valuations cover 2018/2020/2022 | **Confirmed** | 99.9% / 97.0% / 90.6% of linked players have a value within 365 days; missing ones are mostly retirements (median age 37.5) (Q6). |
| H7 | WC 2018 / Euro 2016 not needed for the core | **Partially confirmed** | Not needed for any core module, but WC 2018 Wyscout events are required for the StatsBomb benchmark (64 of 100 pairs), and 14 WC matches fall after `DECISION_DATE` (Q10). |

## 2. Modules

| # | Module | Verdict | Evidence | Proposed adjustment | Roadmap impact |
|---|---|---|---|---|---|
| 1 | Data platform (PostgreSQL, ETL, Wyscout → SPADL, entity resolution) | **Supported** | All expected files present and parseable except `referees.json` (truncated, not needed). Events: single key set, 3.25 M rows. Linking 96.6% (Q1, Q2, Q5). | ETL must decode double-escaped names (1,152 players) and remove soft hyphens. Entity resolution adds a fallback tier (exact surname + DOB ± 1 year + 2017/18 club from TM `appearances`) for the 29 DOB discrepancies; twins resolved by club. Skip `referees.json`, `coaches.json`. | None. S2 target "≥ 90% linked" is already met; raise it to ≥ 97%. |
| 2 | Metrics (per-90, possession-adjusted, own xG, VAEP) | **Supported** | Minutes validated (Q3); 40,461 shots in the five leagues for xG; positions 0–100, periods 1H/2H (Q2). | Minutes capped at 90 per match (stoppage time not counted): document as approximate. Train xG on club-league shots only. | None. |
| 3 | Scouting (roles, similar players, shortlist) | **Supported, with a universe limit** | 1,628 players > 900 min across five leagues (Q3); age, position and value filters available (Q5, Q6). | Candidate pool is **only the five top leagues in 2017/18**: no Championship, Eredivisie, Portugal, etc. For a budget club, frame the shortlist as "undervalued players inside the top 5". | None in effort; affects the pitch narrative. |
| 4 | Squad analysis (renew/sell/loan/keep, team style) | **Partially supported** | Style metrics (PPDA, build-up, loss zones) computable from events (Q2). No contract expiry as of 2018: `contract_expiration_date` is a current snapshot (Q4). | Matrix built on age, minutes, performance and value trend; contract length as of 2018 becomes a **user input** (or is omitted). | S7: small; add a contract-years input. |
| 5 | Fair value (CatBoost hedonic + SHAP) | **Supported, small sample** | 1,570 rows at > 900 min with a 2018-06-30 value; 148 real fee transfers of linked players in summer 2018 for validation (Q7). | Lower the minutes threshold (e.g. ≥ 450) to enlarge the sample; group CV by club; external check on the 148 fees (and 775 fees overall). | None; S5 "done when" unchanged. |
| 6 | Contract risk (Merton jump-diffusion, VaR/CVaR) | **Partially supported** | No salaries/fees as contracts (H3). Per player: median 18 snapshots before 2018-07-01 (p10 8, p90 27), median gap 158 days; pooled 257,563 snapshots from 24,211 players (Q8). | Fee and salary are user inputs (hypothetical contracts). Drift and jumps calibrated **pooled by age bucket × position**; volatility per player with shrinkage to the pool; returns normalised by Δt. | S6 unchanged (still first to cut). |
| 7 | Delivery (Streamlit, n8n SMTP PDFs) | **Supported (not data-dependent)** | — | `directivos` is an application table we create; no source data needed. | None. |
| — | Backtest 2018 → 2022 | **Supported** | Coverage 99.9% / 97.0% / 90.6%; 90.6% valued on all three dates (Q6). | Report the 9.4% without a 2022 value separately (retired / left tracked leagues); compare against a league- and age-matched benchmark (COVID drop in 2020). | None. |
| — | StatsBomb xG benchmark (optional) | **Supported** | 100/100 pairs with one team-name alias (Q9). | Use as validation only; World Cup matches after 2018-06-30 used for benchmarking, never for training. | Remains cut #2. |

## 3. Point-in-time rules confirmed by the data

- Never use: Wyscout `currentTeamId`/`currentNationalTeamId`; TM `players.*current*`, `market_value_in_eur`,
  `highest_market_value_in_eur`, `contract_expiration_date`, `agent_name`, `last_season`, caps;
  `appearances.player_current_club_id`; all `clubs.csv`/`national_teams.csv` aggregates (Q4).
- Historical values only via as-of joins on `player_valuations` (last value ≤ date).
- `transfers` filtered by `transfer_date ≤ 2018-06-30` for features (475 rows are dated in the future).
- 2017/18 club derived from Wyscout match participation (173 of 1,628 players have a different
  `currentTeamId`; 124 played for two clubs).

## 4. Decisions for the product owner

| # | Decision | Recommendation |
|---|---|---|
| D1 | Entity-resolution method and target | Three name tiers + fallback "exact surname, DOB ± 1 year, same 2017/18 club in TM appearances"; target ≥ 97% for > 900 min; manual review list for the rest (Dale Stephens is the only Brighton case). ADR in S2. |
| D2 | Source of minutes played | Derive from `matches → teamsData` (validated 99.0%); keep `playerank.json` only as a test fixture; do not parse events for minutes. |
| D3 | Contract-risk calibration level | Pooled drift/jumps by age bucket × position, per-player volatility with shrinkage; fee and salary as user inputs. ADR in S6. |
| D4 | Fair-value sample | Minimum 450 minutes (instead of 900) to enlarge the cross-section; validate on the 2018 summer transfers with a fee. |
| D5 | Scouting universe | Accept "top-5 leagues 2017/18 only" and state it in the pitch; no extra data source in this window. |
| D6 | Squad-analysis contract input | Contract years remaining become a manual input on the dashboard; no contract data is inferred. |
| D7 | Euro 2016 / World Cup 2018 | Load raw (cheap) but exclude from every feature and model; WC 2018 used only by the StatsBomb benchmark. |
| D8 | `referees.json` truncated | Ignore it (no module needs referees); no re-download. |
| D9 | Python version | Local Python is 3.12.0, CLAUDE.md says 3.11: decide in the S1 environment ADR (recommend pinning 3.11 via `uv` to match the plan; verify socceraction/CatBoost wheels for arm64 before deciding). |
