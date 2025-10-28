-- =====================================================================
-- HC in Lombardo — Human-facing Game Matchup View (Regular Season Only)
-- One row per game with home/away stats side-by-side.
-- Requires: hcl.games, hcl.team_game_stats, hcl.team_context (optional), hcl.weather (optional)
-- Safe to re-run.
-- =====================================================================
-- 
-- Purpose: Display view for UI/API consumption
-- Output: One row per game with home vs away stats pivoted side-by-side
-- Features:
--   - Season-to-date averages (per-game stats)
--   - Last-3 game form (momentum indicators)
--   - Simple diffs (home minus away edges)
--   - No look-ahead bias (only uses prior games)
--   - Regular season only
--
-- Usage:
--   SELECT * FROM v_game_matchup_display WHERE season = 2024 AND week = 8;
-- =====================================================================

SET search_path = hcl, public;

CREATE OR REPLACE VIEW v_game_matchup_display AS
WITH base AS (
  SELECT
    g.game_id, g.season, g.week, g.game_date,
    g.home_team, g.away_team, g.stadium, g.city, g.state, g.timezone
  FROM games g
  WHERE COALESCE(g.is_postseason, FALSE) = FALSE
),

/* ---------- Helper: season-to-date aggregate up to (week-1) ---------- */
-- Aggregates only prior games this season to avoid look-ahead.
home_st AS (
  SELECT
    b.game_id,
    COUNT(*)                                AS home_gp,
    SUM(t.points_for)                       AS home_pf,
    SUM(t.points_against)                   AS home_pa,
    SUM(t.plays)                            AS home_plays,
    SUM(t.yards_total)                      AS home_yards_total,
    SUM(t.success_plays)                    AS home_success_plays,
    SUM(t.epa_total)                        AS home_epa_total,
    SUM(t.turnovers)                        AS home_turnovers,
    SUM(t.red_zone_trips)                   AS home_rz_trips,
    SUM(t.third_down_att)                   AS home_3d_att,
    SUM(t.third_down_conv)                  AS home_3d_conv,
    SUM(t.fourth_down_att)                  AS home_4d_att,
    SUM(t.fourth_down_conv)                 AS home_4d_conv
  FROM base b
  JOIN team_game_stats t
    ON t.season = b.season
   AND t.team_id = b.home_team
   AND t.week   < b.week
  GROUP BY b.game_id
),
away_st AS (
  SELECT
    b.game_id,
    COUNT(*)                                AS away_gp,
    SUM(t.points_for)                       AS away_pf,
    SUM(t.points_against)                   AS away_pa,
    SUM(t.plays)                            AS away_plays,
    SUM(t.yards_total)                      AS away_yards_total,
    SUM(t.success_plays)                    AS away_success_plays,
    SUM(t.epa_total)                        AS away_epa_total,
    SUM(t.turnovers)                        AS away_turnovers,
    SUM(t.red_zone_trips)                   AS away_rz_trips,
    SUM(t.third_down_att)                   AS away_3d_att,
    SUM(t.third_down_conv)                  AS away_3d_conv,
    SUM(t.fourth_down_att)                  AS away_4d_att,
    SUM(t.fourth_down_conv)                 AS away_4d_conv
  FROM base b
  JOIN team_game_stats t
    ON t.season = b.season
   AND t.team_id = b.away_team
   AND t.week   < b.week
  GROUP BY b.game_id
),

/* ---------- Helper: last-3 form (EPA/YPP/PPG) ---------- */
home_l3 AS (
  SELECT b.game_id,
         AVG(sub.epa_per_play)              AS home_epa_l3,
         AVG(sub.yards_total::FLOAT / NULLIF(sub.plays,0)) AS home_ypp_l3,
         AVG(sub.points_for)                AS home_ppg_l3
  FROM base b
  JOIN LATERAL (
      SELECT epa_per_play, yards_total, plays, points_for
      FROM team_game_stats t
      WHERE t.season = b.season
        AND t.team_id = b.home_team
        AND t.week   < b.week
      ORDER BY t.week DESC
      LIMIT 3
  ) sub ON TRUE
  GROUP BY b.game_id
),
away_l3 AS (
  SELECT b.game_id,
         AVG(sub.epa_per_play)              AS away_epa_l3,
         AVG(sub.yards_total::FLOAT / NULLIF(sub.plays,0)) AS away_ypp_l3,
         AVG(sub.points_for)                AS away_ppg_l3
  FROM base b
  JOIN LATERAL (
      SELECT epa_per_play, yards_total, plays, points_for
      FROM team_game_stats t
      WHERE t.season = b.season
        AND t.team_id = b.away_team
        AND t.week   < b.week
      ORDER BY t.week DESC
      LIMIT 3
  ) sub ON TRUE
  GROUP BY b.game_id
)

