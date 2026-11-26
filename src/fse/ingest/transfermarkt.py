"""Load the 12 Transfermarkt CSVs (Kaggle, Version 679) into raw.tm_* tables.

The CSV bytes are streamed to PostgreSQL unchanged with COPY (FORMAT csv, HEADER MATCH), so the
server rejects any file whose header does not match the table definition.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import psycopg
from psycopg import sql

from fse.db import log_load

CSV_FILES = (
    "appearances",
    "club_games",
    "clubs",
    "competitions",
    "countries",
    "game_events",
    "game_lineups",
    "games",
    "national_teams",
    "player_valuations",
    "players",
    "transfers",
)

CHUNK = 1 << 20  # 1 MiB


def table_for(stem: str) -> str:
    return f"tm_{stem}"


def table_columns(conn: psycopg.Connection, table: str) -> list[str]:
    rows = conn.execute(
        "SELECT column_name FROM information_schema.columns"
        " WHERE table_schema = 'raw' AND table_name = %s ORDER BY ordinal_position",
        (table,),
    ).fetchall()
    if not rows:
        raise RuntimeError(f"raw.{table} does not exist: run `fse db init` first")
    return [r[0] for r in rows]


def load_csv(conn: psycopg.Connection, path: Path) -> int:
    table = table_for(path.stem)
    cols = table_columns(conn, table)
    copy_sql = sql.SQL("COPY {} ({}) FROM STDIN WITH (FORMAT csv, HEADER MATCH)").format(
        sql.Identifier("raw", table), sql.SQL(", ").join(map(sql.Identifier, cols))
    )
    with conn.transaction():
        conn.execute(sql.SQL("TRUNCATE {}").format(sql.Identifier("raw", table)))
        with conn.cursor() as cur:
            with cur.copy(copy_sql) as copy, path.open("rb") as fh:
                while chunk := fh.read(CHUNK):
                    copy.write(chunk)
            rows = cur.rowcount
        log_load(conn, f"raw.{table}", path, rows)
    return rows


def load_transfermarkt(
    conn: psycopg.Connection, root: Path, log: Callable[[str], None] = print
) -> dict:
    counts = {}
    for stem in CSV_FILES:
        n = load_csv(conn, root / "transfermarkt" / f"{stem}.csv")
        counts[f"raw.{table_for(stem)}"] = n
        log(f"raw.{table_for(stem)}: {n:,} rows")
    return counts
