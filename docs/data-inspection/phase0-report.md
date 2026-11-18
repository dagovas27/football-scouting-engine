# Phase 0 — Data inspection report

**Date:** 2026-11-18 · **Branch:** `docs/phase0-data-inspection` · **Data root:** `~/Documents/data-sc/` (read-only)

All numbers below come from throwaway Python scripts (standard library only, Python 3.12.0) that read the
data in place. The scripts are deliberately **not versioned** (they live outside the repository); each
section names the script and the computation behind every number so it can be reproduced.

| Script | Answers |
|---|---|
| `q09_sha.py` | Q9 checksums |
| `q02_wy_struct.py`, `q02b_wy_quality.py`, `q02c_wy_events.py` | Q2 |
| `q03_minutes.py` | Q3 |
| `q04_tm_profile.py`, `q04b_tm_leak.py` | Q4 |
| `q05_link.py`, `q05b_unlinked.py` | Q5 |
| `q06_coverage.py` | Q6, Q7 (hedonic sample), Q8 |
| `q07_q09_q10.py` | Q7 (transfers), Q9 (pairing), Q10 |

---

## Q1. Inventory

Totals (`du -sh`): `wyscout/` 928 MB, `transfermarkt/` 872 MB, `statsbomb/` 298 MB. Full per-file list with
sizes is in [`docs/data-sources.md`](../data-sources.md).

| Folder | Files | Format | Expected? |
|---|---|---|---|
| `wyscout/` | `competitions`, `teams`, `players`, `coaches`, `referees`, `playerank` (.json); `matches/matches_*.json` ×7; `events/events_*.json` ×7 | JSON arrays | Expected set present. **Extra:** `coaches.json`, `referees.json`, `playerank.json`. |
| `transfermarkt/` | 12 CSVs: appearances, club_games, clubs, competitions, countries, game_events, game_lineups, games, national_teams, player_valuations, players, transfers | CSV, UTF-8, header row | Exactly 12 as expected. |
| `statsbomb/` | `LICENSE.pdf`, `README.md`, `MANIFEST.json`, `fetch_statsbomb.py`, `data/competitions.json`, `data/matches/{43/3,11/1}.json`, `data/events/*.json` ×100, `data/lineups/*.json` ×100 | JSON | As expected. |

**Anomalies**
- `wyscout/referees.json` (196,709 bytes) is **truncated**: `json.load` fails at char 196,709 (end of file),
  the file ends mid-object. Not needed by any module.
- `.DS_Store` at the data root (macOS metadata, harmless).
- All Transfermarkt CSVs parse with 0 malformed rows (`csv.reader`, row length == header length).

## Q2. Wyscout structure

| File | Records | Notes |
|---|---|---|
| `competitions.json` | 7 | 5 club leagues (524 ITA, 364 ENG, 795 ESP, 412 FRA, 426 GER) + 102 Euro, 28 World Cup |
| `teams.json` | 142 | 98 club, 44 national; 8 names contain double-escaped unicode |
| `players.json` | 3,603 | unique `wyId`; roles GK 426 / DF 1,200 / MD 1,257 / FW 720 |
| `coaches.json` | 208 | not needed |
| `playerank.json` | 46,897 | per player-match: `minutesPlayed`, `playerankScore`, `roleCluster`, `goalScored`; **no goalkeepers** (MD 18,948 / DF 16,983 / FW 10,966) |

| Competition | Matches | Season id | Dates (UTC) | Durations | Events | Shots |
|---|---|---|---|---|---|---|
| England | 380 | 181150 | 2017-08-11 … 2018-05-13 | all Regular | 643,150 | 8,451 |
| France | 380 | 181189 | 2017-08-04 … 2018-05-19 | all Regular | 632,807 | 8,327 |
| Germany | 306 | 181137 | 2017-08-18 … 2018-05-12 | all Regular | 519,407 | 6,898 |
| Italy | 380 | 181248 | 2017-08-19 … 2018-05-20 | all Regular | 647,372 | 8,806 |
| Spain | 380 | 181144 | 2017-08-18 … 2018-05-20 | all Regular | 628,659 | 7,979 |
| Euro 2016 | 51 | 9291 | 2016-06-10 … 2016-07-10 | 46 R / 2 ET / 3 P | 78,140 | 1,198 |
| World Cup 2018 | 64 | 10078 | 2018-06-14 … 2018-07-15 | 59 R / 1 ET / 4 P | 101,759 | 1,419 |

Top-5 club leagues: 1,826 matches, 3,071,395 events, 40,461 shots.

**Record layouts**
- Match: `wyId, competitionId, seasonId, dateutc, date, duration, gameweek, label, referees, roundId,
  status, venue, winner, teamsData`.