/* ---------- Final select: human-facing matchup card ---------- */
SELECT
  b.season, b.week, b.game_date,
  b.game_id,
  b.home_team, b.away_team,
  b.stadium, b.city, b.state, b.timezone,

  -- Home: season-to-date (per-game averages unless noted)
  h.home_gp,
  CASE WHEN h.home_gp > 0 THEN h.home_pf::FLOAT / h.home_gp ELSE NULL END                    AS home_ppg_for,
  CASE WHEN h.home_gp > 0 THEN h.home_pa::FLOAT / h.home_gp ELSE NULL END                    AS home_ppg_against,
  CASE WHEN h.home_plays > 0 THEN h.home_yards_total::FLOAT / h.home_plays ELSE NULL END     AS home_ypp,
  CASE WHEN h.home_plays > 0 THEN h.home_success_plays::FLOAT / h.home_plays ELSE NULL END   AS home_sr,
  CASE WHEN h.home_plays > 0 THEN h.home_epa_total / h.home_plays ELSE NULL END              AS home_epa_pp,
  CASE WHEN h.home_gp    > 0 THEN h.home_turnovers::FLOAT / h.home_gp ELSE NULL END          AS home_to_pg,
  CASE WHEN h.home_rz_trips > 0 THEN h.home_4d_conv::FLOAT / NULLIF(h.home_4d_att,0) END     AS home_4d_rate,
  CASE WHEN h.home_3d_att > 0 THEN h.home_3d_conv::FLOAT / h.home_3d_att ELSE NULL END       AS home_3d_rate,

  -- Away: season-to-date
  a.away_gp,
  CASE WHEN a.away_gp > 0 THEN a.away_pf::FLOAT / a.away_gp ELSE NULL END                    AS away_ppg_for,
  CASE WHEN a.away_gp > 0 THEN a.away_pa::FLOAT / a.away_gp ELSE NULL END                    AS away_ppg_against,
  CASE WHEN a.away_plays > 0 THEN a.away_yards_total::FLOAT / a.away_plays ELSE NULL END     AS away_ypp,
  CASE WHEN a.away_plays > 0 THEN a.away_success_plays::FLOAT / a.away_plays ELSE NULL END   AS away_sr,
  CASE WHEN a.away_plays > 0 THEN a.away_epa_total / a.away_plays ELSE NULL END              AS away_epa_pp,
  CASE WHEN a.away_gp    > 0 THEN a.away_turnovers::FLOAT / a.away_gp ELSE NULL END          AS away_to_pg,
  CASE WHEN a.away_rz_trips > 0 THEN a.away_4d_conv::FLOAT / NULLIF(a.away_4d_att,0) END     AS away_4d_rate,
  CASE WHEN a.away_3d_att > 0 THEN a.away_3d_conv::FLOAT / a.away_3d_att ELSE NULL END       AS away_3d_rate,

  -- Last-3 form (momentum indicators)
  hl3.home_epa_l3, hl3.home_ypp_l3, hl3.home_ppg_l3,
  al3.away_epa_l3, al3.away_ypp_l3, al3.away_ppg_l3,

  -- Simple diffs (home minus away) for quick "edge" read in the UI
  (CASE WHEN h.home_plays > 0 AND a.away_plays > 0
        THEN (h.home_epa_total / h.home_plays) - (a.away_epa_total / a.away_plays) END)      AS diff_epa_pp,
  (CASE WHEN h.home_plays > 0 AND a.away_plays > 0
        THEN (h.home_yards_total::FLOAT / h.home_plays) - (a.away_yards_total::FLOAT / a.away_plays) END) AS diff_ypp,
  (CASE WHEN h.home_plays > 0 AND a.away_plays > 0
        THEN (h.home_success_plays::FLOAT / h.home_plays) - (a.away_success_plays::FLOAT / a.away_plays) END) AS diff_sr,
  (CASE WHEN h.home_gp    > 0 AND a.away_gp    > 0
        THEN (h.home_pf::FLOAT / h.home_gp) - (a.away_pf::FLOAT / a.away_gp) END)            AS diff_ppg_for

