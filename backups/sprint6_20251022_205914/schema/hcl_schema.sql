-- ============================================================================
-- HC Lombardo - Historical Data Schema (hcl)
-- Sprint 5-6: Historical Game Analytics & Team Performance Tracking
-- ============================================================================
-- Purpose: Store NFL play-by-play aggregated stats for betting analytics
-- Tables: games, team_game_stats
-- Views: v_game_matchup_display, v_game_matchup_with_proj, v_team_season_stats
-- Data Source: nflverse (via nfl-data-py)
-- ============================================================================

-- Create schema
CREATE SCHEMA IF NOT EXISTS hcl;
SET search_path = hcl, public;

-- ============================================================================
-- TABLE: hcl.games
-- ============================================================================
-- Stores game metadata (schedule, teams, scores, location)
-- One row per game (home + away in single row)
-- ============================================================================

CREATE TABLE IF NOT EXISTS hcl.games (
    -- Primary Key
    game_id TEXT PRIMARY KEY,  -- Format: 2024_08_KC_BUF
    
    -- Season/Week Information
    season INTEGER NOT NULL,
    week INTEGER,  -- NULL for playoffs
    game_type TEXT NOT NULL,  -- 'REG', 'WC', 'DIV', 'CONF', 'SB'
    
    -- Game Timing
    game_date DATE,
    kickoff_time_utc TIMESTAMP WITH TIME ZONE,
    
    -- Teams
    home_team TEXT NOT NULL,  -- 3-letter abbreviation (e.g., 'KC')
    away_team TEXT NOT NULL,
    
    -- Final Scores (NULL if game not played yet)
    home_score INTEGER,
    away_score INTEGER,
    
    -- Location
    stadium TEXT,
    city TEXT,
    state TEXT,
    
    -- Metadata
    is_postseason BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE hcl.games IS 'Game schedule and results - one row per game';
COMMENT ON COLUMN hcl.games.game_id IS 'Unique identifier: YYYY_WW_AWAY_HOME';
COMMENT ON COLUMN hcl.games.game_type IS 'REG=Regular, WC=Wild Card, DIV=Divisional, CONF=Conference, SB=Super Bowl';
COMMENT ON COLUMN hcl.games.kickoff_time_utc IS 'Game start time in UTC (for timezone-aware queries)';

-- ============================================================================
-- TABLE: hcl.team_game_stats
-- ============================================================================
-- Stores team-level performance stats for each game
-- Two rows per game (one for home team, one for away team)
-- Aggregated from play-by-play data (nflverse)
-- ============================================================================

CREATE TABLE IF NOT EXISTS hcl.team_game_stats (
    -- Composite Primary Key
    id SERIAL PRIMARY KEY,
    game_id TEXT NOT NULL REFERENCES hcl.games(game_id) ON DELETE CASCADE,
    team TEXT NOT NULL,  -- Which team these stats belong to
    
    -- Context
    season INTEGER NOT NULL,
    week INTEGER,
    opponent TEXT NOT NULL,
    is_home BOOLEAN NOT NULL,
    
    -- Game Result
    points_scored INTEGER,
    points_allowed INTEGER,
    won BOOLEAN,  -- TRUE if team won
    
    -- ========================================================================
    -- CORE EFFICIENCY METRICS (EPA-based)
    -- ========================================================================
    
    -- EPA (Expected Points Added) - THE key metric for betting
    epa_per_play NUMERIC(6,4),  -- Offensive EPA per play (higher = better offense)
    epa_per_play_defense NUMERIC(6,4),  -- Defensive EPA allowed per play (lower = better defense)
    
    -- Success Rate - % of plays that "succeed" (context-aware)
    success_rate NUMERIC(5,4),  -- Offensive success rate (0.50 = 50%)
    success_rate_defense NUMERIC(5,4),  -- Defensive success rate allowed
    
    -- ========================================================================
    -- BASIC OFFENSE STATS
    -- ========================================================================
    
    total_plays INTEGER,
    total_yards INTEGER,
    yards_per_play NUMERIC(5,2),
    
    passing_yards INTEGER,
    passing_attempts INTEGER,
    passing_completions INTEGER,
    passing_touchdowns INTEGER,
    interceptions INTEGER,
    
    rushing_yards INTEGER,
    rushing_attempts INTEGER,
    rushing_touchdowns INTEGER,
    
    first_downs INTEGER,
    third_down_attempts INTEGER,
    third_down_conversions INTEGER,
    third_down_rate NUMERIC(5,4),  -- Conversion rate (0.40 = 40%)
    
    fourth_down_attempts INTEGER,
    fourth_down_conversions INTEGER,
    fourth_down_rate NUMERIC(5,4),
    
    red_zone_attempts INTEGER,
    red_zone_scores INTEGER,
    red_zone_touchdowns INTEGER,
    red_zone_efficiency NUMERIC(5,4),  -- TD rate in red zone
    
    -- ========================================================================
    -- TURNOVERS & PENALTIES
    -- ========================================================================
    
    turnovers_lost INTEGER,  -- Interceptions + fumbles lost
    turnovers_gained INTEGER,  -- Defensive takeaways
    turnover_differential INTEGER,  -- gained - lost
    
    penalties INTEGER,
    penalty_yards INTEGER,
    
    -- ========================================================================
    -- SITUATIONAL STATS
    -- ========================================================================
    
    time_of_possession_seconds INTEGER,  -- Time of possession in seconds
    explosive_plays INTEGER,  -- Plays gaining 20+ yards
    
    -- ========================================================================
    -- MOMENTUM INDICATORS (Last 3 Games Rolling Averages)
    -- ========================================================================
    
    epa_last_3_games NUMERIC(6,4),  -- Avg EPA/play over last 3 games
    yards_per_play_last_3 NUMERIC(5,2),
    ppg_last_3_games NUMERIC(5,2),  -- Points per game, last 3
    
    -- ========================================================================
    -- SCORING BREAKDOWN
    -- ========================================================================
    
    touchdowns INTEGER,
    field_goals_made INTEGER,
    field_goals_attempted INTEGER,
    extra_points_made INTEGER,
    two_point_conversions INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(game_id, team)
);

COMMENT ON TABLE hcl.team_game_stats IS 'Team performance stats per game (2 rows per game)';
COMMENT ON COLUMN hcl.team_game_stats.epa_per_play IS 'Expected Points Added per play - KEY betting metric (0.20+ = elite offense)';
COMMENT ON COLUMN hcl.team_game_stats.success_rate IS 'Percentage of plays gaining "enough" yards (down/distance context)';
COMMENT ON COLUMN hcl.team_game_stats.epa_last_3_games IS 'Rolling 3-game average EPA - momentum indicator';
COMMENT ON COLUMN hcl.team_game_stats.turnover_differential IS 'Turnovers gained - turnovers lost (positive = good)';

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Query by season/week (for week selector)
CREATE INDEX IF NOT EXISTS idx_games_season_week ON hcl.games(season, week);

-- Query by kickoff time (for "next week" logic)
CREATE INDEX IF NOT EXISTS idx_games_kickoff ON hcl.games(kickoff_time_utc);

-- Query team stats by team (for team detail pages)
CREATE INDEX IF NOT EXISTS idx_team_stats_team ON hcl.team_game_stats(team);

-- Query team stats by season/week (for filtering)
CREATE INDEX IF NOT EXISTS idx_team_stats_season_week ON hcl.team_game_stats(season, week);

-- Query by game_id (for joining)
CREATE INDEX IF NOT EXISTS idx_team_stats_game_id ON hcl.team_game_stats(game_id);

-- ============================================================================
-- VIEW: v_team_season_stats
-- ============================================================================
-- Season-level aggregates per team (for team detail page overview)
-- ============================================================================

CREATE OR REPLACE VIEW hcl.v_team_season_stats AS
SELECT 
    team,
    season,
    
    -- Record
    COUNT(*) as games_played,
    SUM(CASE WHEN won THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN NOT won THEN 1 ELSE 0 END) as losses,
    
    -- Scoring
    AVG(points_scored) as avg_ppg_for,
    AVG(points_allowed) as avg_ppg_against,
    SUM(points_scored) as total_points_for,
    SUM(points_allowed) as total_points_against,
    
    -- EPA (Key Betting Metrics)
    AVG(epa_per_play) as avg_epa_offense,
    AVG(epa_per_play_defense) as avg_epa_defense,
    
    -- Success Rate
    AVG(success_rate) as avg_success_rate_offense,
    AVG(success_rate_defense) as avg_success_rate_defense,
    
    -- Efficiency
    AVG(yards_per_play) as avg_yards_per_play,
    AVG(third_down_rate) as avg_third_down_rate,
    AVG(red_zone_efficiency) as avg_red_zone_efficiency,
    
    -- Turnovers
    SUM(turnovers_lost) as total_turnovers_lost,
    SUM(turnovers_gained) as total_turnovers_gained,
    SUM(turnover_differential) as total_turnover_diff,
    
    -- Home/Away Splits
    AVG(CASE WHEN is_home THEN epa_per_play END) as avg_epa_home,
    AVG(CASE WHEN NOT is_home THEN epa_per_play END) as avg_epa_away,
    
    SUM(CASE WHEN is_home AND won THEN 1 ELSE 0 END) as home_wins,
    SUM(CASE WHEN is_home AND NOT won THEN 1 ELSE 0 END) as home_losses,
    SUM(CASE WHEN NOT is_home AND won THEN 1 ELSE 0 END) as away_wins,
    SUM(CASE WHEN NOT is_home AND NOT won THEN 1 ELSE 0 END) as away_losses

FROM hcl.team_game_stats
GROUP BY team, season;

COMMENT ON VIEW hcl.v_team_season_stats IS 'Season-level aggregates per team (for team detail pages)';

-- ============================================================================
-- VIEW: v_game_matchup_display
-- ============================================================================
-- Matchup view with home/away stats pivoted into single row per game
-- Used for week-by-week browsing and game comparisons
-- ============================================================================

CREATE OR REPLACE VIEW hcl.v_game_matchup_display AS
SELECT 
    g.game_id,
    g.season,
    g.week,
    g.game_type,
    g.game_date,
    g.kickoff_time_utc,
    
    -- Teams
    g.home_team,
    g.away_team,
    
    -- Scores
    g.home_score,
    g.away_score,
    
    -- Location
    g.stadium,
    g.city,
    g.state,
    
    -- Home Team Stats
    h.games_played as home_gp,
    h.points_scored as home_points,
    h.epa_per_play as home_epa_pp,
    h.success_rate as home_sr,
    h.yards_per_play as home_ypp,
    h.third_down_rate as home_3d_rate,
    h.red_zone_efficiency as home_rz_eff,
    h.turnovers_lost as home_to_lost,
    h.turnovers_gained as home_to_gained,
    h.turnover_differential as home_to_diff,
    
    -- Home Momentum (Last 3 Games)
    h.epa_last_3_games as home_epa_l3,
    h.yards_per_play_last_3 as home_ypp_l3,
    h.ppg_last_3_games as home_ppg_l3,
    
    -- Away Team Stats
    a.games_played as away_gp,
    a.points_scored as away_points,
    a.epa_per_play as away_epa_pp,
    a.success_rate as away_sr,
    a.yards_per_play as away_ypp,
    a.third_down_rate as away_3d_rate,
    a.red_zone_efficiency as away_rz_eff,
    a.turnovers_lost as away_to_lost,
    a.turnovers_gained as away_to_gained,
    a.turnover_differential as away_to_diff,
    
    -- Away Momentum (Last 3 Games)
    a.epa_last_3_games as away_epa_l3,
    a.yards_per_play_last_3 as away_ypp_l3,
    a.ppg_last_3_games as away_ppg_l3,
    
    -- Matchup Edges (Home - Away)
    (h.epa_per_play - a.epa_per_play) as diff_epa_pp,
    (h.success_rate - a.success_rate) as diff_sr,
    (h.yards_per_play - a.yards_per_play) as diff_ypp,
    (h.points_scored - a.points_scored) as diff_ppg

FROM hcl.games g

-- Join home team stats (season averages up to this game)
LEFT JOIN LATERAL (
    SELECT 
        COUNT(*) as games_played,
        AVG(points_scored) as points_scored,
        AVG(epa_per_play) as epa_per_play,
        AVG(success_rate) as success_rate,
        AVG(yards_per_play) as yards_per_play,
        AVG(third_down_rate) as third_down_rate,
        AVG(red_zone_efficiency) as red_zone_efficiency,
        AVG(turnovers_lost) as turnovers_lost,
        AVG(turnovers_gained) as turnovers_gained,
        AVG(turnover_differential) as turnover_differential,
        AVG(epa_last_3_games) as epa_last_3_games,
        AVG(yards_per_play_last_3) as yards_per_play_last_3,
        AVG(ppg_last_3_games) as ppg_last_3_games
    FROM hcl.team_game_stats
    WHERE team = g.home_team
      AND season = g.season
      AND (week < g.week OR g.week IS NULL)  -- Only games before this one
) h ON TRUE

-- Join away team stats (season averages up to this game)
LEFT JOIN LATERAL (
    SELECT 
        COUNT(*) as games_played,
        AVG(points_scored) as points_scored,
        AVG(epa_per_play) as epa_per_play,
        AVG(success_rate) as success_rate,
        AVG(yards_per_play) as yards_per_play,
        AVG(third_down_rate) as third_down_rate,
        AVG(red_zone_efficiency) as red_zone_efficiency,
        AVG(turnovers_lost) as turnovers_lost,
        AVG(turnovers_gained) as turnovers_gained,
        AVG(turnover_differential) as turnover_differential,
        AVG(epa_last_3_games) as epa_last_3_games,
        AVG(yards_per_play_last_3) as yards_per_play_last_3,
        AVG(ppg_last_3_games) as ppg_last_3_games
    FROM hcl.team_game_stats
    WHERE team = g.away_team
      AND season = g.season
      AND (week < g.week OR g.week IS NULL)
) a ON TRUE

WHERE g.game_type = 'REG'  -- Regular season only (filter postseason separately)
ORDER BY g.kickoff_time_utc DESC;

COMMENT ON VIEW hcl.v_game_matchup_display IS 'Matchup view with home/away stats in single row - for week browsing';

-- ============================================================================
-- VIEW: v_game_matchup_with_proj
-- ============================================================================
-- Extends matchup view with spread/total projections
-- Uses ChatGPT's baseline projection formulas
-- ============================================================================

CREATE OR REPLACE VIEW hcl.v_game_matchup_with_proj AS
SELECT 
    d.*,
    
    -- ========================================================================
    -- SPREAD PROJECTION
    -- Formula: -2.2 * diff_epa_pp - 8.0 * diff_sr - 1.2 (home field advantage)
    -- Negative spread = home favored
    -- ========================================================================
    
    (
        -2.2 * COALESCE(d.diff_epa_pp, 0) 
        - 8.0 * COALESCE(d.diff_sr, 0) 
        - 1.2  -- Home field advantage
    ) AS projected_spread,
    
    -- ========================================================================
    -- TOTAL PROJECTION
    -- Formula: (home_ppg + away_ppg) + 14.0 * (home_epa + away_epa)
    -- ========================================================================
    
    (
        COALESCE(d.home_points, 0) + COALESCE(d.away_points, 0)
        + 14.0 * (COALESCE(d.home_epa_pp, 0) + COALESCE(d.away_epa_pp, 0))
    ) AS projected_total,
    
    -- ========================================================================
    -- CONFIDENCE INDICATORS
    -- ========================================================================
    
    -- Spread confidence (based on differential magnitude)
    CASE 
        WHEN ABS(COALESCE(d.diff_epa_pp, 0)) > 0.15 THEN 'HIGH'
        WHEN ABS(COALESCE(d.diff_epa_pp, 0)) > 0.08 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS spread_confidence,
    
    -- Matchup strength
    CASE
        WHEN COALESCE(d.home_epa_pp, 0) > 0.15 AND COALESCE(d.away_epa_pp, 0) < 0 THEN 'HOME_MISMATCH'
        WHEN COALESCE(d.away_epa_pp, 0) > 0.15 AND COALESCE(d.home_epa_pp, 0) < 0 THEN 'AWAY_MISMATCH'
        WHEN COALESCE(d.home_epa_pp, 0) > 0.10 AND COALESCE(d.away_epa_pp, 0) > 0.10 THEN 'SHOOTOUT'
        WHEN COALESCE(d.home_epa_pp, 0) < 0 AND COALESCE(d.away_epa_pp, 0) < 0 THEN 'DEFENSIVE_BATTLE'
        ELSE 'EVEN_MATCHUP'
    END AS matchup_type

FROM hcl.v_game_matchup_display d;

COMMENT ON VIEW hcl.v_game_matchup_with_proj IS 'Matchup view with spread/total projections - for betting analytics';
COMMENT ON COLUMN hcl.v_game_matchup_with_proj.projected_spread IS 'Negative = home favored. Formula: -2.2*EPA_diff - 8.0*SR_diff - 1.2';
COMMENT ON COLUMN hcl.v_game_matchup_with_proj.projected_total IS 'Formula: PPG_sum + 14.0*(EPA_sum)';

-- ============================================================================
-- VALIDATION QUERIES
-- ============================================================================
-- Run these after loading data to verify schema works
-- ============================================================================

-- Check table row counts
-- SELECT 'games' as table_name, COUNT(*) as row_count FROM hcl.games
-- UNION ALL
-- SELECT 'team_game_stats', COUNT(*) FROM hcl.team_game_stats;

-- Check view works (should return matchups with stats)
-- SELECT * FROM hcl.v_game_matchup_display WHERE season = 2024 AND week = 7 LIMIT 5;

-- Check projections calculated
-- SELECT game_id, home_team, away_team, projected_spread, projected_total, matchup_type 
-- FROM hcl.v_game_matchup_with_proj 
-- WHERE season = 2024 AND week = 7 
-- LIMIT 5;

-- Check team season stats
-- SELECT * FROM hcl.v_team_season_stats WHERE season = 2024 AND team = 'KC';

-- ============================================================================
-- SCHEMA COMPLETE
-- ============================================================================
-- Next Steps:
-- 1. Run this file via setup_test_db.py or psql
-- 2. Load Week 7 data with enhanced nflverse_data_loader.py
-- 3. Run validation queries above
-- 4. Build Flask API endpoints for team detail pages
-- ============================================================================
