#!/usr/bin/env python3
"""
NFL Betting Predictor Example
Demonstrates how to use the database for betting line predictions
"""

import sqlite3
from nfl_database_utils import NFLDatabaseManager
from datetime import datetime

class BettingPredictor:
    """Simple betting line predictor using database data"""
    
    def __init__(self, db_path="sports_betting.db"):
        self.db_manager = NFLDatabaseManager(db_path)
    
    def analyze_team_performance(self, team_id: int, season: int) -> dict:
        """Analyze team performance for the season"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get team's offensive and defensive stats
            cursor.execute('''
                SELECT 
                    AVG(ts.offense_yards) as avg_offense,
                    AVG(ts.defense_yards) as avg_defense,
                    AVG(ts.turnovers) as avg_turnovers,
                    AVG(ts.passing_yards) as avg_passing,
                    AVG(ts.rushing_yards) as avg_rushing,
                    COUNT(*) as games_played,
                    t.name, t.abbreviation
                FROM TeamStats ts
                JOIN Games g ON ts.game_id = g.game_id
                JOIN Teams t ON ts.team_id = t.team_id
                WHERE ts.team_id = ? AND g.season = ?
                GROUP BY ts.team_id, t.name, t.abbreviation
            ''', (team_id, season))
            
            result = cursor.fetchone()
            if result:
                return {
                    'team_name': result['name'],
                    'abbreviation': result['abbreviation'],
                    'avg_offense': round(result['avg_offense'] or 0, 1),
                    'avg_defense': round(result['avg_defense'] or 0, 1),
                    'avg_turnovers': round(result['avg_turnovers'] or 0, 1),
                    'avg_passing': round(result['avg_passing'] or 0, 1),
                    'avg_rushing': round(result['avg_rushing'] or 0, 1),
                    'games_played': result['games_played']
                }
            return None
    
    def predict_spread(self, home_team_id: int, away_team_id: int, season: int) -> dict:
        """Simple spread prediction based on team stats"""
        
        home_stats = self.analyze_team_performance(home_team_id, season)
        away_stats = self.analyze_team_performance(away_team_id, season)
        
        if not home_stats or not away_stats:
            return {'error': 'Insufficient data for prediction'}
        
        # Simple prediction algorithm (you can make this more sophisticated)
        home_advantage = 3.0  # Traditional home field advantage
        
        # Calculate offensive/defensive differentials
        home_off_diff = home_stats['avg_offense'] - away_stats['avg_defense']
        away_off_diff = away_stats['avg_offense'] - home_stats['avg_defense']
        
        # Simple spread calculation
        predicted_spread = (home_off_diff - away_off_diff) / 25.0 + home_advantage
        predicted_spread = round(predicted_spread * 2) / 2  # Round to nearest 0.5
        
        # Calculate total prediction
        predicted_total = (home_stats['avg_offense'] + away_stats['avg_offense']) / 15.0 + 42.0
        predicted_total = round(predicted_total * 2) / 2
        
        return {
            'home_team': home_stats['team_name'],
            'away_team': away_stats['team_name'],
            'predicted_spread': predicted_spread,
            'predicted_total': predicted_total,
            'home_stats': home_stats,
            'away_stats': away_stats,
            'confidence': min(0.95, max(0.55, abs(predicted_spread) / 10.0 + 0.6))
        }
    
    def get_upcoming_games(self, season: int, week: int) -> list:
        """Get upcoming games for prediction"""
        return self.db_manager.get_games_by_week(season, week)
    
    def add_prediction_to_database(self, game_id: int, spread: float, total: float, 
                                  confidence: float):
        """Add prediction to betting lines table"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO BettingLines (
                    game_id, spread, total, user_formula_applied, 
                    prediction_confidence, sportsbook
                ) VALUES (?, ?, ?, TRUE, ?, 'User Prediction')
            ''', (game_id, spread, total, confidence))
            conn.commit()
            return cursor.lastrowid

def main():
    """Demonstrate the betting predictor"""
    print("NFL Betting Line Predictor Demo")
    print("=" * 40)
    
    predictor = BettingPredictor()
    
    # Get teams for demonstration
    teams = predictor.db_manager.get_teams()
    print(f"Available teams: {len(teams)}")
    
    # Demo: Predict spread for Chiefs vs Bills
    kc_team = next((t for t in teams if t['abbreviation'] == 'KC'), None)
    buf_team = next((t for t in teams if t['abbreviation'] == 'BUF'), None)
    
    if kc_team and buf_team:
        print(f"\nPredicting: {buf_team['name']} @ {kc_team['name']}")
        
        prediction = predictor.predict_spread(
            home_team_id=kc_team['team_id'],
            away_team_id=buf_team['team_id'],
            season=2024
        )
        
        if 'error' not in prediction:
            print(f"\nPrediction Results:")
            print(f"  Spread: {kc_team['abbreviation']} {prediction['predicted_spread']:+.1f}")
            print(f"  Total: {prediction['predicted_total']:.1f}")
            print(f"  Confidence: {prediction['confidence']:.1%}")
            
            print(f"\nTeam Analysis:")
            print(f"  {prediction['home_team']}:")
            print(f"    Avg Offense: {prediction['home_stats']['avg_offense']} yards")
            print(f"    Avg Defense: {prediction['home_stats']['avg_defense']} yards allowed")
            print(f"  {prediction['away_team']}:")
            print(f"    Avg Offense: {prediction['away_stats']['avg_offense']} yards")
            print(f"    Avg Defense: {prediction['away_stats']['avg_defense']} yards allowed")
        else:
            print(f"Error: {prediction['error']}")
    
    # Show existing betting lines
    print(f"\nExisting Betting Lines:")
    games = predictor.get_upcoming_games(2024, 1)
    for game in games:
        lines = predictor.db_manager.get_betting_lines(game['game_id'])
        if lines:
            line = lines[0]  # Get most recent line
            print(f"  {game['away_abbr']} @ {game['home_abbr']}: "
                  f"Spread {line['spread']:+.1f}, Total {line['total']:.1f}")

if __name__ == "__main__":
    main()