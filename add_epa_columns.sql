-- =============================================================================
-- ADD EPA AND ADVANCED STATS COLUMNS - Sprint 9 Enhancement
-- =============================================================================
-- Purpose: Add EPA (Expected Points Added) and advanced metrics for ML model
-- Date: November 6, 2025
-- Sprint: 9 (ML Predictions with 1999-2025 data)
-- =============================================================================

-- Add EPA and Advanced Stats columns to team_game_stats
ALTER TABLE hcl.team_game_stats 
  ADD COLUMN IF NOT EXISTS epa_per_play            DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS success_rate            DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS pass_epa                DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS rush_epa                DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS total_epa               DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS wpa                     DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS cpoe                    DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS air_yards_per_att       DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS yac_per_completion      DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS explosive_play_pct      DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS stuff_rate              DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS pass_success_rate       DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS rush_success_rate       DOUBLE PRECISION;

-- Add comments explaining the new columns
COMMENT ON COLUMN hcl.team_game_stats.epa_per_play IS 'Expected Points Added per play (offense) - KEY ML FEATURE';
COMMENT ON COLUMN hcl.team_game_stats.success_rate IS 'Percentage of plays with positive EPA (offense)';
COMMENT ON COLUMN hcl.team_game_stats.pass_epa IS 'Total EPA on passing plays';
COMMENT ON COLUMN hcl.team_game_stats.rush_epa IS 'Total EPA on rushing plays';
COMMENT ON COLUMN hcl.team_game_stats.total_epa IS 'Total EPA for all plays';
COMMENT ON COLUMN hcl.team_game_stats.wpa IS 'Win Probability Added - cumulative change in win %';
COMMENT ON COLUMN hcl.team_game_stats.cpoe IS 'Completion Percentage Over Expected';
COMMENT ON COLUMN hcl.team_game_stats.air_yards_per_att IS 'Average air yards per pass attempt';
COMMENT ON COLUMN hcl.team_game_stats.yac_per_completion IS 'Yards After Catch per completion';
COMMENT ON COLUMN hcl.team_game_stats.explosive_play_pct IS 'Percentage of plays gaining 20+ yards';
COMMENT ON COLUMN hcl.team_game_stats.stuff_rate IS 'Percentage of rush attempts for 0 or negative yards';
COMMENT ON COLUMN hcl.team_game_stats.pass_success_rate IS 'Success rate on passing plays only';
COMMENT ON COLUMN hcl.team_game_stats.rush_success_rate IS 'Success rate on rushing plays only';

-- Create indexes on EPA columns for faster ML queries
CREATE INDEX IF NOT EXISTS idx_tgs_epa ON hcl.team_game_stats(epa_per_play);
CREATE INDEX IF NOT EXISTS idx_tgs_success_rate ON hcl.team_game_stats(success_rate);
CREATE INDEX IF NOT EXISTS idx_tgs_season_team_epa ON hcl.team_game_stats(season, team, epa_per_play);

-- Verify the changes
SELECT 
    column_name, 
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'hcl' 
  AND table_name = 'team_game_stats'
  AND column_name LIKE '%epa%' OR column_name LIKE '%success%'
ORDER BY ordinal_position;

COMMIT;

-- =============================================================================
-- SUMMARY
-- =============================================================================
-- Added 13 new columns for advanced analytics:
-- 1. epa_per_play - THE most predictive stat (explains 80% of outcomes)
-- 2. success_rate - % of plays that gain EPA
-- 3. pass_epa - EPA on passing plays
-- 4. rush_epa - EPA on rushing plays
-- 5. total_epa - Total EPA for game
-- 6. wpa - Win Probability Added
-- 7. cpoe - Completion % Over Expected
-- 8. air_yards_per_att - Average pass distance
-- 9. yac_per_completion - Yards after catch
-- 10. explosive_play_pct - % of 20+ yard plays
-- 11. stuff_rate - % of negative rush plays
-- 12. pass_success_rate - Success rate for passes
-- 13. rush_success_rate - Success rate for rushes
--
-- These columns will be populated by the enhanced data loader that calculates
-- EPA from play-by-play data (1999-2025).
-- =============================================================================