- `teamsData[teamId]`: `side, score, scoreHT, scoreET, scoreP, coachId, hasFormation, formation`.
  `formation = {lineup[11], bench[], substitutions[]}`; each lineup/bench entry has `playerId, goals,
  ownGoals, yellowCards, redCards` where **cards are the minute of the card as a string** (`"0"` = none).
  Substitutions: `{playerIn, playerOut, minute}`. `hasFormation == 1` and lineup size 11 for all 3,882
  team-matches.
- Event: one key set across all 3.25 M events: `id, eventId, eventName, subEventId, subEventName,
  matchId, teamId, playerId, matchPeriod, eventSec, positions, tags`. `positions` has 2 points (1 point in
  741 events); `x` range 0–100 (minimum −1 in Italy). `tags` = list of `{id}`. `matchPeriod` ∈
  {1H, 2H} in leagues; {1H, 2H, E1, E2, P} in tournaments.
- Event types (all files): Pass 1,665,508; Duel 879,083; Others on the ball 257,240; Free Kick 193,273;
  Interruption 130,097; Foul 51,049; Shot 43,078; Save attempt 17,619; Offside 8,182; GK leaving line 6,165.

**Data quality**
- Birth date present for **3,603 / 3,603 (100%)** players.
- **Name encoding:** 1,152 players (32%) have names that still contain literal `\uXXXX` sequences *after*
  JSON decoding (double-escaped), e.g. `Konaté`, `Guðmunds­son` (includes a soft hyphen
  U+00AD). After decoding, 0 names contain raw non-ASCII, i.e. every accented name is affected. A second
  decode pass is required in the ETL.
- 4 duplicate (`birthDate`, `lastName`) pairs inside Wyscout (twins such as the Bender brothers).
- Players referenced in match lineups/bench but missing from `players.json`: ENG 4, FRA 3, GER 2, ITA 3,
  ESP 3.
- `currentTeamId` is a later snapshot: for 173 of the 1,628 players with > 900 min it differs from the
  club derived from 2017/18 match participation; 124 players played for > 1 club in the season.

## Q3. Minutes played (H4)

Method (`q03_minutes.py`): match length L = 90 (Regular) or 120 (ET/Penalties). Starter: start 0;
substitute: start = `minute` of the substitution in. End = `minute` of the substitution out, else L; a red
card (`redCards` minute > 0 in `formation`) cuts the end. All minutes clamped to L.

**Validation against `playerank.minutesPlayed`** (46,880 player-matches where both exist): exact match
**99.0%**, |diff| ≤ 5 min 99.5%, mean |diff| 0.19 min. Red cards: the `formation.redCards` field gives
331 cards in the 5 leagues vs 332 events tagged 1701/1703 (red / second yellow) in the event files, so
event files are not needed for minutes.

Result: 2,570 players with ≥ 1 league appearance; max season minutes 3,420 (= 38 × 90); 0 players >
3,600; **1,628 players > 900 min** (ENG 326, FRA 330, GER 291, ITA 330, ESP 351).

**Brighton & Hove Albion (wyId 1651), 2017/18: 38 matches.**

| Player | Pos | Minutes | Apps | Starts | PlayeRank min |
|---|---|---:|---:|---:|---:|
| M. Ryan | GK | 3,420 | 38 | 38 | — (GK not in PlayeRank) |
| L. Dunk | DF | 3,420 | 38 | 38 | 3,420 |
| S. Duffy | DF | 3,294 | 37 | 37 | 3,294 |
| D. Stephens | MD | 3,240 | 36 | 36 | 3,240 |
| D. Pröpper | MD | 3,120 | 35 | 35 | 3,136 |
| P. Groß | MD | 2,947 | 38 | 35 | 2,936 |
| A. Knockaert | MD | 2,424 | 33 | 27 | 2,411 |
| G. Bong | DF | 2,238 | 25 | 25 | 2,238 |
| G. Murray | FW | 2,201 | 35 | 25 | 2,178 |
| Bruno Saltor | DF | 2,017 | 25 | 23 | 2,017 |
| J. Izquierdo | FW | 1,988 | 32 | 23 | 1,959 |
| S. March | MD | 1,841 | 36 | 18 | 1,817 |
| E. Schelotto | DF | 1,317 | 20 | 15 | 1,291 |
| M. Suttner | DF | 1,178 | 14 | 13 | 1,170 |
| T. Hemed | FW | 845 | 16 | 9 | 841 |
| B. Kayal | MD | 740 | 19 | 8 | 687 |
| I. Brown | FW | 307 | 13 | 4 | 281 |
| L. Ulloa | FW | 260 | 10 | 2 | 260 |
| J. Locadia | FW | 224 | 6 | 3 | 216 |
| C. Goldson | DF | 199 | 3 | 2 | 180 |
| J. Murphy | MD | 165 | 4 | 1 | 156 |
| L. Rosenior | DF | 162 | 3 | 1 | 162 |
| S. Baldock | FW | 30 | 2 | 0 | 24 |
| U. Hünemeier | DF | 17 | 1 | 0 | 17 |

