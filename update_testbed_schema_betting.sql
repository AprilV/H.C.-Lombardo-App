-- =============================================================================
-- UPDATE TESTBED SCHEMA: ADD BETTING/WEATHER/CONTEXT COLUMNS
-- =============================================================================
-- Purpose: Add 23 new columns from nflverse schedules data
-- Run this to update existing testbed schema
-- Created: October 28, 2025
-- =============================================================================

SET search_path = hcl_test, public;

-- Add betting lines columns (10 columns)
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS spread_line DOUBLE PRECISION;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS total_line DOUBLE PRECISION;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS home_moneyline DOUBLE PRECISION;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS away_moneyline DOUBLE PRECISION;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS home_spread_odds DOUBLE PRECISION;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS away_spread_odds DOUBLE PRECISION;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS over_odds DOUBLE PRECISION;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS under_odds DOUBLE PRECISION;

-- Add weather columns (4 columns)
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS roof TEXT;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS surface TEXT;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS temp DOUBLE PRECISION;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS wind DOUBLE PRECISION;

-- Add context columns (9 columns)
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS away_rest INT;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS home_rest INT;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS is_divisional_game BOOLEAN;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS overtime INT;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS referee TEXT;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS away_coach TEXT;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS home_coach TEXT;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS away_qb_name TEXT;
ALTER TABLE hcl_test.games ADD COLUMN IF NOT EXISTS home_qb_name TEXT;

-- Add comments for documentation
COMMENT ON COLUMN hcl_test.games.spread_line IS 'Consensus point spread (negative = home favored, e.g., -3.0)';
COMMENT ON COLUMN hcl_test.games.total_line IS 'Consensus over/under total points (e.g., 46.0)';
COMMENT ON COLUMN hcl_test.games.home_moneyline IS 'Home team moneyline odds (e.g., -148)';
COMMENT ON COLUMN hcl_test.games.away_moneyline IS 'Away team moneyline odds (e.g., +124)';
COMMENT ON COLUMN hcl_test.games.roof IS 'Stadium roof type: outdoors, closed, retractable, dome';
COMMENT ON COLUMN hcl_test.games.surface IS 'Playing surface type: grass, fieldturf, a_turf, etc.';
COMMENT ON COLUMN hcl_test.games.temp IS 'Game temperature in Fahrenheit (NULL for domed stadiums)';
COMMENT ON COLUMN hcl_test.games.wind IS 'Wind speed in MPH (NULL for domed stadiums)';
COMMENT ON COLUMN hcl_test.games.away_rest IS 'Days of rest for away team since last game';
COMMENT ON COLUMN hcl_test.games.home_rest IS 'Days of rest for home team since last game';
COMMENT ON COLUMN hcl_test.games.is_divisional_game IS 'TRUE for division rivalry games';
COMMENT ON COLUMN hcl_test.games.overtime IS '1 if game went to overtime, 0 otherwise';
COMMENT ON COLUMN hcl_test.games.referee IS 'Head referee name';
COMMENT ON COLUMN hcl_test.games.away_coach IS 'Away team head coach';
COMMENT ON COLUMN hcl_test.games.home_coach IS 'Home team head coach';
COMMENT ON COLUMN hcl_test.games.away_qb_name IS 'Starting quarterback for away team';
COMMENT ON COLUMN hcl_test.games.home_qb_name IS 'Starting quarterback for home team';

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_games_spread ON hcl_test.games(spread_line) WHERE spread_line IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_games_roof ON hcl_test.games(roof);
CREATE INDEX IF NOT EXISTS idx_games_surface ON hcl_test.games(surface);
CREATE INDEX IF NOT EXISTS idx_games_div_game ON hcl_test.games(is_divisional_game) WHERE is_divisional_game = TRUE;

-- Verification query
SELECT 
    'Schema Update Complete' as status,
    COUNT(*) as total_games,
    COUNT(spread_line) as games_with_spread,
    COUNT(roof) as games_with_weather,
    COUNT(referee) as games_with_referee
FROM hcl_test.games;

COMMENT ON TABLE hcl_test.games IS 'Game metadata, betting lines, weather, and context for all NFL games (enhanced Oct 28, 2025)';

-- Done!
SELECT '✓ 23 new columns added to hcl_test.games table' as result;
