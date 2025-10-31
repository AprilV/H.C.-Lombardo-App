-- ============================================================================
-- HCL FEATURE ENGINEERING VIEWS
-- H.C. Lombardo NFL Analytics App
-- Created: October 30, 2025
-- ============================================================================
-- 
-- These views transform raw game data into analytical insights:
-- 1. v_team_betting_performance - ATS records, O/U performance
-- 2. v_weather_impact_analysis - Scoring by weather conditions
-- 3. v_rest_advantage - Win rates by rest days
-- 4. v_referee_tendencies - Penalty patterns by official
--
-- Usage: Query these views like regular tables
-- Example: SELECT * FROM hcl.v_team_betting_performance WHERE team = 'BAL';
--
-- ============================================================================

-- ============================================================================
-- VIEW 1: Team Betting Performance
-- ============================================================================
-- Calculates each team's record against the spread (ATS) and over/under (O/U)
-- 
-- Use cases:
-- - Identify teams that consistently cover the spread
-- - Find teams that go over/under more often
-- - Analyze betting trends by season or situation
-- ============================================================================

CREATE OR REPLACE VIEW hcl.v_team_betting_performance AS
SELECT 
    tgs.team,
    tgs.season,
    COUNT(*) as total_games,
    
    -- Against The Spread (ATS) Performance
    SUM(CASE 
        WHEN tgs.is_home AND (g.home_score - g.away_score) > ABS(g.spread_line) AND g.spread_line < 0 THEN 1
        WHEN tgs.is_home AND (g.home_score - g.away_score) < ABS(g.spread_line) AND g.spread_line > 0 THEN 1
        WHEN NOT tgs.is_home AND (g.away_score - g.home_score) > ABS(g.spread_line) AND g.spread_line > 0 THEN 1
        WHEN NOT tgs.is_home AND (g.away_score - g.home_score) < ABS(g.spread_line) AND g.spread_line < 0 THEN 1
        ELSE 0
    END) as ats_wins,
    
    SUM(CASE 
        WHEN tgs.is_home AND (g.home_score - g.away_score) < ABS(g.spread_line) AND g.spread_line < 0 THEN 1
        WHEN tgs.is_home AND (g.home_score - g.away_score) > ABS(g.spread_line) AND g.spread_line > 0 THEN 1
        WHEN NOT tgs.is_home AND (g.away_score - g.home_score) < ABS(g.spread_line) AND g.spread_line > 0 THEN 1
        WHEN NOT tgs.is_home AND (g.away_score - g.home_score) > ABS(g.spread_line) AND g.spread_line < 0 THEN 1
        ELSE 0
    END) as ats_losses,
    
    SUM(CASE 
        WHEN ABS((g.home_score + g.away_score) - g.spread_line) <= 0.5 THEN 1
        ELSE 0
    END) as ats_pushes,
    
    -- Over/Under Performance
    SUM(CASE 
        WHEN (g.home_score + g.away_score) > g.total_line THEN 1
        ELSE 0
    END) as games_over,
    
    SUM(CASE 
        WHEN (g.home_score + g.away_score) < g.total_line THEN 1
        ELSE 0
    END) as games_under,
    
    SUM(CASE 
        WHEN ABS((g.home_score + g.away_score) - g.total_line) <= 0.5 THEN 1
        ELSE 0
    END) as games_push,
    
    -- Favorite/Underdog Splits
    SUM(CASE 
        WHEN (tgs.is_home AND g.spread_line < 0) OR (NOT tgs.is_home AND g.spread_line > 0) THEN 1
        ELSE 0
    END) as games_as_favorite,
    
    SUM(CASE 
        WHEN ((tgs.is_home AND g.spread_line < 0) OR (NOT tgs.is_home AND g.spread_line > 0)) AND tgs.result = 'W' THEN 1
        ELSE 0
    END) as wins_as_favorite,
    
    SUM(CASE 
        WHEN (tgs.is_home AND g.spread_line > 0) OR (NOT tgs.is_home AND g.spread_line < 0) THEN 1
        ELSE 0
    END) as games_as_underdog,
    
    SUM(CASE 
        WHEN ((tgs.is_home AND g.spread_line > 0) OR (NOT tgs.is_home AND g.spread_line < 0)) AND tgs.result = 'W' THEN 1
        ELSE 0
    END) as wins_as_underdog,
    
    -- Calculated Percentages
    ROUND(
        SUM(CASE 
            WHEN tgs.is_home AND (g.home_score - g.away_score) > ABS(g.spread_line) AND g.spread_line < 0 THEN 1
            WHEN tgs.is_home AND (g.home_score - g.away_score) < ABS(g.spread_line) AND g.spread_line > 0 THEN 1
            WHEN NOT tgs.is_home AND (g.away_score - g.home_score) > ABS(g.spread_line) AND g.spread_line > 0 THEN 1
            WHEN NOT tgs.is_home AND (g.away_score - g.home_score) < ABS(g.spread_line) AND g.spread_line < 0 THEN 1
            ELSE 0
        END)::NUMERIC / NULLIF(COUNT(*), 0) * 100, 1
    ) as ats_win_pct,
    
    ROUND(
        SUM(CASE WHEN (g.home_score + g.away_score) > g.total_line THEN 1 ELSE 0 END)::NUMERIC / 
        NULLIF(COUNT(*), 0) * 100, 1
    ) as over_pct

