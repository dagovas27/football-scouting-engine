-- Core Wyscout entities: clean and typed, built from raw by `fse build core`.

-- Wyscout names are double-escaped: after JSON parsing they still contain literal \uXXXX sequences.
-- Re-parse the text as a JSON string to decode them, drop soft hyphens (U+00AD) and trim.
CREATE OR REPLACE FUNCTION core.decode_wy_text(s text) RETURNS text
LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE AS $$
    SELECT btrim(replace(
        CASE WHEN strpos(s, '\u') > 0
             THEN ('"' || replace(s, '"', '\"') || '"')::json #>> '{}'
             ELSE s END,
        U&'\00AD', ''))
$$;

CREATE TABLE IF NOT EXISTS core.wy_competition (
    wy_id         integer PRIMARY KEY,
    name          text    NOT NULL,
    area_name     text,
    is_club_league boolean NOT NULL
);

CREATE TABLE IF NOT EXISTS core.wy_team (
    wy_id         integer PRIMARY KEY,
    name          text    NOT NULL,
    official_name text,
    type          text    NOT NULL,
    area_name     text
);

CREATE TABLE IF NOT EXISTS core.wy_player (
    wy_id       integer PRIMARY KEY,
    short_name  text NOT NULL,
    first_name  text,
    middle_name text,
    last_name   text,
    birth_date  date,
    role_code   text,   -- GK / DF / MD / FW
    foot        text,
    height_cm   integer,
    weight_kg   integer
);

CREATE TABLE IF NOT EXISTS core.wy_match (
    wy_id          integer PRIMARY KEY,
    competition_id integer NOT NULL REFERENCES core.wy_competition (wy_id),
    season_id      integer NOT NULL,
    gameweek       integer,
    date_utc       timestamp NOT NULL,
    duration       text    NOT NULL,   -- Regular / ExtraTime / Penalties
    match_length   integer NOT NULL,   -- 90 or 120 minutes, stoppage time not counted
    label          text
);

-- Approximate minutes per player and match (Phase 0, Q3; validated 99.0% exact vs PlayeRank).
CREATE TABLE IF NOT EXISTS core.player_match_minutes (
    match_id        integer NOT NULL REFERENCES core.wy_match (wy_id),
    team_id         integer NOT NULL,
    player_id       integer NOT NULL,
    is_starter      boolean NOT NULL,
    minute_in       integer NOT NULL,
    minute_out      integer NOT NULL,
    red_card_minute integer,
    minutes         integer NOT NULL CHECK (minutes BETWEEN 0 AND 120),
    PRIMARY KEY (match_id, player_id)
);
CREATE INDEX IF NOT EXISTS player_match_minutes_team_idx ON core.player_match_minutes (team_id);
