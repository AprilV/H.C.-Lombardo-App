-- =============================================================================
-- H.C. LOMBARDO APP - TESTBED HCL SCHEMA CREATION
-- =============================================================================
-- Purpose: Create HCL (Historical Context Layer) schema for game-by-game data
-- Testing: Run in testbed database first before production deployment
-- Created: October 28, 2025
-- Reference: PHASE2_IMPLEMENTATION_PLAN.md
-- =============================================================================

-- Create schema for historical data
CREATE SCHEMA IF NOT EXISTS hcl_test;
SET search_path = hcl_test, public;

-- =============================================================================
-- TABLE 1: games (Game Metadata)
-- =============================================================================
-- Purpose: Store basic information about each NFL game
-- Source: nflverse schedules data
-- Primary Key: game_id (nflverse format: YYYY_WW_AWAY_HOME)
-- =============================================================================

CREATE TABLE IF NOT EXISTS hcl_test.games (
  game_id          TEXT PRIMARY KEY,
  season           INT NOT NULL,
  week             INT NOT NULL,
  game_date        DATE,
  kickoff_time_utc TIMESTAMPTZ,
  home_team        TEXT NOT NULL,
  away_team        TEXT NOT NULL,
  stadium          TEXT,
  city             TEXT,
  state            TEXT,
  timezone         TEXT,
  is_postseason    BOOLEAN DEFAULT FALSE,
  home_score       INT,
  away_score       INT,
  
  -- Betting Lines (from nflverse schedules)
  spread_line           DOUBLE PRECISION,  -- Point spread (negative = home favored)
  total_line            DOUBLE PRECISION,  -- Over/under total points
  home_moneyline        DOUBLE PRECISION,  -- Home team moneyline odds
  away_moneyline        DOUBLE PRECISION,  -- Away team moneyline odds
  home_spread_odds      DOUBLE PRECISION,  -- Home spread betting odds
  away_spread_odds      DOUBLE PRECISION,  -- Away spread betting odds
  over_odds             DOUBLE PRECISION,  -- Over bet odds
  under_odds            DOUBLE PRECISION,  -- Under bet odds
  
  -- Weather Conditions (from nflverse schedules)
  roof                  TEXT,              -- Stadium type: outdoors/closed/retractable/dome
  surface               TEXT,              -- Playing surface: grass/turf types
  temp                  DOUBLE PRECISION,  -- Temperature in Fahrenheit
  wind                  DOUBLE PRECISION,  -- Wind speed in MPH
  
  -- Game Context (from nflverse schedules)
  away_rest             INT,               -- Days since away team's last game
  home_rest             INT,               -- Days since home team's last game
  is_divisional_game    BOOLEAN,           -- TRUE for division games
  overtime              INT,               -- 1 if game went to OT, 0 otherwise
  referee               TEXT,              -- Head referee name
  away_coach            TEXT,              -- Away team head coach
  home_coach            TEXT,              -- Home team head coach
  away_qb_name          TEXT,              -- Starting away QB
  home_qb_name          TEXT,              -- Starting home QB
  
  created_at       TIMESTAMPTZ DEFAULT NOW(),
  updated_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_games_season_week ON hcl_test.games(season, week);
CREATE INDEX IF NOT EXISTS idx_games_kickoff ON hcl_test.games(kickoff_time_utc);
CREATE INDEX IF NOT EXISTS idx_games_home_team ON hcl_test.games(home_team);
CREATE INDEX IF NOT EXISTS idx_games_away_team ON hcl_test.games(away_team);

COMMENT ON TABLE hcl_test.games IS 'Game metadata, betting lines, weather, and context for all NFL games';
COMMENT ON COLUMN hcl_test.games.game_id IS 'Unique identifier format: YYYY_WW_AWAY_HOME';
COMMENT ON COLUMN hcl_test.games.week IS 'Week number: 1-18 regular season, 19+ playoffs';
COMMENT ON COLUMN hcl_test.games.is_postseason IS 'TRUE for playoff games';
COMMENT ON COLUMN hcl_test.games.spread_line IS 'Consensus point spread (negative = home favored, e.g., -3.0)';
COMMENT ON COLUMN hcl_test.games.total_line IS 'Consensus over/under total points (e.g., 46.0)';
COMMENT ON COLUMN hcl_test.games.roof IS 'Stadium roof type: outdoors, closed, retractable, dome';
COMMENT ON COLUMN hcl_test.games.temp IS 'Game temperature in Fahrenheit (NULL for domed stadiums)';
COMMENT ON COLUMN hcl_test.games.away_rest IS 'Days of rest for away team since last game';
COMMENT ON COLUMN hcl_test.games.home_rest IS 'Days of rest for home team since last game';

-- =============================================================================
-- TABLE 2: team_game_stats (Performance Metrics Per Game)
-- =============================================================================
-- Purpose: Store comprehensive stats for each team in each game
-- Source: nflverse play-by-play data aggregated to game level
-- Primary Key: (game_id, team)
-- Foreign Key: game_id references games(game_id)
-- =============================================================================

CREATE TABLE IF NOT EXISTS hcl_test.team_game_stats (
  game_id                    TEXT NOT NULL,
  team                       TEXT NOT NULL,
  opponent                   TEXT NOT NULL,
  is_home                    BOOLEAN NOT NULL,
  season                     INT NOT NULL,
  week                       INT NOT NULL,
  
  -- Scoring
  points                     INT,
  touchdowns                 INT,
  field_goals_made           INT,
  field_goals_att            INT,
  
  -- Offensive Stats
  total_yards                INT,
  passing_yards              INT,
  rushing_yards              INT,
  plays                      INT,
  yards_per_play             DOUBLE PRECISION,
  
  -- Passing Stats
  completions                INT,
  passing_att                INT,
  completion_pct             DOUBLE PRECISION,
  passing_tds                INT,
  interceptions              INT,
  sacks_taken                INT,
  sack_yards_lost            INT,
  qb_rating                  DOUBLE PRECISION,
  
  -- Rushing Stats
  rushing_att                INT,
  yards_per_carry            DOUBLE PRECISION,
  rushing_tds                INT,
  
  -- Efficiency Metrics
  third_down_conv            INT,
  third_down_att             INT,
  third_down_pct             DOUBLE PRECISION,
  fourth_down_conv           INT,
  fourth_down_att            INT,
  fourth_down_pct            DOUBLE PRECISION,
  red_zone_conv              INT,
  red_zone_att               INT,
  red_zone_pct               DOUBLE PRECISION,
  
  -- Special Teams
  punt_count                 INT,
  punt_avg_yards             DOUBLE PRECISION,
  kickoff_return_yards       INT,
  punt_return_yards          INT,
  
  -- Defense/Turnovers
  turnovers                  INT,
  fumbles_lost               INT,
  penalties                  INT,
  penalty_yards              INT,
  
  -- Time of Possession
  time_of_possession_sec     INT,
  time_of_possession_pct     DOUBLE PRECISION,
  
  -- Advanced Metrics
  drives                     INT,
  early_down_success_rate    DOUBLE PRECISION,
  starting_field_pos_yds     DOUBLE PRECISION,
  
  -- Result
  result                     TEXT,  -- 'W', 'L', 'T'
  
  created_at                 TIMESTAMPTZ DEFAULT NOW(),
  updated_at                 TIMESTAMPTZ DEFAULT NOW(),
  
  PRIMARY KEY (game_id, team),
  FOREIGN KEY (game_id) REFERENCES hcl_test.games(game_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tgs_team ON hcl_test.team_game_stats(team);
CREATE INDEX IF NOT EXISTS idx_tgs_season_week ON hcl_test.team_game_stats(season, week);
CREATE INDEX IF NOT EXISTS idx_tgs_season_team ON hcl_test.team_game_stats(season, team);

COMMENT ON TABLE hcl_test.team_game_stats IS 'Comprehensive performance statistics for each team in each game';
COMMENT ON COLUMN hcl_test.team_game_stats.is_home IS 'TRUE if team is home, FALSE if away';
COMMENT ON COLUMN hcl_test.team_game_stats.result IS 'Game result: W (win), L (loss), T (tie)';

-- =============================================================================
-- TABLE 3: betting_lines (Historical Odds Data) - OPTIONAL
-- =============================================================================
-- Purpose: Store betting odds from various sportsbooks
-- Source: CSV imports or betting API (future)
-- Primary Key: (game_id, book, line_type)
-- =============================================================================

CREATE TABLE IF NOT EXISTS hcl_test.betting_lines (
  game_id          TEXT    NOT NULL,
  book             TEXT    NOT NULL,
  line_type        TEXT    NOT NULL,  -- 'spread', 'total', 'moneyline'
  open_value       DOUBLE PRECISION,
  open_time_utc    TIMESTAMPTZ,
  close_value      DOUBLE PRECISION,
  close_time_utc   TIMESTAMPTZ,
  created_at       TIMESTAMPTZ DEFAULT NOW(),
  
  PRIMARY KEY (game_id, book, line_type),
  FOREIGN KEY (game_id) REFERENCES hcl_test.games(game_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_blines_type ON hcl_test.betting_lines(line_type);
CREATE INDEX IF NOT EXISTS idx_blines_game ON hcl_test.betting_lines(game_id);

COMMENT ON TABLE hcl_test.betting_lines IS 'Historical betting odds from sportsbooks';
COMMENT ON COLUMN hcl_test.betting_lines.line_type IS 'Type: spread, total, moneyline';

-- =============================================================================
-- TABLE 4: injuries (Weekly Injury Reports) - OPTIONAL
-- =============================================================================
-- Purpose: Track player injuries for advanced analysis
-- Source: nflverse injuries data
-- Primary Key: (season, week, team, full_name)
-- =============================================================================

CREATE TABLE IF NOT EXISTS hcl_test.injuries (
  season       INT NOT NULL,
  week         INT NOT NULL,
  team         TEXT NOT NULL,
  full_name    TEXT NOT NULL,
  position     TEXT,
  status       TEXT,  -- 'Out', 'Doubtful', 'Questionable', 'Probable'
  designation  TEXT,  -- 'IR', 'PUP', etc.
  report_date  DATE,
  gsis_id      TEXT,
  updated_at   TIMESTAMPTZ DEFAULT NOW(),
  
  PRIMARY KEY (season, week, team, full_name)
);

CREATE INDEX IF NOT EXISTS idx_injuries_team ON hcl_test.injuries(team);
CREATE INDEX IF NOT EXISTS idx_injuries_season_week ON hcl_test.injuries(season, week);

COMMENT ON TABLE hcl_test.injuries IS 'Weekly injury reports for players';

-- =============================================================================
-- TABLE 5: weather (Game Weather Conditions) - OPTIONAL
-- =============================================================================
-- Purpose: Store weather data for outdoor games
-- Source: Weather API or manual data entry
-- Primary Key: game_id
-- =============================================================================

CREATE TABLE IF NOT EXISTS hcl_test.weather (
  game_id        TEXT PRIMARY KEY,
  roof           TEXT,  -- 'dome', 'open', 'retractable_open', 'retractable_closed'
  surface        TEXT,  -- 'grass', 'turf'
  temp_f         DOUBLE PRECISION,
  wind_mph       DOUBLE PRECISION,
  precip_prob    DOUBLE PRECISION,
  source         TEXT,
  observed_time  TIMESTAMPTZ,
  updated_at     TIMESTAMPTZ DEFAULT NOW(),
  
  FOREIGN KEY (game_id) REFERENCES hcl_test.games(game_id) ON DELETE CASCADE
);

COMMENT ON TABLE hcl_test.weather IS 'Weather conditions for outdoor games';

-- =============================================================================
-- MATERIALIZED VIEW 1: v_game_matchup_display (Base Analytics View)
-- =============================================================================
-- Purpose: Provide game-level view with home vs away stats side-by-side
-- Source: Joins games + team_game_stats (home) + team_game_stats (away)
-- Refresh: After data loads or on demand
-- =============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS hcl_test.v_game_matchup_display AS
SELECT 
  g.game_id,
  g.season,
  g.week,
  g.game_date,
  g.kickoff_time_utc,
  g.home_team,
  g.away_team,
  g.stadium,
  g.is_postseason,
  
  -- Home Team Stats
  h.points AS home_score,
  h.total_yards AS home_total_yards,
  h.passing_yards AS home_passing_yards,
  h.rushing_yards AS home_rushing_yards,
  h.turnovers AS home_turnovers,
  h.time_of_possession_sec AS home_top_sec,
  h.third_down_pct AS home_3rd_down_pct,
  h.red_zone_pct AS home_rz_pct,
  h.yards_per_play AS home_ypp,
  h.completion_pct AS home_comp_pct,
  
  -- Away Team Stats
  a.points AS away_score,
  a.total_yards AS away_total_yards,
  a.passing_yards AS away_passing_yards,
  a.rushing_yards AS away_rushing_yards,
  a.turnovers AS away_turnovers,
  a.time_of_possession_sec AS away_top_sec,
  a.third_down_pct AS away_3rd_down_pct,
  a.red_zone_pct AS away_rz_pct,
  a.yards_per_play AS away_ypp,
  a.completion_pct AS away_comp_pct,
  
  -- Game Result
  CASE 
    WHEN h.points > a.points THEN g.home_team
    WHEN a.points > h.points THEN g.away_team
    ELSE 'TIE'
  END AS winner
  
FROM hcl_test.games g
LEFT JOIN hcl_test.team_game_stats h ON g.game_id = h.game_id AND h.is_home = TRUE
LEFT JOIN hcl_test.team_game_stats a ON g.game_id = a.game_id AND a.is_home = FALSE
ORDER BY g.season DESC, g.week DESC, g.game_date DESC;

CREATE UNIQUE INDEX IF NOT EXISTS idx_vgmd_game_id ON hcl_test.v_game_matchup_display(game_id);

COMMENT ON MATERIALIZED VIEW hcl_test.v_game_matchup_display IS 'Game-level view with home vs away stats pivoted side-by-side';

-- =============================================================================
-- UTILITY FUNCTIONS
-- =============================================================================

-- Function to refresh materialized view
CREATE OR REPLACE FUNCTION hcl_test.refresh_matchup_views()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY hcl_test.v_game_matchup_display;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION hcl_test.refresh_matchup_views IS 'Refresh all materialized views after data loads';

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================
-- Run these after data loading to verify schema and data integrity

-- Query 1: Check table row counts
-- SELECT 'games' AS table_name, COUNT(*) AS row_count FROM hcl_test.games
-- UNION ALL
-- SELECT 'team_game_stats', COUNT(*) FROM hcl_test.team_game_stats
-- UNION ALL
-- SELECT 'betting_lines', COUNT(*) FROM hcl_test.betting_lines
-- UNION ALL
-- SELECT 'injuries', COUNT(*) FROM hcl_test.injuries
-- UNION ALL
-- SELECT 'weather', COUNT(*) FROM hcl_test.weather;

-- Query 2: Games by season
-- SELECT season, COUNT(*) AS game_count 
-- FROM hcl_test.games 
-- GROUP BY season 
-- ORDER BY season DESC;

-- Query 3: Team-game stats by season
-- SELECT season, COUNT(*) AS record_count 
-- FROM hcl_test.team_game_stats 
-- GROUP BY season 
-- ORDER BY season DESC;

-- Query 4: Test matchup view
-- SELECT game_id, home_team, away_team, home_score, away_score, winner
-- FROM hcl_test.v_game_matchup_display
-- WHERE season = 2024 AND week = 1
-- ORDER BY game_date;

-- =============================================================================
-- SCHEMA CREATION COMPLETE
-- =============================================================================
-- Next Steps:
-- 1. Run this SQL in testbed database (pgAdmin or psql)
-- 2. Verify tables created: SELECT table_name FROM information_schema.tables WHERE table_schema = 'hcl_test';
-- 3. Run historical data loader: python ingest_historical_games.py --testbed --seasons 2024
-- 4. Verify data loaded: Run verification queries above
-- 5. Refresh materialized view: SELECT hcl_test.refresh_matchup_views();
-- 6. If successful, migrate to production (use 'hcl' schema instead of 'hcl_test')
-- =============================================================================