FROM hcl.team_game_stats tgs
JOIN hcl.games g ON tgs.game_id = g.game_id
WHERE g.spread_line IS NOT NULL 
  AND g.total_line IS NOT NULL
  AND g.home_score IS NOT NULL
  AND g.away_score IS NOT NULL
GROUP BY tgs.team, tgs.season
ORDER BY tgs.season DESC, ats_win_pct DESC;

COMMENT ON VIEW hcl.v_team_betting_performance IS 
'Team betting performance metrics including ATS records, O/U trends, and favorite/underdog splits';


-- ============================================================================
-- VIEW 2: Weather Impact Analysis
-- ============================================================================
-- Analyzes how weather conditions affect scoring and performance
--
-- Use cases:
-- - Compare outdoor vs. dome scoring
-- - Identify temperature thresholds for offense
-- - Analyze wind impact on passing games
-- ============================================================================

CREATE OR REPLACE VIEW hcl.v_weather_impact_analysis AS
SELECT 
    g.roof,
    g.surface,
    CASE 
        WHEN g.temp IS NULL THEN 'Indoor'
        WHEN g.temp < 32 THEN 'Freezing (<32°F)'
        WHEN g.temp BETWEEN 32 AND 50 THEN 'Cold (32-50°F)'
        WHEN g.temp BETWEEN 51 AND 70 THEN 'Mild (51-70°F)'
        WHEN g.temp > 70 THEN 'Hot (>70°F)'
    END as temp_range,
    CASE 
        WHEN g.wind IS NULL THEN 'Indoor'
        WHEN g.wind < 5 THEN 'Calm (<5 MPH)'
        WHEN g.wind BETWEEN 5 AND 10 THEN 'Light (5-10 MPH)'
        WHEN g.wind BETWEEN 11 AND 15 THEN 'Moderate (11-15 MPH)'
        WHEN g.wind > 15 THEN 'High (>15 MPH)'
    END as wind_range,
    g.season,
    
    -- Game counts
    COUNT(*) as total_games,
    
    -- Scoring averages
    ROUND(AVG(g.home_score + g.away_score)::NUMERIC, 1) as avg_total_points,
    ROUND(AVG(g.home_score)::NUMERIC, 1) as avg_home_score,
    ROUND(AVG(g.away_score)::NUMERIC, 1) as avg_away_score,
    
    -- Offensive stats averages (from team_game_stats)
    ROUND(AVG(tgs.total_yards)::NUMERIC, 1) as avg_total_yards,
    ROUND(AVG(tgs.passing_yards)::NUMERIC, 1) as avg_passing_yards,
    ROUND(AVG(tgs.rushing_yards)::NUMERIC, 1) as avg_rushing_yards,
    ROUND(AVG(tgs.completion_pct)::NUMERIC, 1) as avg_completion_pct,
    ROUND(AVG(tgs.yards_per_play)::NUMERIC, 2) as avg_yards_per_play,
    
    -- High/low scoring games
    MAX(g.home_score + g.away_score) as highest_scoring_game,
    MIN(g.home_score + g.away_score) as lowest_scoring_game,
    
    -- Over/Under performance (when available)
    SUM(CASE WHEN (g.home_score + g.away_score) > g.total_line THEN 1 ELSE 0 END) as games_over,
    SUM(CASE WHEN (g.home_score + g.away_score) < g.total_line THEN 1 ELSE 0 END) as games_under,
    ROUND(
        SUM(CASE WHEN (g.home_score + g.away_score) > g.total_line THEN 1 ELSE 0 END)::NUMERIC / 
        NULLIF(COUNT(*), 0) * 100, 1
    ) as over_pct

FROM hcl.games g
LEFT JOIN hcl.team_game_stats tgs ON g.game_id = tgs.game_id
WHERE g.home_score IS NOT NULL 
  AND g.away_score IS NOT NULL
GROUP BY g.roof, g.surface, temp_range, wind_range, g.season
ORDER BY g.season DESC, avg_total_points DESC;

COMMENT ON VIEW hcl.v_weather_impact_analysis IS 
'Weather impact on scoring and performance by roof type, temperature, and wind conditions';


