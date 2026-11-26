-- S1 acceptance query: minutes played by every Brighton & Hove Albion player in the 2017/18
-- Premier League (Wyscout season 181150). Expected result: docs/data-inspection/phase0-report.md, Q3.
SELECT p.short_name                          AS player,
       p.role_code                           AS pos,
       sum(pm.minutes)                       AS minutes,
       count(*)                              AS appearances,
       count(*) FILTER (WHERE pm.is_starter) AS starts
FROM core.player_match_minutes pm
JOIN core.wy_match  m ON m.wy_id = pm.match_id
JOIN core.wy_team   t ON t.wy_id = pm.team_id
JOIN core.wy_player p ON p.wy_id = pm.player_id
WHERE t.name = 'Brighton & Hove Albion'
  AND m.season_id = 181150
GROUP BY p.wy_id, p.short_name, p.role_code
ORDER BY minutes DESC, player;
