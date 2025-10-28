-- =====================================================================
-- PHASE 2 DATABASE SCHEMA - NFL BETTING ANALYTICS MVP
-- =====================================================================
-- 
-- Creates team_game_stats table with all 47 columns for betting models
-- 
-- Columns organized by category:
--   A) Identifiers (7)
--   B) Base Volume & Splits (8)
--   C) Scoring & Pressure/TOs (8)
--   D) Efficiency Advanced (8)
--   E) Situational Red Zone/3rd/4th (6)
--   F) Context (4)
--   G) Rolling Form (6)
--
-- Data Source: nflfastR play-by-play via nfl-data-py
-- Coverage: 2022-2024 seasons (~850 games, ~1700 team-game records)
-- =====================================================================

-- Drop existing table if re-running
DROP TABLE IF EXISTS team_game_stats CASCADE;

-- Create main table
CREATE TABLE team_game_stats (
    
    -- =====================================================================
    -- A) IDENTIFIERS (7 fields)
    -- =====================================================================
    game_id TEXT NOT NULL,              -- Unique game identifier (e.g., "2024_07_DEN_NO")
    team_id TEXT NOT NULL,              -- Team abbreviation (e.g., "DEN")
    season INT NOT NULL,                -- Season year (e.g., 2024)
    week INT NOT NULL,                  -- NFL week number (1-18)
    opponent_id TEXT,                   -- Opponent team abbreviation
    is_home BOOLEAN,                    -- TRUE if home game
    game_date DATE,                     -- Game date
    
    -- =====================================================================
    -- B) BASE VOLUME & SPLITS (8 fields)
    -- =====================================================================
    plays INT,                          -- Total offensive plays
    pass_attempts INT,                  -- Total pass attempts
    rush_attempts INT,                  -- Total rush attempts
    yards_total INT,                    -- Total offensive yards
    yards_pass INT,                     -- Passing yards only
    yards_rush INT,                     -- Rushing yards only
    drives INT,                         -- Number of offensive drives
    plays_per_drive DECIMAL(5,2),      -- Pace proxy (plays / drives)
    
    -- =====================================================================
    -- C) SCORING & PRESSURE/TURNOVERS (8 fields)
    -- =====================================================================
    points_for INT,                     -- Team points scored
    points_against INT,                 -- Opponent points scored
    sacks INT,                          -- Sacks taken by offense
    interceptions INT,                  -- Interceptions thrown
    fumbles_lost INT,                   -- Fumbles lost
    turnovers INT,                      -- Total turnovers (INTs + fumbles)
    penalty_yards INT,                  -- Penalty yards against team
    starting_field_pos_yds DECIMAL(5,2), -- Avg starting field position
    
    -- =====================================================================
    -- D) EFFICIENCY (ADVANCED) (8 fields)
    -- =====================================================================
    yards_per_play DECIMAL(5,2),       -- Offensive efficiency (yards / plays)
    success_plays INT,                  -- Number of successful plays
    success_rate DECIMAL(5,4),         -- Success rate (success / plays)
    epa_total DECIMAL(8,2),            -- Total EPA for game
    epa_per_play DECIMAL(5,3),         -- EPA per play
    rush_epa_per_play DECIMAL(5,3),    -- Rushing EPA per rush attempt
    pass_epa_per_play DECIMAL(5,3),    -- Passing EPA per pass attempt
    early_down_success_rate DECIMAL(5,4), -- Success on 1st/2nd down
    
    -- =====================================================================
    -- E) SITUATIONAL (RED ZONE / 3RD/4TH) (6 fields)
    -- =====================================================================
    red_zone_trips INT,                 -- Drives inside opponent 20
    red_zone_td_rate DECIMAL(5,4),     -- TD rate in red zone
    third_down_att INT,                 -- 3rd down attempts
    third_down_conv INT,                -- 3rd down conversions
    fourth_down_att INT,                -- 4th down attempts
    fourth_down_conv INT,               -- 4th down conversions
    
    -- =====================================================================
    -- F) CONTEXT (4 fields)
    -- =====================================================================
    home_field BOOLEAN,                 -- Same as is_home (clarity)
    days_rest INT,                      -- Days since last game
    short_week BOOLEAN,                 -- Game < 6 days after previous
    off_bye BOOLEAN,                    -- Coming off bye week (13+ days)
    
    -- =====================================================================
    -- G) ROLLING FORM (MOMENTUM) (6 fields)
    -- Computed from PRIOR games only - no look-ahead bias
    -- =====================================================================
    epa_l3 DECIMAL(5,3),               -- Mean EPA/play last 3 games
    epa_l5 DECIMAL(5,3),               -- Mean EPA/play last 5 games
    ppg_for_l3 DECIMAL(5,2),           -- Mean points scored last 3
    ppg_against_l3 DECIMAL(5,2),       -- Mean points allowed last 3
    ypp_l3 DECIMAL(5,2),               -- Mean yards/play last 3
    sr_l3 DECIMAL(5,4),                -- Mean success rate last 3
    
    -- =====================================================================
    -- CONSTRAINTS
    -- =====================================================================
    PRIMARY KEY (game_id, team_id)
);

