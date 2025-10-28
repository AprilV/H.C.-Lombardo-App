-- =====================================================================
-- PHASE 2 SQL MIGRATION - ADD MVP COLUMNS
-- =====================================================================
-- Run this once on your database after initial schema creation.
-- If a column already exists, Postgres will skip it (IF NOT EXISTS).
-- 
-- This adds the advanced betting analytics columns to team_game_stats:
--   - drives, plays_per_drive
--   - turnovers, penalty_yards, starting_field_pos_yds
--   - rush_epa_per_play, pass_epa_per_play
--   - early_down_success_rate
--   - red_zone_trips, red_zone_td_rate
--   - third_down_att/conv, fourth_down_att/conv
-- =====================================================================

SET search_path = hcl, public;

ALTER TABLE team_game_stats
  ADD COLUMN IF NOT EXISTS drives                INT,
  ADD COLUMN IF NOT EXISTS plays_per_drive       DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS turnovers             INT,
  ADD COLUMN IF NOT EXISTS penalty_yards         INT,
  ADD COLUMN IF NOT EXISTS starting_field_pos_yds DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS rush_epa_per_play     DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS pass_epa_per_play     DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS early_down_success_rate DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS red_zone_trips        INT,
  ADD COLUMN IF NOT EXISTS red_zone_td_rate      DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS third_down_att        INT,
  ADD COLUMN IF NOT EXISTS third_down_conv       INT,
  ADD COLUMN IF NOT EXISTS fourth_down_att       INT,
  ADD COLUMN IF NOT EXISTS fourth_down_conv      INT;

-- Helpful index for model builds (season/week queries)
CREATE INDEX IF NOT EXISTS idx_tgs_season_week_team_game
  ON team_game_stats(season, week, team_id, game_id);

-- =====================================================================
-- NOTES:
-- - All columns use IF NOT EXISTS so you can re-run safely
-- - DOUBLE PRECISION used for rates/efficiency metrics
-- - INT used for counts (drives, attempts, conversions)
-- - Index on (season, week, team_id, game_id) optimizes model queries
-- =====================================================================
