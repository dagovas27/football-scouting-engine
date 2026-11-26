-- Rebuild core Wyscout tables from raw. Executed in one transaction by `fse build core`.

TRUNCATE core.player_match_minutes, core.wy_match, core.wy_player, core.wy_team,
         core.wy_competition;

INSERT INTO core.wy_competition (wy_id, name, area_name, is_club_league)
SELECT wy_id, name, area ->> 'name', type = 'club'
FROM raw.wy_competitions;

INSERT INTO core.wy_team (wy_id, name, official_name, type, area_name)
SELECT wy_id,
       core.decode_wy_text(name),
       core.decode_wy_text(official_name),
       type,
       area ->> 'name'
FROM raw.wy_teams;

INSERT INTO core.wy_player (wy_id, short_name, first_name, middle_name, last_name, birth_date,
                            role_code, foot, height_cm, weight_kg)
SELECT wy_id,
       core.decode_wy_text(short_name),
       core.decode_wy_text(first_name),
       nullif(core.decode_wy_text(middle_name), ''),
       core.decode_wy_text(last_name),
       birth_date,
       role ->> 'code2',
       nullif(nullif(foot, ''), 'null'),
       nullif(height, 0),
       nullif(weight, 0)
FROM raw.wy_players;

INSERT INTO core.wy_match (wy_id, competition_id, season_id, gameweek, date_utc, duration,
                           match_length, label)
SELECT wy_id, competition_id, season_id, gameweek, date_utc, duration,
       CASE WHEN duration = 'Regular' THEN 90 ELSE 120 END,
       core.decode_wy_text(label)
FROM raw.wy_matches;

-- Minutes: starters enter at 0, substitutes at their substitution minute; a player leaves at the
-- substitution-out minute, at a red card (formation.redCards holds the card minute) or at full time.
-- All minutes are capped at the match length.
WITH team_formation AS (
    SELECT m.wy_id AS match_id,
           m.match_length,
           kv.key::integer AS team_id,
           kv.value -> 'formation' AS f
    FROM core.wy_match m
    JOIN raw.wy_matches r ON r.wy_id = m.wy_id
    CROSS JOIN LATERAL jsonb_each(r.teams_data) AS kv
),
subs AS (
    SELECT tf.match_id, tf.team_id,
           (s ->> 'playerIn')::integer  AS player_in,
           (s ->> 'playerOut')::integer AS player_out,
           (s ->> 'minute')::integer    AS minute
    FROM team_formation tf
    CROSS JOIN LATERAL jsonb_array_elements(
        CASE WHEN jsonb_typeof(tf.f -> 'substitutions') = 'array'
             THEN tf.f -> 'substitutions' ELSE '[]'::jsonb END) AS s
),
sub_in AS (
    SELECT match_id, team_id, player_in AS player_id, min(minute) AS minute
    FROM subs GROUP BY 1, 2, 3
),
sub_out AS (
    SELECT match_id, team_id, player_out AS player_id, max(minute) AS minute
    FROM subs GROUP BY 1, 2, 3
),
squad AS (
    SELECT tf.match_id, tf.team_id, tf.match_length, true AS is_starter, p
    FROM team_formation tf
    CROSS JOIN LATERAL jsonb_array_elements(tf.f -> 'lineup') AS p
    UNION ALL
    SELECT tf.match_id, tf.team_id, tf.match_length, false, p
    FROM team_formation tf
    CROSS JOIN LATERAL jsonb_array_elements(
        CASE WHEN jsonb_typeof(tf.f -> 'bench') = 'array'
             THEN tf.f -> 'bench' ELSE '[]'::jsonb END) AS p
),
played AS (
    SELECT q.match_id, q.team_id, (q.p ->> 'playerId')::integer AS player_id, q.is_starter,
           q.match_length,
           nullif(nullif(q.p ->> 'redCards', 'null'), '0')::integer AS red_card_minute,
           CASE WHEN q.is_starter THEN 0 ELSE least(si.minute, q.match_length) END AS minute_in,
           so.minute AS sub_out_minute
    FROM squad q
    LEFT JOIN sub_in  si ON si.match_id = q.match_id AND si.team_id = q.team_id
                        AND si.player_id = (q.p ->> 'playerId')::integer
    LEFT JOIN sub_out so ON so.match_id = q.match_id AND so.team_id = q.team_id
                        AND so.player_id = (q.p ->> 'playerId')::integer
    WHERE q.is_starter OR si.minute IS NOT NULL
)
INSERT INTO core.player_match_minutes (match_id, team_id, player_id, is_starter, minute_in,
                                       minute_out, red_card_minute, minutes)
SELECT match_id, team_id, player_id, is_starter, minute_in,
       least(coalesce(sub_out_minute, match_length), coalesce(red_card_minute, match_length),
             match_length) AS minute_out,
       red_card_minute,
       greatest(0, least(coalesce(sub_out_minute, match_length),
                         coalesce(red_card_minute, match_length), match_length) - minute_in)
FROM played;
