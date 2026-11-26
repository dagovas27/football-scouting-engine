"""Unit tests for the Wyscout row builders, on small synthetic records (no real data)."""

import json

import pytest

from fse.ingest.wyscout import (
    COLUMNS,
    event_rows,
    match_rows,
    player_rows,
    to_int,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [(None, None), ("", None), ("null", None), (0, 0), ("12", 12), (4502, 4502)],
)
def test_to_int_handles_wyscout_missing_markers(value, expected):
    assert to_int(value) == expected


def _ncols(table: str) -> int:
    return len(COLUMNS[table].split(","))


def test_player_row_keeps_double_escaped_name_and_nulls_ids():
    rec = {
        "wyId": 1,
        "shortName": "I. Konat\\u00e9",
        "firstName": "Ibrahima",
        "middleName": "",
        "lastName": "Konat\\u00e9",
        "birthDate": "1999-05-25",
        "height": 192,
        "weight": 0,
        "foot": "right",
        "role": {"code2": "DF"},
        "birthArea": {"name": "France"},
        "passportArea": {"name": "France"},
        "currentTeamId": None,
        "currentNationalTeamId": "null",
    }
    (row,) = player_rows([rec])
    assert len(row) == _ncols("raw.wy_players")
    assert row[4] == "Konat\\u00e9"  # raw keeps the source string; core decodes it
    assert row[12] is None and row[13] is None
    assert json.loads(row[9]) == {"code2": "DF"}


def test_match_row_serialises_teams_data():
    rec = {
        "wyId": 10,
        "competitionId": 364,
        "seasonId": 181150,
        "roundId": 4405654,
        "gameweek": 1,
        "dateutc": "2017-08-11 18:45:00",
        "date": "August 11, 2017 at 8:45:00 PM GMT+2",
        "duration": "Regular",
        "status": "Played",
        "label": "A - B, 4 - 3",
        "venue": "Stadium",
        "winner": 1609,
        "referees": [],
        "teamsData": {"1609": {"formation": {"lineup": [], "bench": [], "substitutions": []}}},
    }
    (row,) = match_rows([rec], "England")
    assert len(row) == _ncols("raw.wy_matches")
    assert row[-1] == "England"
    assert json.loads(row[13])["1609"]["formation"]["substitutions"] == []


def test_event_row_converts_empty_sub_event_id():
    rec = {
        "id": 177959171,
        "eventId": 8,
        "eventName": "Pass",
        "subEventId": "",
        "subEventName": "",
        "matchId": 2499719,
        "teamId": 1609,
        "playerId": 25413,
        "matchPeriod": "1H",
        "eventSec": 2.75,
        "positions": [{"y": 49, "x": 49}, {"y": 78, "x": 31}],
        "tags": [{"id": 1801}],
    }
    (row,) = event_rows([rec], "England")
    assert len(row) == _ncols("raw.wy_events")
    assert row[3] is None
    assert json.loads(row[11]) == [{"id": 1801}]