Sanity checks pass: 38 matches; nobody above 3,420; the first-choice goalkeeper (Ryan) is at the maximum.
Stoppage time is not counted (minutes are capped at 90), so these are approximate minutes.

## Q4. Transfermarkt structure

| CSV | Rows | Cols | Date range | Key nulls |
|---|---:|---:|---|---|
| appearances | 1,894,350 | 13 | 2012-07-03 … 2026-06-28 | none in keys |
| club_games | 177,916 | 11 | — | positions 28.5% |
| clubs | 796 | 17 | — | `total_market_value` 100% null; `coach_name` 49.4% |
| competitions | 65 | 11 | — | — |
| countries | 124 | 8 | — | — |
| game_events | 1,274,469 | 11 | 2006-06-09 … 2026-07-06 | `player_in_id` 50.5%, `player_assist_id` 85.2% |
| game_lineups | 3,179,016 | 10 | 2013-07-02 … 2026-07-06 | — |
| games | 88,958 | 23 | 2006-06-09 … 2026-07-06 | positions 28.5%, attendance 12.1% |
| national_teams | 124 | 17 | — | `coach_name` 100% |
| player_valuations | 656,301 | 6 | 2000-01-20 … 2026-06-12 | `player_club_domestic_competition_id` 14.2% |
| players | 50,149 | 26 | DOB 1968 … 2011 | DOB 49 (0.1%), `market_value_in_eur` 17.2%, `contract_expiration_date` 37.0% |
| transfers | 175,165 | 10 | 1993-07-01 … 2030-06-30 | `transfer_fee` 35.1%, `market_value_in_eur` 38.9% |

Columns per CSV are listed in `docs/data-sources.md`. TM has all 2017/18 top-5 games (GB1 380, ES1 380,
IT1 380, L1 306, FR1 380).

**Current-snapshot columns that leak the future (never use for the 2018 decision)**
- `players.csv`: `current_club_id`, `current_club_name`, `current_club_domestic_competition_id`,
  `market_value_in_eur`, `highest_market_value_in_eur`, `contract_expiration_date`, `agent_name`,
  `last_season`, `international_caps`, `international_goals`, `current_national_team_id`.
- `appearances.csv`: `player_current_club_id` (differs from the club at the time in 68.7% of 128,379
  appearances in 2017/18).
- `clubs.csv` and `national_teams.csv`: all squad aggregates (`squad_size`, `average_age`,
  `foreigners_*`, `national_team_players`, `net_transfer_record`, `coach_name`, `fifa_ranking`, `last_season`).
- `transfers.csv`: 475 rows dated after 2026-11-18 (385 on 2026-12-31), i.e. scheduled loan returns;
  filter every use by `transfer_date ≤ DECISION_DATE`.
- `player_valuations.current_club_*` looks **historical** despite its name: 18,821 of 41,528 players
  (45.3%) have > 1 distinct club across their valuations. To be confirmed in S2 against `transfers`.

**Salary / contract history (H3):** no salary or wage column in any CSV. The only contract field is
`players.contract_expiration_date`, a current snapshot (37.0% null). No contract history. `transfers` has
`transfer_fee` (0 = 96,085 rows, > 0 = 17,554, null = 61,526) and no loan flag.

## Q5. Entity resolution Wyscout ↔ Transfermarkt (H5)

Method (`q05_link.py`): candidates = TM players with the same date of birth. Names normalised with NFKD
accent stripping, special letters (ß→ss, ø→o, ł→l, đ→d, æ→ae, þ→th, ð→d, ı→i, soft hyphen removed),
lower-case, tokenised; particles (de, da, van, von, filho, junior…) ignored. Tiers, each accepted only if
it yields exactly one candidate:
1. `strict`: normalised last name equal;
2. `surname_token`: any surname token shared (these two tiers are the spec heuristic);
3. `any_name_token`: any token of first/last/short name shared with TM `name` (mononyms such as
   Fernandinho, Marquinhos, Roberto Firmino).

Population: 1,628 players with > 900 min. No TM id was linked to two Wyscout players.

| League | n | DOB + surname | + any name token |
|---|---:|---:|---:|
| England | 326 | 93.6% | 96.6% |
| France | 330 | 91.5% | 97.0% |
| Germany | 291 | 95.2% | 98.3% |
| Italy | 330 | 88.2% | 96.1% |
| Spain | 351 | 86.3% | 95.2% |
| **All** | **1,628** | **1,478 (90.8%)** | **1,572 (96.6%)** |

