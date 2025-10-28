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
        JSON array of teams with abbreviation, name, wins, losses, PPG, EPA
    """
    try:
        season = request.args.get('season', default=2025, type=int)
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                team,
                games_played,
                wins,
                losses,
                ROUND(avg_ppg_for::numeric, 1) as ppg,
                ROUND(avg_epa_offense::numeric, 3) as epa_per_play,
                ROUND(avg_success_rate_offense::numeric, 3) as success_rate,
                ROUND(avg_yards_per_play::numeric, 2) as yards_per_play
            FROM hcl.v_team_season_stats
            WHERE season = %s
            ORDER BY wins DESC, avg_epa_offense DESC
        """
        
        cur.execute(query, (season,))
        teams = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(teams),
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
        
        # Get season stats
        query = """
            SELECT 
                team,
                season,
                games_played,
                wins,
                losses,
                ROUND(avg_ppg_for::numeric, 1) as ppg,
                ROUND(avg_epa_offense::numeric, 3) as epa_per_play,
                ROUND(avg_success_rate_offense::numeric, 3) as success_rate,
                ROUND(avg_yards_per_play::numeric, 2) as yards_per_play,
                ROUND(avg_epa_offense::numeric, 3) as pass_epa,
                ROUND(avg_epa_offense::numeric, 3) as rush_epa,
                ROUND(avg_third_down_rate::numeric, 3) as third_down_rate,
                ROUND(avg_red_zone_efficiency::numeric, 3) as red_zone_efficiency,
                total_turnovers_lost as turnovers_lost,
                total_turnovers_gained as turnovers_gained,
                total_turnover_diff as turnover_differential,
                ROUND(avg_epa_home::numeric, 3) as home_epa,
                ROUND(avg_epa_away::numeric, 3) as away_epa
            FROM hcl.v_team_season_stats
            WHERE team = %s AND season = %s
        """
        
        cur.execute(query, (team_abbr, season))
        team_stats = cur.fetchone()
        
        if not team_stats:
            cur.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': f'Team {team_abbr} not found'
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
    Get game-by-game history for a specific team
    
    Args:
        team_abbr: Team abbreviation (e.g. 'BAL', 'KC')
    
    Query params:
        season: Filter by season (default: all)
        limit: Max games to return (default: 20)
    
    Returns:
        JSON array of games with stats, opponent, result
    """
    try:
        team_abbr = team_abbr.upper()
        season = request.args.get('season', default=2025, type=int)
        limit = request.args.get('limit', default=20, type=int)
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT 
                tgs.game_id,
                tgs.season,
                tgs.week,
                g.game_type,
                g.kickoff_time_utc,
                tgs.team,
                tgs.opponent,
                tgs.is_home,
                tgs.points_scored as team_points,
                tgs.points_allowed as opponent_points,
                tgs.won as result,
                ROUND(tgs.epa_per_play::numeric, 3) as epa_per_play,
                ROUND(tgs.success_rate::numeric, 3) as success_rate,
                ROUND(tgs.yards_per_play::numeric, 2) as yards_per_play,
                tgs.total_yards,
                tgs.passing_yards as pass_yards,
                tgs.rushing_yards as rush_yards,
                tgs.turnovers_lost,
                tgs.turnovers_gained,
                ROUND(tgs.third_down_rate::numeric, 3) as third_down_rate,
                ROUND(tgs.red_zone_efficiency::numeric, 3) as red_zone_efficiency
            FROM hcl.team_game_stats tgs
            JOIN hcl.games g ON tgs.game_id = g.game_id
            WHERE tgs.team = %s AND tgs.season = %s
            ORDER BY g.kickoff_time_utc DESC 
            LIMIT %s
        """
        
        cur.execute(query, (team_abbr, season, limit))
        games = cur.fetchall()
        
        cur.close()
        conn.close()
        
        if not games:
            return jsonify({
                'success': False,
                'error': f'No games found for team {team_abbr}'
            }), 404
        
        return jsonify({
            'success': True,
            'count': len(games),
            'team': team_abbr,
            'games': games
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