-- ============================================================================
-- VIEW 3: Rest Advantage Analysis
-- ============================================================================
-- Analyzes team performance based on days of rest
--
-- Use cases:
-- - Identify rest advantage in wins/losses
-- - Compare short week vs. bye week performance
-- - Analyze scoring patterns with different rest
-- ============================================================================

CREATE OR REPLACE VIEW hcl.v_rest_advantage AS
SELECT 
    CASE 
        WHEN tgs.is_home THEN g.home_rest
        ELSE g.away_rest
    END as rest_days,
    CASE 
        WHEN (CASE WHEN tgs.is_home THEN g.home_rest ELSE g.away_rest END) <= 4 THEN 'Short Week (3-4 days)'
        WHEN (CASE WHEN tgs.is_home THEN g.home_rest ELSE g.away_rest END) BETWEEN 5 AND 6 THEN 'Mini Bye (5-6 days)'
        WHEN (CASE WHEN tgs.is_home THEN g.home_rest ELSE g.away_rest END) = 7 THEN 'Normal Week (7 days)'
        WHEN (CASE WHEN tgs.is_home THEN g.home_rest ELSE g.away_rest END) BETWEEN 8 AND 13 THEN 'Extended Rest (8-13 days)'
        WHEN (CASE WHEN tgs.is_home THEN g.home_rest ELSE g.away_rest END) >= 14 THEN 'Bye Week (14+ days)'
    END as rest_category,
    tgs.season,
    
    -- Game counts
    COUNT(*) as total_games,
    
    -- Win/Loss records
    SUM(CASE WHEN tgs.result = 'W' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN tgs.result = 'L' THEN 1 ELSE 0 END) as losses,
    SUM(CASE WHEN tgs.result = 'T' THEN 1 ELSE 0 END) as ties,
    
    -- Win percentage
    ROUND(
        SUM(CASE WHEN tgs.result = 'W' THEN 1 ELSE 0 END)::NUMERIC / 
        NULLIF(COUNT(*), 0) * 100, 1
    ) as win_pct,
    
    -- Performance stats
    ROUND(AVG(tgs.points)::NUMERIC, 1) as avg_points_scored,
    ROUND(AVG(tgs.total_yards)::NUMERIC, 1) as avg_total_yards,
    ROUND(AVG(tgs.passing_yards)::NUMERIC, 1) as avg_passing_yards,
    ROUND(AVG(tgs.rushing_yards)::NUMERIC, 1) as avg_rushing_yards,
    ROUND(AVG(tgs.turnovers)::NUMERIC, 1) as avg_turnovers,
    ROUND(AVG(tgs.yards_per_play)::NUMERIC, 2) as avg_yards_per_play,
    
    -- Home/Away splits
    SUM(CASE WHEN tgs.is_home THEN 1 ELSE 0 END) as home_games,
    SUM(CASE WHEN NOT tgs.is_home THEN 1 ELSE 0 END) as away_games,
    ROUND(
        SUM(CASE WHEN tgs.is_home AND tgs.result = 'W' THEN 1 ELSE 0 END)::NUMERIC / 
        NULLIF(SUM(CASE WHEN tgs.is_home THEN 1 ELSE 0 END), 0) * 100, 1
    ) as home_win_pct,
    ROUND(
        SUM(CASE WHEN NOT tgs.is_home AND tgs.result = 'W' THEN 1 ELSE 0 END)::NUMERIC / 
        NULLIF(SUM(CASE WHEN NOT tgs.is_home THEN 1 ELSE 0 END), 0) * 100, 1
    ) as away_win_pct

FROM hcl.team_game_stats tgs
JOIN hcl.games g ON tgs.game_id = g.game_id
WHERE (CASE WHEN tgs.is_home THEN g.home_rest ELSE g.away_rest END) IS NOT NULL
GROUP BY rest_days, rest_category, tgs.season
ORDER BY tgs.season DESC, rest_days;

COMMENT ON VIEW hcl.v_rest_advantage IS 
'Team performance analysis by days of rest including win rates and scoring averages';


-- ============================================================================
-- VIEW 4: Referee Tendencies
-- ============================================================================
-- Analyzes referee patterns and potential biases
--
-- Use cases:
-- - Identify refs who call more/fewer penalties
-- - Detect home field bias in officiating
-- - Analyze scoring patterns by referee
-- ============================================================================