FROM base b
LEFT JOIN home_st h  ON h.game_id = b.game_id
LEFT JOIN away_st a  ON a.game_id = b.game_id
LEFT JOIN home_l3 hl3 ON hl3.game_id = b.game_id
LEFT JOIN away_l3 al3 ON al3.game_id = b.game_id
ORDER BY b.season DESC, b.week DESC, b.game_date NULLS LAST, b.home_team, b.away_team;

-- =====================================================================
-- EXAMPLE QUERIES
-- =====================================================================

-- Get all matchups for upcoming week 8:
-- SELECT * FROM v_game_matchup_display WHERE season = 2024 AND week = 8;

-- Get single game matchup:
-- SELECT * FROM v_game_matchup_display WHERE game_id = '2024_08_KC_BUF';

-- Get all games for a specific team:
-- SELECT * FROM v_game_matchup_display 
-- WHERE season = 2024 AND (home_team = 'KC' OR away_team = 'KC')
-- ORDER BY week;

-- =====================================================================
-- OPTIONAL ENHANCEMENTS
-- =====================================================================

-- Add weather context (if hcl.weather table exists):
-- LEFT JOIN hcl.weather w ON w.game_id = b.game_id

-- Add rest days context (if hcl.team_context table exists):
-- LEFT JOIN hcl.team_context hc ON hc.game_id = b.game_id AND hc.team_id = b.home_team
-- LEFT JOIN hcl.team_context ac ON ac.game_id = b.game_id AND ac.team_id = b.away_team

-- Add betting lines (if hcl.betting_lines table exists):
-- LEFT JOIN hcl.betting_lines bl ON bl.game_id = b.game_id

-- =====================================================================
-- OUTPUT COLUMNS (43 total)
-- =====================================================================
-- 
-- Game Identifiers (10):
--   season, week, game_date, game_id, home_team, away_team, 
--   stadium, city, state, timezone
--
-- Home Season-to-Date (9):
--   home_gp, home_ppg_for, home_ppg_against, home_ypp, home_sr, 
--   home_epa_pp, home_to_pg, home_4d_rate, home_3d_rate
--
-- Away Season-to-Date (9):
--   away_gp, away_ppg_for, away_ppg_against, away_ypp, away_sr,
--   away_epa_pp, away_to_pg, away_4d_rate, away_3d_rate
--
-- Momentum Last-3 Games (6):
--   home_epa_l3, home_ypp_l3, home_ppg_l3,
--   away_epa_l3, away_ypp_l3, away_ppg_l3
--
-- Matchup Edges (4):
--   diff_epa_pp, diff_ypp, diff_sr, diff_ppg_for
--
-- =====================================================================
-- NOTES
-- =====================================================================
--
-- 1. NO LOOK-AHEAD BIAS:
--    - Season-to-date uses t.week < b.week (only prior games)
--    - Last-3 uses ORDER BY t.week DESC LIMIT 3 (prior games only)
--    - Week 1 games will have NULL for season-to-date (no prior data)
--
-- 2. NULL HANDLING:
--    - If team hasn't played, all averages return NULL
--    - UI can display "N/A" or hide stats for Week 1
--    - NULLIF() prevents division by zero
--
-- 3. REGULAR SEASON ONLY:
--    - WHERE COALESCE(g.is_postseason, FALSE) = FALSE
--    - Excludes playoff games from view
--
-- 4. PERFORMANCE:
--    - CTEs optimize repeated aggregations
--    - LATERAL joins for last-3 are efficient with proper indexes
--    - Index on (season, team_id, week) recommended
--
-- 5. UI CONSUMPTION:
--    - Perfect for React matchup cards
--    - All fields are pre-calculated (no client-side math)
--    - Diffs show home advantage at a glance
--
-- =====================================================================
