-- Validation of derived minutes against PlayeRank's minutesPlayed (Phase 0: 99.0% exact).
SELECT count(*)                                                         AS player_matches,
       round(avg((pm.minutes = pr.minutes_played)::int)::numeric, 4)     AS exact_share,
       round(avg((abs(pm.minutes - pr.minutes_played) <= 5)::int)::numeric, 4) AS within_5_share,
       round(avg(abs(pm.minutes - pr.minutes_played))::numeric, 2)        AS mean_abs_diff
FROM core.player_match_minutes pm
JOIN raw.wy_playerank pr ON pr.match_id = pm.match_id AND pr.player_id = pm.player_id;
