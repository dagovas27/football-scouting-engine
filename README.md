# football-scouting-engine

Scouting, squad-analysis and player-valuation platform for budget-constrained football clubs, demonstrated
with a point-in-time backtest (decisions taken with data up to 2018-06-30, checked against 2018–2022).

Scope and data findings: [`docs/scope.md`](docs/scope.md) ·
[`docs/data-inspection/phase0-report.md`](docs/data-inspection/phase0-report.md) ·
decisions in [`docs/decisions/`](docs/decisions/).

## Local setup

Requirements: [uv](https://docs.astral.sh/uv/), Docker Desktop, and the source data in
`~/Documents/data-sc/` (not distributed with this repository; see [`docs/data-sources.md`](docs/data-sources.md)).

```bash
cp .env.example .env          # then set your own POSTGRES_PASSWORD
uv sync                       # Python 3.11 environment from uv.lock
docker compose up -d --wait   # PostgreSQL 16 on 127.0.0.1:${FSE_DB_PORT}
uv run --env-file .env fse db init       # create schemas and tables (idempotent)
uv run --env-file .env fse load all      # load Wyscout + Transfermarkt into raw (idempotent)
uv run --env-file .env fse build core    # rebuild the core layer
uv run --env-file .env pytest            # unit tests + database acceptance tests
```

Example query: [`sql/queries/brighton_minutes_2017_18.sql`](sql/queries/brighton_minutes_2017_18.sql).

## Data attribution

- Pappalardo, L., Cintia, P., Rossi, A., Massucco, E., Ferragina, P., Pedreschi, D., Giannotti, F. (2019).
  *A public data set of spatio-temporal match events in soccer competitions.* Scientific Data, 6, 236.
- Pappalardo, L., Cintia, P., Ferragina, P., Massucco, E., Pedreschi, D., Giannotti, F. (2019).
  *PlayeRank: data-driven performance evaluation and player ranking in soccer via a machine learning
  approach.* ACM Transactions on Intelligent Systems and Technology, 10(5).
- Transfermarkt data via Kaggle "Football Data from Transfermarkt".
- StatsBomb Open Data: any published analysis states "StatsBomb" as data source and shows its logo.
