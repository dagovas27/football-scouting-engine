"""S1 acceptance tests against the local database (skipped when it is not reachable or empty).

Expected values come from docs/data-inspection/phase0-report.md, Q3.
"""

from pathlib import Path

import pytest

from fse.db import SQL_DIR

psycopg = pytest.importorskip("psycopg")

pytestmark = pytest.mark.db

# (player, position, minutes, appearances, starts)
BRIGHTON_2017_18 = [
    ("L. Dunk", "DF", 3420, 38, 38),  # ties ordered by name
    ("M. Ryan", "GK", 3420, 38, 38),
    ("S. Duffy", "DF", 3294, 37, 37),
    ("D. Stephens", "MD", 3240, 36, 36),
    ("D. Pröpper", "MD", 3120, 35, 35),
    ("P. Groß", "MD", 2947, 38, 35),
    ("A. Knockaert", "MD", 2424, 33, 27),
    ("G. Bong", "DF", 2238, 25, 25),
    ("G. Murray", "FW", 2201, 35, 25),
    ("Bruno Saltor", "DF", 2017, 25, 23),
    ("J. Izquierdo", "FW", 1988, 32, 23),
    ("S. March", "MD", 1841, 36, 18),
    ("E. Schelotto", "DF", 1317, 20, 15),
    ("M. Suttner", "DF", 1178, 14, 13),
    ("T. Hemed", "FW", 845, 16, 9),
    ("B. Kayal", "MD", 740, 19, 8),
    ("I. Brown", "FW", 307, 13, 4),
    ("L. Ulloa", "FW", 260, 10, 2),
    ("J. Locadia", "FW", 224, 6, 3),
    ("C. Goldson", "DF", 199, 3, 2),
    ("J. Murphy", "MD", 165, 4, 1),
    ("L. Rosenior", "DF", 162, 3, 1),
    ("S. Baldock", "FW", 30, 2, 0),
    ("U. Hünemeier", "DF", 17, 1, 0),
]


def _query(name: str) -> str:
    return (Path(SQL_DIR) / "queries" / name).read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def conn():
    from fse.db import connect

    try:
        c = connect()
    except psycopg.OperationalError as exc:
        pytest.skip(f"database not reachable: {exc}")
    try:
        n = c.execute("SELECT count(*) FROM core.player_match_minutes").fetchone()[0]
    except psycopg.Error:
        c.close()
        pytest.skip("core schema not built")
    if n == 0:
        c.close()
        pytest.skip("core.player_match_minutes is empty: run `fse load all` and `fse build core`")
    yield c
    c.close()


def test_raw_row_counts_match_phase0(conn):
    expected = {
        "raw.wy_players": 3603,
        "raw.wy_teams": 142,
        "raw.wy_matches": 1941,
        "raw.wy_events": 3251294,
        "raw.wy_playerank": 46897,
        "raw.tm_players": 50149,
        "raw.tm_player_valuations": 656301,
        "raw.tm_transfers": 175165,
        "raw.tm_appearances": 1894350,
    }
    for table, n in expected.items():
        assert conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0] == n, table


def test_names_are_decoded(conn):
    left = conn.execute(
        "SELECT count(*) FROM core.wy_player WHERE strpos(concat_ws(' ', first_name,"
        " middle_name, last_name, short_name), '\\u') > 0"
    ).fetchone()[0]
    assert left == 0
    # Source: 'Johann ' / 'Berg Gu\\u00f0munds\\u00adson' -> trimmed, decoded, no soft hyphen
    found = conn.execute(
        "SELECT count(*) FROM core.wy_player"
        " WHERE first_name = 'Johann' AND last_name = 'Berg Guðmundsson'"
    ).fetchone()[0]
    assert found == 1


def test_brighton_minutes_match_phase0(conn):
    rows = conn.execute(_query("brighton_minutes_2017_18.sql")).fetchall()
    assert [tuple(r) for r in rows] == BRIGHTON_2017_18


def test_brighton_played_38_matches(conn):
    n = conn.execute(
        "SELECT count(DISTINCT pm.match_id) FROM core.player_match_minutes pm"
        " JOIN core.wy_team t ON t.wy_id = pm.team_id"
        " WHERE t.name = 'Brighton & Hove Albion'"
    ).fetchone()[0]
    assert n == 38


def test_minutes_agree_with_playerank(conn):
    _, exact, within5, _ = conn.execute(_query("minutes_vs_playerank.sql")).fetchone()
    assert exact >= 0.99
    assert within5 >= 0.995


def test_no_league_player_exceeds_full_season(conn):
    over = conn.execute(
        "SELECT count(*) FROM (SELECT pm.player_id FROM core.player_match_minutes pm"
        " JOIN core.wy_match m ON m.wy_id = pm.match_id"
        " JOIN core.wy_competition c ON c.wy_id = m.competition_id AND c.is_club_league"
        " GROUP BY pm.player_id HAVING sum(pm.minutes) > 3420) x"
    ).fetchone()[0]
    assert over == 0