CREATE OR REPLACE VIEW hcl.v_referee_tendencies AS
SELECT 
    g.referee,
    g.season,
    
    -- Game counts
    COUNT(*) as total_games,
    
    -- Home/Away results
    SUM(CASE WHEN g.home_score > g.away_score THEN 1 ELSE 0 END) as home_wins,
    SUM(CASE WHEN g.home_score < g.away_score THEN 1 ELSE 0 END) as away_wins,
    SUM(CASE WHEN g.home_score = g.away_score THEN 1 ELSE 0 END) as ties,
    
    -- Home win percentage (potential bias indicator)
    ROUND(
        SUM(CASE WHEN g.home_score > g.away_score THEN 1 ELSE 0 END)::NUMERIC / 
        NULLIF(COUNT(*), 0) * 100, 1
    ) as home_win_pct,
    
    -- Scoring averages
    ROUND(AVG(g.home_score + g.away_score)::NUMERIC, 1) as avg_total_points,
    ROUND(AVG(g.home_score)::NUMERIC, 1) as avg_home_score,
    ROUND(AVG(g.away_score)::NUMERIC, 1) as avg_away_score,
    ROUND(AVG(g.home_score - g.away_score)::NUMERIC, 1) as avg_point_differential,
    
    -- High/low scoring games
    MAX(g.home_score + g.away_score) as highest_scoring_game,
    MIN(g.home_score + g.away_score) as lowest_scoring_game,
    
    -- Overtime games
    SUM(CASE WHEN g.overtime = 1 THEN 1 ELSE 0 END) as overtime_games,
    ROUND(
        SUM(CASE WHEN g.overtime = 1 THEN 1 ELSE 0 END)::NUMERIC / 
        NULLIF(COUNT(*), 0) * 100, 1
    ) as overtime_pct,
    
    -- Turnovers (combined from team_game_stats)
    ROUND(AVG(
        (SELECT SUM(turnovers) FROM hcl.team_game_stats WHERE game_id = g.game_id)
    )::NUMERIC, 1) as avg_turnovers_per_game,
    
    -- Divisional games (rivalry intensity)
    SUM(CASE WHEN g.is_divisional_game THEN 1 ELSE 0 END) as divisional_games,
    
    -- Over/Under performance (when betting lines available)
    SUM(CASE WHEN (g.home_score + g.away_score) > g.total_line THEN 1 ELSE 0 END) as games_over,
    SUM(CASE WHEN (g.home_score + g.away_score) < g.total_line THEN 1 ELSE 0 END) as games_under,
    ROUND(
        SUM(CASE WHEN (g.home_score + g.away_score) > g.total_line THEN 1 ELSE 0 END)::NUMERIC / 
        NULLIF(COUNT(*), 0) * 100, 1
    ) as over_pct

FROM hcl.games g
WHERE g.referee IS NOT NULL
  AND g.home_score IS NOT NULL
  AND g.away_score IS NOT NULL
GROUP BY g.referee, g.season
HAVING COUNT(*) >= 3  -- Only include refs with at least 3 games
ORDER BY g.season DESC, total_games DESC;

COMMENT ON VIEW hcl.v_referee_tendencies IS 
'Referee officiating patterns including scoring averages, home bias, and overtime rates';


-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these to verify views were created successfully
-- ============================================================================

-- Check that all views exist
SELECT 
    schemaname,
    viewname,
    viewowner
FROM pg_views
WHERE schemaname = 'hcl'
  AND viewname LIKE 'v_%'
ORDER BY viewname;

-- Sample data from each view
SELECT 'v_team_betting_performance' as view_name, COUNT(*) as row_count 
FROM hcl.v_team_betting_performance
UNION ALL
SELECT 'v_weather_impact_analysis', COUNT(*) 
FROM hcl.v_weather_impact_analysis
UNION ALL
SELECT 'v_rest_advantage', COUNT(*) 
FROM hcl.v_rest_advantage
UNION ALL
SELECT 'v_referee_tendencies', COUNT(*) 
FROM hcl.v_referee_tendencies;

-- ============================================================================
-- SAMPLE USAGE EXAMPLES
-- ============================================================================

-- Example 1: Best teams against the spread in 2025
-- SELECT team, total_games, ats_wins, ats_losses, ats_win_pct
-- FROM hcl.v_team_betting_performance
-- WHERE season = 2025
-- ORDER BY ats_win_pct DESC
-- LIMIT 10;

-- Example 2: How does scoring change in dome vs outdoor stadiums?
-- SELECT roof, AVG(avg_total_points) as avg_ppg, COUNT(*) as conditions
-- FROM hcl.v_weather_impact_analysis
-- GROUP BY roof
-- ORDER BY avg_ppg DESC;

-- Example 3: Do teams with bye weeks perform better?
-- SELECT rest_category, win_pct, avg_points_scored, total_games
-- FROM hcl.v_rest_advantage
-- WHERE season = 2025
-- ORDER BY rest_days;

-- Example 4: Which referees have the highest home win percentage?
-- SELECT referee, total_games, home_win_pct, avg_total_points
-- FROM hcl.v_referee_tendencies
-- WHERE season = 2025
-- ORDER BY home_win_pct DESC
-- LIMIT 10;

-- ============================================================================
-- END OF FILE
-- ============================================================================
