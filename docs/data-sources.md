# Data sources

All data lives outside the repository in `~/Documents/data-sc/` and is **read-only**. Nothing from it is
committed. Sizes are in bytes as read on 2026-11-18. "Local copy date" is the file modification date on
disk, not an official release date.

## 1. Wyscout public dataset

- **Source:** Pappalardo et al. (2019), figshare collection, DOI
  [10.6084/m9.figshare.c.4415000](https://doi.org/10.6084/m9.figshare.c.4415000).
- **Version:** figshare collection as downloaded (no version tag). Event files carry an original mtime of
  2019-02-25; metadata files were unpacked locally on 2026-11-16.
- **License:** CC BY 4.0. Cite both papers below.
- **Content:** 2017/18 season of the Premier League, La Liga, Serie A, Bundesliga and Ligue 1, plus
  World Cup 2018 and Euro 2016.

| File | Bytes | Notes |
|---|---:|---|
| `competitions.json` | 1,209 | 7 competitions |
| `teams.json` | 27,404 | 142 teams |
| `players.json` | 1,737,347 | 3,603 players; names double-escaped (see report Q2) |
| `coaches.json` | 70,664 | 208 coaches (not used) |
| `referees.json` | 196,709 | **truncated, invalid JSON** (not used) |
| `playerank.json` | 6,241,757 | 46,897 player-match rows (validation of minutes) |
| `matches/matches_England.json` | 1,694,720 | 380 matches |
| `matches/matches_France.json` | 1,707,222 | 380 matches |
| `matches/matches_Germany.json` | 1,377,328 | 306 matches |
| `matches/matches_Italy.json` | 2,019,196 | 380 matches |
| `matches/matches_Spain.json` | 1,705,380 | 380 matches |
| `matches/matches_European_Championship.json` | 312,151 | 51 matches |
| `matches/matches_World_Cup.json` | 395,677 | 64 matches |
| `events/events_England.json` | 188,888,614 | 643,150 events |
| `events/events_France.json` | 186,374,196 | 632,807 events |
| `events/events_Germany.json` | 152,916,631 | 519,407 events |
| `events/events_Italy.json` | 190,544,685 | 647,372 events |
| `events/events_Spain.json` | 184,164,406 | 628,659 events |
| `events/events_European_Championship.json` | 22,954,338 | 78,140 events |
| `events/events_World_Cup.json` | 29,981,214 | 101,759 events |

**Citations**
- Pappalardo, L., Cintia, P., Rossi, A., Massucco, E., Ferragina, P., Pedreschi, D., Giannotti, F. (2019).
  *A public data set of spatio-temporal match events in soccer competitions.* Scientific Data, 6, 236.
- Pappalardo, L., Cintia, P., Ferragina, P., Massucco, E., Pedreschi, D., Giannotti, F. (2019).
  *PlayeRank: data-driven performance evaluation and player ranking in soccer via a machine learning
  approach.* ACM Transactions on Intelligent Systems and Technology, 10(5).

## 2. Transfermarkt (Kaggle)

- **Source:** Kaggle dataset "Football Data from Transfermarkt" (data scraped from transfermarkt.co.uk).
- **Version:** Kaggle Version 679. Local copy date 2026-09-05 (file mtime). Latest valuation in the data:
  2026-06-12.
- **License / terms:** scraped from Transfermarkt; acceptable for a demo; review Transfermarkt terms before
  any paid or commercial use.
- **Attribution:** "Transfermarkt data via Kaggle 'Football Data from Transfermarkt'".

| File | Bytes | Rows | Columns |
|---|---:|---:|---|
| `appearances.csv` | 198,398,405 | 1,894,350 | appearance_id, game_id, player_id, player_club_id, player_current_club_id, date, player_name, competition_id, yellow_cards, red_cards, goals, assists, minutes_played |
| `club_games.csv` | 14,748,080 | 177,916 | game_id, club_id, own_goals, own_position, own_manager_name, opponent_id, opponent_goals, opponent_position, opponent_manager_name, hosting, is_win |
| `clubs.csv` | 208,374 | 796 | club_id, club_code, name, domestic_competition_id, total_market_value, squad_size, average_age, foreigners_number, foreigners_percentage, national_team_players, stadium_name, stadium_seats, net_transfer_record, coach_name, last_season, filename, url |
| `competitions.csv` | 12,247 | 65 | competition_id, competition_code, name, sub_type, type, country_id, country_name, domestic_league_code, confederation, total_clubs, url |
| `countries.csv` | 15,058 | 124 | country_id, country_name, country_code, confederation, total_clubs, total_players, average_age, url |
| `game_events.csv` | 179,098,694 | 1,274,469 | game_event_id, date, game_id, minute, type, club_id, club_name, player_id, description, player_in_id, player_assist_id |
| `game_lineups.csv` | 415,978,884 | 3,179,016 | game_lineups_id, date, game_id, player_id, club_id, player_name, type, position, number, team_captain |
| `games.csv` | 28,965,132 | 88,958 | game_id, competition_id, season, round, date, home_club_id, away_club_id, home_club_goals, away_club_goals, home_club_position, away_club_position, home_club_manager_name, away_club_manager_name, stadium, attendance, referee, url, home_club_formation, away_club_formation, home_club_name, away_club_name, aggregate, competition_type |
| `national_teams.csv` | 32,980 | 124 | national_team_id, name, team_code, country_id, country_name, country_code, confederation, team_image_url, squad_size, average_age, foreigners_number, foreigners_percentage, total_market_value, coach_name, fifa_ranking, last_season, url |
| `player_valuations.csv` | 39,647,280 | 656,301 | player_id, date, market_value_in_eur, current_club_name, current_club_id, player_club_domestic_competition_id |
| `players.csv` | 19,624,138 | 50,149 | player_id, first_name, last_name, name, last_season, current_club_id, player_code, country_of_birth, city_of_birth, country_of_citizenship, date_of_birth, sub_position, position, foot, height_in_cm, contract_expiration_date, agent_name, image_url, international_caps, international_goals, current_national_team_id, url, current_club_domestic_competition_id, current_club_name, market_value_in_eur, highest_market_value_in_eur |
| `transfers.csv` | 18,112,063 | 175,165 | player_id, transfer_date, transfer_season, from_club_id, to_club_id, from_club_name, to_club_name, transfer_fee, market_value_in_eur, player_name |

## 3. StatsBomb Open Data (pinned subset)

- **Source:** <https://github.com/statsbomb/open-data>, commit `4b73468fc5b0f1950f9f66fada70ad3a4f9327cb`.
- **Downloaded:** 2026-11-18T15:10:33Z (from `MANIFEST.json`), with `fetch_statsbomb.py`.
- **Selection:** FIFA World Cup 2018 (competition 43, season 3, 64 matches) and La Liga 2017/18
  (competition 11, season 1, 36 matches).
- **Integrity:** 205 files, 312,132,676 bytes; all 205 sha256 hashes verified on 2026-11-18.
- **License / terms:** free for research; any published analysis must state "StatsBomb" as the data source
  and show the StatsBomb logo; review `LICENSE.pdf` before commercial use.

| Path | Files | Bytes (range) |
|---|---:|---|
| `LICENSE.pdf` | 1 | 165,130 |
| `README.md` | 1 | 1,753 |
| `MANIFEST.json` | 1 | 32,945 |
| `fetch_statsbomb.py` | 1 | 3,302 |
| `data/competitions.json` | 1 | 34,887 |
| `data/matches/43/3.json`, `data/matches/11/1.json` | 2 | 114,527 / 66,269 |
| `data/events/<match_id>.json` | 100 | 2,342,239 – 4,283,466 |
| `data/lineups/<match_id>.json` | 100 | 16,518 – 25,335 |
