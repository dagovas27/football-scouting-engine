-- Raw Wyscout tables (Pappalardo et al., 2019). Top-level JSON fields become typed columns;
-- nested objects stay as jsonb. Strings are stored exactly as decoded by the JSON parser, so the
-- double-escaped names (literal \uXXXX) are kept here and fixed in core.
-- No primary keys in raw: uniqueness is checked when building core.

CREATE TABLE IF NOT EXISTS raw.wy_competitions (
    wy_id  integer,
    name   text,
    format text,
    type   text,
    area   jsonb
);

CREATE TABLE IF NOT EXISTS raw.wy_teams (
    wy_id         integer,
    name          text,
    official_name text,
    city          text,
    type          text,
    area          jsonb
);

CREATE TABLE IF NOT EXISTS raw.wy_players (
    wy_id                    integer,
    short_name               text,
    first_name               text,
    middle_name              text,
    last_name                text,
    birth_date               date,
    height                   integer,
    weight                   integer,
    foot                     text,
    role                     jsonb,
    birth_area               jsonb,
    passport_area            jsonb,
    current_team_id          integer,  -- later snapshot, never the 2017/18 club
    current_national_team_id integer
);

CREATE TABLE IF NOT EXISTS raw.wy_matches (
    wy_id          integer,
    competition_id integer,
    season_id      integer,
    round_id       integer,
    gameweek       integer,
    date_utc       timestamp,
    date_local     text,
    duration       text,
    status         text,
    label          text,
    venue          text,
    winner         integer,
    referees       jsonb,
    teams_data     jsonb,
    source_file    text
);

CREATE TABLE IF NOT EXISTS raw.wy_events (
    id             bigint,
    event_id       integer,
    event_name     text,
    sub_event_id   integer,
    sub_event_name text,
    match_id       integer,
    team_id        integer,
    player_id      integer,
    match_period   text,
    event_sec      double precision,
    positions      jsonb,
    tags           jsonb,
    source_file    text
);
CREATE INDEX IF NOT EXISTS wy_events_match_idx ON raw.wy_events (match_id);

CREATE TABLE IF NOT EXISTS raw.wy_playerank (
    match_id        integer,
    player_id       integer,
    minutes_played  integer,
    goal_scored     integer,
    playerank_score double precision,
    role_cluster    text
);