The 56 unlinked players (`q05b_unlinked.py`): 29 exist in TM with the same surname but a **different
DOB** (e.g. D. Gosling 1990-02-02 vs 1990-02-01; D. Stephens 1989-12-12 vs 1989-06-12; D. Gayle 1990 vs
1989); 10 ambiguous (same DOB and surname: twins such as Lars/Sven Bender, Jacob/Josh Murphy); 16 surname
not found (multi-part names); 1 surname found but DOB far. A fallback "exact surname + DOB within ±1 year +
same 2017/18 club in TM appearances" would recover most of the 29 + 10 → est. ~98–99%.

**Brighton:** 14 players > 900 min, 13 linked. **Not linked: Dale Stephens** (Wyscout DOB 1989-12-12, TM
1989-06-12). Among all 24 Brighton players, Stephens is the only one that fails.

## Q6. Backtest coverage (H6)

Linked players > 900 min (n = 1,572). As-of value = last valuation on or before the date, accepted if
within the previous 365 days (`q06_coverage.py`).

| Date | Covered | ENG | FRA | GER | ITA | ESP | Stale (> 365 d) | Never valued |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2018-06-30 | **99.9%** (1,570) | 100% | 99.4% | 100% | 100% | 100% | 1 | 1 |
| 2020-06-30 | **97.0%** (1,525) | 98.4% | 94.1% | 98.6% | 96.2% | 97.9% | 46 | 1 |
| 2022-06-30 | **90.6%** (1,425) | 91.4% | 88.1% | 93.0% | 89.3% | 91.6% | 146 | 1 |

Valued at all three dates: 1,424 (90.6%).

How missing values cluster (2022, n = 147): median age at the date 37.5 vs 31.2 for all linked players;
their last valuation is in a top-5 league (FR1 35, IT1 31, ES1 27, GB1 22, L1 18), and `last_season`
is 2017–2020 for 142 of them → mostly **retirements or moves out of TM-tracked leagues** (the dataset
cannot tell them apart), not lower-league drops. France is the weakest league (88.1%). By role: DF 64,
MD 51, FW 20, GK 12.

## Q7. Fair-value sample

- Hedonic rows: linked players > 900 min with a valuation as of 2018-06-30 = **1,570** (one season,
  cross-sectional). Lowering the minutes threshold increases this (2,570 players have ≥ 1 appearance).
- Real transfers in summer 2018 (`transfer_date` 2018-06-01 … 2018-09-02): 7,167 total, **775 with fee > 0**
  (713 of them with `market_value_in_eur`); **148** with fee > 0 for linked > 900-min players (median fee
  €9.55 M, max €180 M).

## Q8. Contract-risk calibration

Valuation snapshots before 2018-07-01 per linked player: **median 18, p10 8.3, p90 27** (min 0, max 39).
Share with ≥ 10 snapshots 86.7%, ≥ 20 snapshots 43.1%, < 5 snapshots 1.3%. Gap between snapshots: median
158 days (p10 72, p90 232); median first valuation 2010-07-16.
Pooled universe: 257,563 snapshots before 2018-07-01 from 24,211 TM players.

Conclusion: ~17 log-returns per player is enough for a per-player volatility with shrinkage, but **not** for
per-player drift or jump parameters. Drift and jumps must be pooled (age bucket × position), volatility can
be per player shrunk towards the pool.

## Q9. StatsBomb (H2)

- Checksums: **205 / 205** files match `MANIFEST.json` (sha256 and size); 0 missing; total 312,132,676 bytes.
  Files on disk not in the manifest: only `MANIFEST.json` and `fetch_statsbomb.py`.
- Pairing with Wyscout by date (±1 day) + normalised team names: La Liga 2017/18 **36 / 36**; World Cup
  2018 **61 / 64**. The 3 failures are all South Korea (StatsBomb "South Korea" vs Wyscout "Korea Republic");
  one alias gives **100 / 100**.

## Q10. Euro 2016 / World Cup 2018 in Wyscout (H7)

- No core module needs national-team matches: minutes, metrics, scouting, squad analysis, valuation and the
  backtest all run on the five club leagues.
- World Cup 2018 Wyscout events **are** needed for the optional StatsBomb xG benchmark (64 of the 100 paired
  matches).
- 14 of the 64 World Cup matches are played after `DECISION_DATE` (50 on/before 2018-06-30), so they must
  never feed features or training for the 2018 decision.
- Euro 2016 (51 matches, 1,198 shots) could add xG training shots, but different context (national teams);
  not needed.