-- =====================================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================================

-- Team + season queries (most common)
CREATE INDEX idx_team_season ON team_game_stats(team_id, season, week);

-- Date-based queries
CREATE INDEX idx_game_date ON team_game_stats(game_date DESC);

-- Season + week lookups
CREATE INDEX idx_season_week ON team_game_stats(season, week);

-- Opponent matchup queries
CREATE INDEX idx_opponent ON team_game_stats(opponent_id, season);

-- =====================================================================
-- BETTING LINES TABLE (Separate - from schedules, not PBP)
-- =====================================================================

DROP TABLE IF EXISTS betting_lines CASCADE;

CREATE TABLE betting_lines (
    game_id TEXT PRIMARY KEY,          -- Links to team_game_stats
    season INT NOT NULL,
    week INT NOT NULL,
    game_date DATE,
    home_team TEXT,
    away_team TEXT,
    
    -- Spread
    spread_line DECIMAL(4,1),          -- Point spread (negative = favorite)
    home_spread_odds INT,              -- Odds for home spread bet
    away_spread_odds INT,              -- Odds for away spread bet
    
    -- Total
    total_line DECIMAL(4,1),           -- Over/Under total points
    over_odds INT,                     -- Odds for over bet
    under_odds INT,                    -- Odds for under bet
    
    -- Moneyline
    home_moneyline INT,                -- Moneyline for home win
    away_moneyline INT,                -- Moneyline for away win
    
    -- Results (populated after game)
    home_score INT,
    away_score INT,
    spread_result TEXT,                -- 'home_covered', 'away_covered', 'push'
    total_result TEXT                  -- 'over', 'under', 'push'
);

CREATE INDEX idx_betting_season_week ON betting_lines(season, week);
CREATE INDEX idx_betting_date ON betting_lines(game_date DESC);

-- =====================================================================
-- GAME CONTEXT TABLE (Weather, stadium, personnel)
-- =====================================================================

DROP TABLE IF EXISTS game_context CASCADE;

CREATE TABLE game_context (
    game_id TEXT PRIMARY KEY,
    season INT,
    week INT,
    game_date DATE,
    game_time TIME,
    
    -- Venue
    stadium TEXT,
    roof TEXT,                         -- 'dome', 'outdoors', 'retractable'
    surface TEXT,                      -- 'grass', 'sportturf', 'fieldturf'
    
    -- Weather
    temperature INT,                   -- Fahrenheit
    wind_speed INT,                    -- MPH
    
    -- Personnel
    home_qb TEXT,
    away_qb TEXT,
    home_coach TEXT,
    away_coach TEXT,
    referee TEXT,
    
    -- Situational
    is_division_game BOOLEAN,
    is_primetime BOOLEAN               -- Sun/Mon/Thu night games
);

CREATE INDEX idx_context_season ON game_context(season, week);

-- =====================================================================
-- HELPER VIEWS
-- =====================================================================

-- View: Team performance summary by season
CREATE OR REPLACE VIEW team_season_summary AS
SELECT 
    team_id,
    season,
    COUNT(*) as games_played,
    SUM(CASE WHEN points_for > points_against THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN points_for < points_against THEN 1 ELSE 0 END) as losses,
    SUM(CASE WHEN points_for = points_against THEN 1 ELSE 0 END) as ties,
    ROUND(AVG(points_for), 1) as avg_points_for,
    ROUND(AVG(points_against), 1) as avg_points_against,
    ROUND(AVG(yards_per_play), 2) as avg_yards_per_play,
    ROUND(AVG(epa_per_play), 3) as avg_epa_per_play,
    ROUND(AVG(success_rate), 3) as avg_success_rate
