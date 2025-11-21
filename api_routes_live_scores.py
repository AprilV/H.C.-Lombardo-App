"""
Live Scores API - Fetches current week's games from ESPN with AI predictions
"""
from flask import Blueprint, jsonify
import requests
from datetime import datetime
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Team abbreviation mapping (ESPN to Database)
TEAM_ABBR_MAP = {
    'LAR': 'LA',  # ESPN uses LAR, database uses LA for Rams
}

def normalize_team_abbr(abbr):
    """Convert ESPN team abbreviation to database format"""
    return TEAM_ABBR_MAP.get(abbr, abbr)

def get_db_connection():
    """Connect to database"""
    db_name = os.getenv('DB_NAME', 'nfl_analytics')
    return psycopg2.connect(
        dbname=db_name,
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'aprilv120'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432')
    )

live_scores_api = Blueprint('live_scores_api', __name__)

ESPN_SCOREBOARD_URL = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"

def get_predictions_for_week(week, season=2025):
    """Fetch AI and Vegas predictions for a specific week"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
            SELECT 
                home_team,
                away_team,
                predicted_winner,
                ai_spread,
                vegas_spread,
                vegas_total
            FROM hcl.ml_predictions
            WHERE week = %s AND season = %s
        """
        
        cur.execute(query, (week, season))
        rows = cur.fetchall()
        
        print(f"DEBUG: Found {len(rows)} predictions for Week {week} Season {season}")
        
        # Create lookup dictionary by teams
        predictions = {}
        for row in rows:
            home_team, away_team, ai_winner, ai_spread, vegas_spread, vegas_total = row
            key = f"{away_team}@{home_team}"
            predictions[key] = {
                'ai_predicted_winner': ai_winner,
                'ai_spread': float(ai_spread) if ai_spread else None,
                'vegas_spread': float(vegas_spread) if vegas_spread else None,
                'vegas_total': float(vegas_total) if vegas_total else None
            }
            print(f"DEBUG: Added prediction {key} -> AI: {ai_winner}")
        
        print(f"DEBUG: Total predictions in dict: {len(predictions)}")
        
        cur.close()
        conn.close()
        
        return predictions
        
    except Exception as e:
        print(f"Error fetching predictions: {e}")
        return {}

@live_scores_api.route('/api/live-scores', methods=['GET'])
def get_live_scores():
    """Fetch current week's NFL games with live scores from ESPN"""
    try:
        # Fetch from ESPN API
        response = requests.get(ESPN_SCOREBOARD_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract games
        games = []
        week_info = None
        
        if 'week' in data and 'number' in data['week']:
            week_info = {
                'week': data['week']['number'],
                'season': data.get('season', {}).get('year', 2025)
            }
        
        # Fetch predictions if we have week info
        predictions = {}
        if week_info:
            predictions = get_predictions_for_week(week_info['week'], week_info['season'])
        
        for event in data.get('events', []):
            try:
                competition = event['competitions'][0]
                competitors = competition['competitors']
                
                # Get home and away teams
                home_team = next((c for c in competitors if c['homeAway'] == 'home'), None)
                away_team = next((c for c in competitors if c['homeAway'] == 'away'), None)
                
                if not home_team or not away_team:
                    continue
                
                # Get status
                status_type = competition['status']['type']['name'].lower()
                period = competition['status'].get('period', 0)
                clock = competition['status'].get('displayClock', '')
                
                # Map status
                if status_type in ['status_in_progress', 'status_halftime']:
                    if 'half' in status_type:
                        game_status = 'halftime'
                    else:
                        game_status = 'in_progress'
                elif status_type in ['status_final', 'status_end_period']:
                    game_status = 'final'
                else:
                    game_status = 'scheduled'
                
                # Get period text
                period_text = ''
                if game_status == 'in_progress':
                    if period == 1:
                        period_text = '1st Qtr'
                    elif period == 2:
                        period_text = '2nd Qtr'
                    elif period == 3:
                        period_text = '3rd Qtr'
                    elif period == 4:
                        period_text = '4th Qtr'
                    elif period > 4:
                        period_text = f'OT{period - 4}' if period > 5 else 'OT'
                
                # Get game time if scheduled
                game_time = ''
                game_date_str = ''
                if game_status == 'scheduled':
                    game_date = event.get('date', '')
                    if game_date:
                        try:
                            # Parse ISO datetime from ESPN
                            dt = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
                            # Format time in ET
                            game_time = dt.strftime('%I:%M %p ET')
                            # Format date
                            game_date_str = dt.strftime('%a %b %d')  # e.g., "Thu Nov 21"
                        except:
                            game_time = 'TBD'
                            game_date_str = ''
                
                game_data = {
                    'home_team': home_team['team']['abbreviation'],
                    'away_team': away_team['team']['abbreviation'],
                    'home_score': int(home_team.get('score', 0)),
                    'away_score': int(away_team.get('score', 0)),
                    'status': game_status,
                    'period': period_text,
                    'clock': clock,
                    'time': game_time,
                    'game_date': game_date_str,
                    'game_id': event.get('id', ''),
                }
                
                # Add AI prediction and Vegas data if available
                # Normalize team abbreviations for database lookup
                home_db = normalize_team_abbr(game_data['home_team'])
                away_db = normalize_team_abbr(game_data['away_team'])
                matchup_key = f"{away_db}@{home_db}"
                
                print(f"DEBUG: Looking for {matchup_key} in predictions (ESPN: {game_data['away_team']}@{game_data['home_team']})")
                
                if matchup_key in predictions:
                    pred = predictions[matchup_key]
                    game_data['ai_prediction'] = pred['ai_predicted_winner']
                    game_data['ai_spread'] = pred['ai_spread']
                    game_data['vegas_spread'] = pred['vegas_spread']
                    game_data['vegas_total'] = pred['vegas_total']
                    
                    # Determine if AI prediction was correct (only for final games)
                    if game_status == 'final':
                        if game_data['home_score'] > game_data['away_score']:
                            actual_winner = home_db
                        elif game_data['away_score'] > game_data['home_score']:
                            actual_winner = away_db
                        else:
                            actual_winner = 'TIE'
                        
                        game_data['ai_correct'] = (pred['ai_predicted_winner'] == actual_winner)
                    else:
                        game_data['ai_correct'] = None
                else:
                    game_data['ai_prediction'] = None
                    game_data['ai_spread'] = None
                    game_data['vegas_spread'] = None
                    game_data['vegas_total'] = None
                    game_data['ai_correct'] = None
                
                games.append(game_data)
                
            except Exception as e:
                print(f"Error parsing game: {e}")
                continue
        
        # Sort games: live first, then final, then scheduled
        def sort_key(game):
            if game['status'] == 'in_progress':
                return 0
            elif game['status'] == 'halftime':
                return 1
            elif game['status'] == 'final':
                return 2
            else:
                return 3
        
        games.sort(key=sort_key)
        
        return jsonify({
            'success': True,
            'games': games,
            'week_info': week_info,
            'total_games': len(games),
            'timestamp': datetime.now().isoformat()
        })
        
    except requests.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch from ESPN API: {str(e)}',
            'games': [],
            'week_info': None
        }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'games': [],
            'week_info': None
        }), 500
