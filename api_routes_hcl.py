"""
HCL Historical Data API Routes
Flask endpoints for team statistics and game history
"""

from flask import Blueprint, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection - Use environment variable for database name
# Defaults to production database (nfl_analytics)
def get_db_connection():
    """Connect to HCL historical data database"""
    db_name = os.getenv('DB_NAME', 'nfl_analytics')  # Default to production
    return psycopg2.connect(
        dbname=db_name,
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'aprilv120'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432')
    )

# Create blueprint
hcl_bp = Blueprint('hcl', __name__, url_prefix='/api/hcl')

@hcl_bp.route('/teams', methods=['GET'])
def get_teams():
    """
    Get list of all NFL teams with basic season stats
    
    Query params:
        season: Season year (default: 2025)
    
    Returns:
        JSON array of teams with abbreviation, name, wins, losses, PPG, yards
    """
    try:
        season = request.args.get('season', default=2025, type=int)
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Aggregate stats from team_game_stats table with team names
        query = """
            SELECT 
                tgs.team,
                t.name as team_name,
                COUNT(*) as games_played,
                SUM(CASE WHEN tgs.result = 'W' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN tgs.result = 'L' THEN 1 ELSE 0 END) as losses,
                SUM(CASE WHEN tgs.result = 'T' THEN 1 ELSE 0 END) as ties,
                ROUND(AVG(tgs.points)::numeric, 1) as ppg,
                ROUND(AVG(tgs.total_yards)::numeric, 1) as yards_per_game,
                ROUND(AVG(tgs.yards_per_play)::numeric, 2) as yards_per_play,
                ROUND(AVG(tgs.completion_pct)::numeric, 1) as completion_pct,
                SUM(tgs.turnovers) as total_turnovers
            FROM hcl.team_game_stats tgs
            LEFT JOIN public.teams t ON tgs.team = t.abbreviation
            WHERE tgs.season = %s
            GROUP BY tgs.team, t.name
            ORDER BY wins DESC, ppg DESC
        """
        
        cur.execute(query, (season,))
        teams = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(teams),
            'season': season,
            'teams': teams
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/teams/<team_abbr>', methods=['GET'])
def get_team_details(team_abbr):
    """
    Get detailed season statistics for a specific team
    
    Args:
        team_abbr: Team abbreviation (e.g. 'BAL', 'KC')
    
    Query params:
        season: Filter by season (default: current/latest)
    
    Returns:
        JSON with team stats, home/away splits, recent form
    """
    try:
        team_abbr = team_abbr.upper()
        season = request.args.get('season', default=2025, type=int)
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get season stats from team_game_stats - ALL AVAILABLE STATS
        query = """
            SELECT 
                team,
                season,
                COUNT(*) as games_played,
                SUM(CASE WHEN result = 'W' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN result = 'L' THEN 1 ELSE 0 END) as losses,
                SUM(CASE WHEN result = 'T' THEN 1 ELSE 0 END) as ties,
                
                -- Scoring
                ROUND(AVG(points)::numeric, 1) as ppg,
                SUM(points) as total_points,
                ROUND(AVG(touchdowns)::numeric, 1) as touchdowns_per_game,
                ROUND(AVG(field_goals_made)::numeric, 1) as fg_per_game,
                ROUND(AVG(field_goals_att)::numeric, 1) as fg_att_per_game,
                
                -- Offensive Stats
                ROUND(AVG(total_yards)::numeric, 1) as total_yards_per_game,
                ROUND(AVG(passing_yards)::numeric, 1) as passing_yards_per_game,
                ROUND(AVG(rushing_yards)::numeric, 1) as rushing_yards_per_game,
                ROUND(AVG(plays)::numeric, 1) as plays_per_game,
                ROUND(AVG(yards_per_play)::numeric, 2) as yards_per_play,
                
                -- Passing Stats
                ROUND(AVG(completions)::numeric, 1) as completions_per_game,
                ROUND(AVG(passing_att)::numeric, 1) as passing_att_per_game,
                ROUND(AVG(completion_pct)::numeric, 1) as completion_pct,
                ROUND(AVG(passing_tds)::numeric, 1) as passing_tds_per_game,
                ROUND(AVG(interceptions)::numeric, 1) as interceptions_per_game,
                ROUND(AVG(sacks_taken)::numeric, 1) as sacks_taken_per_game,
                ROUND(AVG(sack_yards_lost)::numeric, 1) as sack_yards_lost_per_game,
                ROUND(AVG(qb_rating)::numeric, 1) as qb_rating,
                
                -- Rushing Stats
                ROUND(AVG(rushing_att)::numeric, 1) as rushing_att_per_game,
                ROUND(AVG(yards_per_carry)::numeric, 2) as yards_per_carry,
                ROUND(AVG(rushing_tds)::numeric, 1) as rushing_tds_per_game,
                
                -- Efficiency Metrics
                ROUND(AVG(third_down_pct)::numeric, 1) as third_down_pct,
                ROUND(AVG(fourth_down_pct)::numeric, 1) as fourth_down_pct,
                ROUND(AVG(red_zone_pct)::numeric, 1) as red_zone_pct,
                
                -- Special Teams
                ROUND(AVG(punt_count)::numeric, 1) as punts_per_game,
                ROUND(AVG(punt_avg_yards)::numeric, 1) as punt_avg_yards,
                ROUND(AVG(kickoff_return_yards)::numeric, 1) as kickoff_return_yards_per_game,
                ROUND(AVG(punt_return_yards)::numeric, 1) as punt_return_yards_per_game,
                
                -- Defense/Turnovers
                SUM(turnovers) as total_turnovers,
                ROUND(AVG(turnovers)::numeric, 1) as turnovers_per_game,
                ROUND(AVG(fumbles_lost)::numeric, 1) as fumbles_lost_per_game,
                ROUND(AVG(penalties)::numeric, 1) as penalties_per_game,
                ROUND(AVG(penalty_yards)::numeric, 1) as penalty_yards_per_game,
                
                -- Time of Possession
                ROUND(AVG(time_of_possession_pct)::numeric, 1) as time_of_possession_pct,
                
                -- Advanced Metrics
                ROUND(AVG(drives)::numeric, 1) as drives_per_game,
                ROUND(AVG(early_down_success_rate)::numeric, 1) as early_down_success_rate,
                ROUND(AVG(starting_field_pos_yds)::numeric, 1) as starting_field_pos_yds,
                
                -- Home/Away splits
                ROUND(AVG(CASE WHEN is_home THEN points END)::numeric, 1) as ppg_home,
                ROUND(AVG(CASE WHEN NOT is_home THEN points END)::numeric, 1) as ppg_away,
                SUM(CASE WHEN is_home AND result = 'W' THEN 1 ELSE 0 END) as home_wins,
                SUM(CASE WHEN NOT is_home AND result = 'W' THEN 1 ELSE 0 END) as away_wins
            FROM hcl.team_game_stats
            WHERE team = %s AND season = %s
            GROUP BY team, season
        """
        
        cur.execute(query, (team_abbr, season))
        team_stats = cur.fetchone()
        
        if not team_stats:
            cur.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': f'Team {team_abbr} not found for season {season}'
            }), 404
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'team': team_stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/teams/<team_abbr>/games', methods=['GET'])
def get_team_games(team_abbr):
    """
    Get full season schedule for a specific team (both completed and upcoming games)
    
    Args:
        team_abbr: Team abbreviation (e.g. 'BAL', 'KC')
    
    Query params:
        season: Filter by season (default: 2025)
        limit: Max games to return (default: 20)
    
    Returns:
        JSON array of games with stats for completed games, schedule info for upcoming
    """
    try:
        team_abbr = team_abbr.upper()
        season = request.args.get('season', default=2025, type=int)
        limit = request.args.get('limit', default=18, type=int)  # Changed default to 18 for full season
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query to get all scheduled games (from hcl.games) and join with stats where available
        query = """
            SELECT 
                g.game_id,
                g.season,
                g.week,
                g.game_date,
                CASE WHEN g.home_team = %s THEN g.home_team ELSE g.away_team END as team,
                CASE WHEN g.home_team = %s THEN g.away_team ELSE g.home_team END as opponent,
                CASE WHEN g.home_team = %s THEN TRUE ELSE FALSE END as is_home,
                -- Scores (NULL for upcoming games)
                g.home_score,
                g.away_score,
                CASE WHEN g.home_team = %s THEN g.home_score ELSE g.away_score END as team_points,
                -- Result (NULL for upcoming games)
                tgs.result,
                -- Team stats (NULL for upcoming games)
                tgs.total_yards,
                tgs.passing_yards,
                tgs.rushing_yards,
                ROUND(tgs.yards_per_play::numeric, 2) as yards_per_play,
                ROUND(tgs.completion_pct::numeric, 1) as completion_pct,
                tgs.turnovers,
                ROUND(tgs.third_down_pct::numeric, 1) as third_down_pct,
                -- Betting lines
                g.spread_line,
                g.total_line,
                g.home_moneyline,
                g.away_moneyline,
                -- Weather
                g.roof,
                g.temp,
                g.wind,
                -- Context
                CASE WHEN g.home_team = %s THEN g.home_rest ELSE g.away_rest END as rest_days,
                g.is_divisional_game,
                g.referee
            FROM hcl.games g
            LEFT JOIN hcl.team_game_stats tgs ON g.game_id = tgs.game_id AND tgs.team = %s
            WHERE (g.home_team = %s OR g.away_team = %s) AND g.season = %s
            ORDER BY g.week ASC
            LIMIT %s
        """
        
        cur.execute(query, (team_abbr, team_abbr, team_abbr, team_abbr, team_abbr, team_abbr, team_abbr, team_abbr, season, limit))
        games = cur.fetchall()
        
        cur.close()
        conn.close()
        
        if not games:
            return jsonify({
                'success': False,
                'error': f'No games found for team {team_abbr} in season {season}'
            }), 404
        
        return jsonify({
            'success': True,
            'count': len(games),
            'team': team_abbr,
            'season': season,
            'games': games
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/games/<game_id>', methods=['GET'])
def get_game_details(game_id):
    """
    Get complete game details including betting lines and weather
    
    Args:
        game_id: Game ID (format: YYYY_WW_AWAY_HOME)
    
    Returns:
        JSON with complete game info, team stats, betting lines, weather
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get game info with betting/weather
        query = """
            SELECT 
                g.game_id,
                g.season,
                g.week,
                g.game_date,
                g.home_team,
                g.away_team,
                g.home_score,
                g.away_score,
                g.stadium,
                -- Betting lines
                g.spread_line,
                g.total_line,
                g.home_moneyline,
                g.away_moneyline,
                g.home_spread_odds,
                g.away_spread_odds,
                g.over_odds,
                g.under_odds,
                -- Weather
                g.roof,
                g.surface,
                g.temp,
                g.wind,
                -- Context
                g.away_rest,
                g.home_rest,
                g.is_divisional_game,
                g.overtime,
                g.referee,
                g.away_coach,
                g.home_coach,
                g.away_qb_name,
                g.home_qb_name
            FROM hcl.games g
            WHERE g.game_id = %s
        """
        
        cur.execute(query, (game_id,))
        game = cur.fetchone()
        
        if not game:
            cur.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': f'Game {game_id} not found'
            }), 404
        
        # Get team stats for this game
        cur.execute("""
            SELECT 
                team,
                is_home,
                points,
                total_yards,
                passing_yards,
                rushing_yards,
                turnovers,
                ROUND(yards_per_play::numeric, 2) as yards_per_play,
                ROUND(completion_pct::numeric, 1) as completion_pct,
                ROUND(third_down_pct::numeric, 1) as third_down_pct,
                result
            FROM hcl.team_game_stats
            WHERE game_id = %s
            ORDER BY is_home DESC
        """, (game_id,))
        
        team_stats = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'game': game,
            'team_stats': team_stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/games/week/<int:season>/<int:week>', methods=['GET'])
def get_week_games(season, week):
    """
    Get all games for a specific week with betting lines
    
    Args:
        season: Season year
        week: Week number
    
    Returns:
        JSON array of games with scores, betting lines, weather
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                game_id,
                season,
                week,
                game_date,
                away_team,
                home_team,
                away_score,
                home_score,
                spread_line,
                total_line,
                home_moneyline,
                away_moneyline,
                roof,
                temp,
                wind,
                is_divisional_game,
                referee
            FROM hcl.games
            WHERE season = %s AND week = %s
            ORDER BY game_date, game_id
        """
        
        cur.execute(query, (season, week))
        games = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'season': season,
            'week': week,
            'count': len(games),
            'games': games
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# FEATURE ENGINEERING VIEW ENDPOINTS
# ============================================================================

@hcl_bp.route('/analytics/betting', methods=['GET'])
def get_betting_performance():
    """
    Get team betting performance (ATS records, O/U trends)
    
    Query params:
        season: Filter by season (default: 2025)
        team: Filter by specific team (optional)
    
    Returns:
        JSON with ATS records, over/under performance, favorite/underdog splits
    """
    try:
        season = request.args.get('season', default=2025, type=int)
        team = request.args.get('team', type=str)
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                team,
                season,
                total_games,
                ats_wins,
                ats_losses,
                ats_pushes,
                ats_win_pct,
                games_over,
                games_under,
                games_push,
                over_pct,
                games_as_favorite,
                wins_as_favorite,
                games_as_underdog,
                wins_as_underdog
            FROM hcl.v_team_betting_performance
            WHERE season = %s
        """
        
        params = [season]
        
        if team:
            query += " AND team = %s"
            params.append(team.upper())
        
        query += " ORDER BY ats_win_pct DESC"
        
        cur.execute(query, params)
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        if not results:
            return jsonify({
                'success': False,
                'error': f'No betting data found for season {season}'
            }), 404
        
        return jsonify({
            'success': True,
            'season': season,
            'count': len(results),
            'teams': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/analytics/weather', methods=['GET'])
def get_weather_impact():
    """
    Get weather impact on scoring and performance
    
    Query params:
        season: Filter by season (optional)
        roof: Filter by roof type (outdoors/dome/closed/open) (optional)
    
    Returns:
        JSON with scoring averages by weather conditions
    """
    try:
        season = request.args.get('season', type=int)
        roof = request.args.get('roof', type=str)
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                roof,
                surface,
                temp_range,
                wind_range,
                season,
                total_games,
                avg_total_points,
                avg_home_score,
                avg_away_score,
                avg_total_yards,
                avg_passing_yards,
                avg_rushing_yards,
                avg_completion_pct,
                avg_yards_per_play,
                highest_scoring_game,
                lowest_scoring_game,
                games_over,
                games_under,
                over_pct
            FROM hcl.v_weather_impact_analysis
            WHERE 1=1
        """
        
        params = []
        
        if season:
            query += " AND season = %s"
            params.append(season)
        
        if roof:
            query += " AND roof = %s"
            params.append(roof.lower())
        
        query += " ORDER BY avg_total_points DESC"
        
        cur.execute(query, params)
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'No weather data found'
            }), 404
        
        return jsonify({
            'success': True,
            'count': len(results),
            'conditions': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/analytics/rest', methods=['GET'])
def get_rest_advantage():
    """
    Get team performance by days of rest
    
    Query params:
        season: Filter by season (default: 2025)
    
    Returns:
        JSON with win rates and performance by rest days
    """
    try:
        season = request.args.get('season', default=2025, type=int)
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                rest_days,
                rest_category,
                season,
                total_games,
                wins,
                losses,
                ties,
                win_pct,
                avg_points_scored,
                avg_total_yards,
                avg_passing_yards,
                avg_rushing_yards,
                avg_turnovers,
                avg_yards_per_play,
                home_games,
                away_games,
                home_win_pct,
                away_win_pct
            FROM hcl.v_rest_advantage
            WHERE season = %s
            ORDER BY rest_days
        """
        
        cur.execute(query, (season,))
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        if not results:
            return jsonify({
                'success': False,
                'error': f'No rest data found for season {season}'
            }), 404
        
        return jsonify({
            'success': True,
            'season': season,
            'count': len(results),
            'rest_categories': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/analytics/referees', methods=['GET'])
def get_referee_tendencies():
    """
    Get referee officiating patterns and tendencies
    
    Query params:
        season: Filter by season (default: 2025)
        referee: Filter by specific referee name (optional)
    
    Returns:
        JSON with referee stats, home bias, scoring averages
    """
    try:
        season = request.args.get('season', default=2025, type=int)
        referee = request.args.get('referee', type=str)
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                referee,
                season,
                total_games,
                home_wins,
                away_wins,
                ties,
                home_win_pct,
                avg_total_points,
                avg_home_score,
                avg_away_score,
                avg_point_differential,
                highest_scoring_game,
                lowest_scoring_game,
                overtime_games,
                overtime_pct,
                avg_turnovers_per_game,
                divisional_games,
                games_over,
                games_under,
                over_pct
            FROM hcl.v_referee_tendencies
            WHERE season = %s
        """
        
        params = [season]
        
        if referee:
            query += " AND referee ILIKE %s"
            params.append(f"%{referee}%")
        
        query += " ORDER BY total_games DESC"
        
        cur.execute(query, params)
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        if not results:
            return jsonify({
                'success': False,
                'error': f'No referee data found for season {season}'
            }), 404
        
        return jsonify({
            'success': True,
            'season': season,
            'count': len(results),
            'referees': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@hcl_bp.route('/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """
    Get summary statistics from all analytical views
    
    Query params:
        season: Filter by season (default: 2025)
    
    Returns:
        JSON with key insights from betting, weather, rest, and referee data
    """
    try:
        season = request.args.get('season', default=2025, type=int)
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Best ATS team
        cur.execute("""
            SELECT team, ats_wins, ats_losses, ats_win_pct
            FROM hcl.v_team_betting_performance
            WHERE season = %s
            ORDER BY ats_win_pct DESC
            LIMIT 1
        """, (season,))
        best_ats = cur.fetchone()
        
        # Weather impact summary
        cur.execute("""
            SELECT roof, 
                   ROUND(AVG(avg_total_points)::numeric, 1) as avg_ppg,
                   COUNT(*) as conditions
            FROM hcl.v_weather_impact_analysis
            WHERE season = %s
            GROUP BY roof
            ORDER BY avg_ppg DESC
        """, (season,))
        weather_summary = cur.fetchall()
        
        # Rest advantage summary
        cur.execute("""
            SELECT rest_category,
                   SUM(total_games) as games,
                   ROUND(AVG(win_pct)::numeric, 1) as avg_win_pct
            FROM hcl.v_rest_advantage
            WHERE season = %s
            GROUP BY rest_category
            ORDER BY avg_win_pct DESC
            LIMIT 1
        """, (season,))
        best_rest = cur.fetchone()
        
        # Top referee
        cur.execute("""
            SELECT referee, total_games, home_win_pct
            FROM hcl.v_referee_tendencies
            WHERE season = %s
            ORDER BY total_games DESC
            LIMIT 1
        """, (season,))
        top_referee = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'season': season,
            'summary': {
                'best_ats_team': best_ats,
                'weather_impact': weather_summary,
                'best_rest_advantage': best_rest,
                'most_games_referee': top_referee
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