FROM team_game_stats
GROUP BY team_id, season
ORDER BY season DESC, wins DESC;

-- View: Home vs Away splits
CREATE OR REPLACE VIEW team_venue_splits AS
SELECT 
    team_id,
    season,
    CASE WHEN is_home THEN 'Home' ELSE 'Away' END as venue,
    COUNT(*) as games,
    ROUND(AVG(points_for), 1) as avg_points_for,
    ROUND(AVG(points_against), 1) as avg_points_against,
    ROUND(AVG(yards_per_play), 2) as avg_ypp,
    ROUND(AVG(epa_per_play), 3) as avg_epa
FROM team_game_stats
GROUP BY team_id, season, is_home
ORDER BY team_id, season, venue;

-- View: Recent form (last 3 games)
CREATE OR REPLACE VIEW team_recent_form AS
WITH ranked_games AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY team_id ORDER BY game_date DESC) as rn
    FROM team_game_stats
    WHERE season = EXTRACT(YEAR FROM CURRENT_DATE)  -- Current season only
)
SELECT 
    team_id,
    ROUND(AVG(points_for), 1) as last_3_ppg,
    ROUND(AVG(points_against), 1) as last_3_ppg_against,
    ROUND(AVG(yards_per_play), 2) as last_3_ypp,
    ROUND(AVG(epa_per_play), 3) as last_3_epa
FROM ranked_games
WHERE rn <= 3
GROUP BY team_id;

-- =====================================================================
-- SAMPLE QUERIES
-- =====================================================================

-- Get all stats for a team in a season:
-- SELECT * FROM team_game_stats WHERE team_id = 'KC' AND season = 2024 ORDER BY week;

-- Get betting lines with team stats for upcoming week:
-- SELECT b.*, tg1.epa_l3 as home_epa_l3, tg2.epa_l3 as away_epa_l3
-- FROM betting_lines b
-- LEFT JOIN team_game_stats tg1 ON b.game_id = tg1.game_id AND b.home_team = tg1.team_id
-- LEFT JOIN team_game_stats tg2 ON b.game_id = tg2.game_id AND b.away_team = tg2.team_id
-- WHERE b.week = 8 AND b.season = 2024;

-- Get team matchup history:
-- SELECT * FROM team_game_stats 
-- WHERE (team_id = 'KC' AND opponent_id = 'BUF') 
--    OR (team_id = 'BUF' AND opponent_id = 'KC')
-- ORDER BY game_date DESC LIMIT 10;

-- =====================================================================
-- NOTES
-- =====================================================================
--
-- Data Volume Estimates:
--   - ~285 games per season (17 weeks × ~16 games/week + playoffs)
--   - ~570 team-game records per season (2 teams per game)
--   - 3 seasons (2022-2024) = ~1,710 records
--   - Storage: ~500 KB per season
--
-- Performance:
--   - Indexes on team_id + season enable fast queries
--   - Views pre-compute common aggregations
--   - Consider materialized views if query performance degrades
--
-- Data Quality:
--   - Check for NULL values in critical fields (points, yards, EPA)
--   - Verify rolling averages don't include current game (look-ahead bias)
--   - Validate betting_lines.spread_result matches actual game outcome
--
-- Future Enhancements (Phase 3):
--   - Add defensive stats (calculate from opponent offense)
--   - Add opponent-adjusted metrics (strength of schedule)
--   - Add drive-level detail table
--   - Add player injury impact scores
--
-- =====================================================================

COMMENT ON TABLE team_game_stats IS 'Team performance stats aggregated from nflfastR play-by-play data. All 47 columns for betting analytics MVP. Data covers 2022-2024 seasons.';
COMMENT ON TABLE betting_lines IS 'Betting lines (spread, total, moneyline) from nflverse schedules. Includes results for historical analysis.';
COMMENT ON TABLE game_context IS 'Game context (weather, stadium, personnel) for situational modeling.';
