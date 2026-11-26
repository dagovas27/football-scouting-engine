"""Load the Wyscout public dataset (JSON) into raw.wy_* tables.

Each table is replaced in a single transaction (TRUNCATE + COPY), so a load can be re-run safely.
Event files are read one at a time to bound memory (~1 GB peak per file).
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Iterator, Sequence
from pathlib import Path
from typing import Any

import psycopg

from fse.db import log_load

LEAGUES = ("England", "France", "Germany", "Italy", "Spain")
TOURNAMENTS = ("European_Championship", "World_Cup")
COMPETITION_FILES = LEAGUES + TOURNAMENTS

Row = Sequence[Any]


def to_int(value: Any) -> int | None:
    """Wyscout mixes ints, None, '' and the string 'null' for missing ids."""
    if value is None or value == "" or value == "null":
        return None
    return int(value)


def to_json(value: Any) -> str | None:
    return None if value is None else json.dumps(value)


def competition_rows(records: Iterable[dict]) -> Iterator[Row]:
    for r in records:
        yield (r["wyId"], r["name"], r["format"], r["type"], to_json(r.get("area")))


def team_rows(records: Iterable[dict]) -> Iterator[Row]:
    for r in records:
        yield (
            r["wyId"], r["name"], r["officialName"], r["city"], r["type"], to_json(r.get("area")),
        )  # fmt: skip


def player_rows(records: Iterable[dict]) -> Iterator[Row]:
    for r in records:
        yield (
            r["wyId"],
            r["shortName"],
            r["firstName"],
            r["middleName"],
            r["lastName"],
            r["birthDate"] or None,
            to_int(r.get("height")),
            to_int(r.get("weight")),
            r.get("foot"),
            to_json(r.get("role")),
            to_json(r.get("birthArea")),
            to_json(r.get("passportArea")),
            to_int(r.get("currentTeamId")),
            to_int(r.get("currentNationalTeamId")),
        )


def match_rows(records: Iterable[dict], source: str) -> Iterator[Row]:
    for r in records:
        yield (
            r["wyId"],
            to_int(r.get("competitionId")),
            to_int(r.get("seasonId")),
            to_int(r.get("roundId")),
            to_int(r.get("gameweek")),
            r["dateutc"],
            r.get("date"),
            r.get("duration"),
            r.get("status"),
            r.get("label"),
            r.get("venue"),
            to_int(r.get("winner")),
            to_json(r.get("referees")),
            to_json(r.get("teamsData")),
            source,
        )


def event_rows(records: Iterable[dict], source: str) -> Iterator[Row]:
    for r in records:
        yield (
            r["id"],
            to_int(r.get("eventId")),
            r.get("eventName"),
            to_int(r.get("subEventId")),
            r.get("subEventName"),
            to_int(r.get("matchId")),
            to_int(r.get("teamId")),
            to_int(r.get("playerId")),
            r.get("matchPeriod"),
            r.get("eventSec"),
            to_json(r.get("positions")),
            to_json(r.get("tags")),
            source,
        )


def playerank_rows(records: Iterable[dict]) -> Iterator[Row]:
    for r in records:
        yield (
            r["matchId"], r["playerId"], r["minutesPlayed"], r["goalScored"],
            r["playerankScore"], r["roleCluster"],
        )  # fmt: skip


COLUMNS = {
    "raw.wy_competitions": "wy_id, name, format, type, area",
    "raw.wy_teams": "wy_id, name, official_name, city, type, area",
    "raw.wy_players": (
        "wy_id, short_name, first_name, middle_name, last_name, birth_date, height, weight, foot,"
        " role, birth_area, passport_area, current_team_id, current_national_team_id"
    ),
    "raw.wy_matches": (
        "wy_id, competition_id, season_id, round_id, gameweek, date_utc, date_local, duration,"
        " status, label, venue, winner, referees, teams_data, source_file"
    ),
    "raw.wy_events": (
        "id, event_id, event_name, sub_event_id, sub_event_name, match_id, team_id, player_id,"
        " match_period, event_sec, positions, tags, source_file"
    ),
    "raw.wy_playerank": (
        "match_id, player_id, minutes_played, goal_scored, playerank_score, role_cluster"
    ),
}


def read_json(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _copy(conn: psycopg.Connection, table: str, rows: Iterable[Row]) -> int:
    n = 0
    with conn.cursor() as cur, cur.copy(f"COPY {table} ({COLUMNS[table]}) FROM STDIN") as copy:
        for row in rows:
            copy.write_row(row)
            n += 1
    return n


def _replace(
    conn: psycopg.Connection,
    table: str,
    sources: Sequence[Path],
    make_rows: Callable[[Path], Iterable[Row]],
) -> int:
    """TRUNCATE + COPY every source file into `table` inside one transaction."""
    total = 0
    with conn.transaction():
        conn.execute(f"TRUNCATE {table}")
        for src in sources:
            n = _copy(conn, table, make_rows(src))
            log_load(conn, table, src, n)
            total += n
    return total


def load_wyscout(conn: psycopg.Connection, root: Path, log: Callable[[str], None] = print) -> dict:
    """Load all Wyscout files used by the project. Returns row counts per table."""
    w = root / "wyscout"
    counts: dict[str, int] = {}

    def run(table, sources, make_rows):
        counts[table] = _replace(conn, table, sources, make_rows)
        log(f"{table}: {counts[table]:,} rows")

    run("raw.wy_competitions", [w / "competitions.json"], lambda p: competition_rows(read_json(p)))
    run("raw.wy_teams", [w / "teams.json"], lambda p: team_rows(read_json(p)))
    run("raw.wy_players", [w / "players.json"], lambda p: player_rows(read_json(p)))
    run("raw.wy_playerank", [w / "playerank.json"], lambda p: playerank_rows(read_json(p)))
    run(
        "raw.wy_matches",
        [w / "matches" / f"matches_{c}.json" for c in COMPETITION_FILES],
        lambda p: match_rows(read_json(p), p.stem.removeprefix("matches_")),
    )
    run(
        "raw.wy_events",
        [w / "events" / f"events_{c}.json" for c in COMPETITION_FILES],
        lambda p: event_rows(read_json(p), p.stem.removeprefix("events_")),
    )
    return counts
