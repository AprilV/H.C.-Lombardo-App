#!/usr/bin/env python3
"""
Enhanced NFL Database Utilities
Advanced utilities for working with the user-specified schema:
🗃️ Teams | 🏈 Games | 📊 TeamStats | 💰 BettingLines
"""

import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple, Union
import json

class EnhancedNFLDatabaseManager:
    """Enhanced database manager for the user-specified schema"""
    
    def __init__(self, db_path="enhanced_nfl_betting.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    # 🗃️ TEAMS TABLE OPERATIONS
    def add_team(self, name: str, abbreviation: str, conference: str, 
                 division: str, **kwargs) -> int:
        """Add a new team with enhanced details"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build dynamic INSERT based on provided kwargs
            base_fields = ['name', 'abbreviation', 'conference', 'division']
            base_values = [name, abbreviation, conference, division]
            
            optional_fields = ['city', 'logo_url', 'primary_color', 'secondary_color', 
                             'founded_year', 'stadium_name', 'stadium_capacity', 'head_coach']
            
            extra_fields = []
            extra_values = []
            
            for field in optional_fields:
                if field in kwargs:
                    extra_fields.append(field)
                    extra_values.append(kwargs[field])
            
            all_fields = base_fields + extra_fields
            all_values = base_values + extra_values
            placeholders = ', '.join(['?'] * len(all_fields))
            
            cursor.execute(f'''
                INSERT INTO Teams ({', '.join(all_fields)})
                VALUES ({placeholders})
            ''', all_values)
            return cursor.lastrowid
    
    def get_teams(self, conference: str = None, division: str = None) -> List[sqlite3.Row]:
        """Get teams with optional filtering"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            base_query = '''
                SELECT team_id, name, abbreviation, conference, division, city,
                       stadium_name, stadium_capacity, head_coach, founded_year
                FROM Teams
            '''
            
            conditions = []
            params = []
            
            if conference:
                conditions.append('conference = ?')
                params.append(conference)
            
            if division:
                conditions.append('division = ?')
                params.append(division)
            
            if conditions:
                base_query += ' WHERE ' + ' AND '.join(conditions)
            
            base_query += ' ORDER BY conference, division, name'
            
            cursor.execute(base_query, params)
            return cursor.fetchall()
    
    def get_team_by_id(self, team_id: int) -> Optional[sqlite3.Row]:
        """Get team by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM Teams WHERE team_id = ?', (team_id,))
            return cursor.fetchone()
    
    # 🏈 GAMES TABLE OPERATIONS
    def add_game(self, week: int, season: int, home_team_id: int, 
                 away_team_id: int, date: str, **kwargs) -> int:
        """Add a new game with enhanced details"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            base_fields = ['week', 'season', 'home_team_id', 'away_team_id', 'date']
            base_values = [week, season, home_team_id, away_team_id, date]
            
            optional_fields = ['time', 'score_home', 'score_away', 'game_status',
                             'weather_conditions', 'temperature', 'wind_speed',
                             'is_playoff_game', 'attendance', 'tv_network']
            
            extra_fields = []
            extra_values = []
            
            for field in optional_fields:
                if field in kwargs:
                    extra_fields.append(field)
                    extra_values.append(kwargs[field])
            
            all_fields = base_fields + extra_fields
            all_values = base_values + extra_values
            placeholders = ', '.join(['?'] * len(all_fields))
            
            cursor.execute(f'''
                INSERT INTO Games ({', '.join(all_fields)})
                VALUES ({placeholders})
            ''', all_values)
            return cursor.lastrowid
    
    def get_games(self, season: int = None, week: int = None, 
                  team_id: int = None) -> List[sqlite3.Row]:
        """Get games with optional filtering"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            base_query = '''
                SELECT g.game_id, g.week, g.season, g.date, g.time,
                       g.score_home, g.score_away, g.game_status,
                       g.weather_conditions, g.temperature, g.attendance,
                       ht.name as home_team, ht.abbreviation as home_abbr,
                       at.name as away_team, at.abbreviation as away_abbr
                FROM Games g
                JOIN Teams ht ON g.home_team_id = ht.team_id
                JOIN Teams at ON g.away_team_id = at.team_id
            '''
            
            conditions = []
            params = []
            
            if season:
                conditions.append('g.season = ?')
                params.append(season)
            
            if week:
                conditions.append('g.week = ?')
                params.append(week)
            
            if team_id:
                conditions.append('(g.home_team_id = ? OR g.away_team_id = ?)')
                params.extend([team_id, team_id])
            
            if conditions:
                base_query += ' WHERE ' + ' AND '.join(conditions)
            
            base_query += ' ORDER BY g.date DESC, g.time DESC'
            
            cursor.execute(base_query, params)
            return cursor.fetchall()
    
    def update_game_score(self, game_id: int, score_home: int, score_away: int):
        """Update game score and set status to Final"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE Games 
                SET score_home = ?, score_away = ?, game_status = 'Final',
                    updated_at = CURRENT_TIMESTAMP
                WHERE game_id = ?
            ''', (score_home, score_away, game_id))
            conn.commit()
    
    # 📊 TEAMSTATS TABLE OPERATIONS
    def add_team_stats(self, game_id: int, team_id: int, stats: Dict) -> int:
        """Add comprehensive team statistics for a game"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # All possible stat fields
            stat_fields = [
                'offense_yards', 'defense_yards', 'turnovers', 'passing_yards',
                'rushing_yards', 'first_downs', 'third_down_conversions',
                'third_down_attempts', 'fourth_down_conversions', 'fourth_down_attempts',
                'red_zone_conversions', 'red_zone_attempts', 'penalties', 'penalty_yards',
                'sacks', 'sack_yards', 'interceptions', 'fumbles_lost',
                'time_of_possession', 'completion_percentage', 'quarterback_rating',
                'rushing_average'
            ]
            
            # Build INSERT with provided stats
            fields = ['game_id', 'team_id'] + [f for f in stat_fields if f in stats]
            values = [game_id, team_id] + [stats[f] for f in stat_fields if f in stats]
            placeholders = ', '.join(['?'] * len(fields))
            
            cursor.execute(f'''
                INSERT INTO TeamStats ({', '.join(fields)})
                VALUES ({placeholders})
            ''', values)
            return cursor.lastrowid
    
    def get_team_stats(self, game_id: int = None, team_id: int = None) -> List[sqlite3.Row]:
        """Get team statistics with optional filtering"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            base_query = '''
                SELECT ts.*, t.name, t.abbreviation,
                       g.week, g.season, g.date
                FROM TeamStats ts
                JOIN Teams t ON ts.team_id = t.team_id
                JOIN Games g ON ts.game_id = g.game_id
            '''
            
            conditions = []
            params = []
            
            if game_id:
                conditions.append('ts.game_id = ?')
                params.append(game_id)
            
            if team_id:
                conditions.append('ts.team_id = ?')
                params.append(team_id)
            
            if conditions:
                base_query += ' WHERE ' + ' AND '.join(conditions)
            
            base_query += ' ORDER BY g.date DESC, g.week DESC'
            
            cursor.execute(base_query, params)
            return cursor.fetchall()
    
    # 💰 BETTINGLINES TABLE OPERATIONS
    def add_betting_line(self, game_id: int, spread: float, total: float,
                        formula_name: str = None, predicted_by_user: str = None,
                        **kwargs) -> int:
        """Add betting line with user prediction details"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            base_fields = ['game_id', 'spread', 'total']
            base_values = [game_id, spread, total]
            
            if formula_name:
                base_fields.append('formula_name')
                base_values.append(formula_name)
            
            if predicted_by_user:
                base_fields.append('predicted_by_user')
                base_values.append(predicted_by_user)
                base_fields.append('is_user_prediction')
                base_values.append(True)
            
            optional_fields = ['home_moneyline', 'away_moneyline', 'prediction_confidence',
                             'sportsbook', 'line_movement', 'opening_spread', 'opening_total',
                             'closing_spread', 'closing_total', 'algorithm_used', 'model_accuracy']
            
            extra_fields = []
            extra_values = []
            
            for field in optional_fields:
                if field in kwargs:
                    extra_fields.append(field)
                    extra_values.append(kwargs[field])
            
            all_fields = base_fields + extra_fields
            all_values = base_values + extra_values
            placeholders = ', '.join(['?'] * len(all_fields))
            
            cursor.execute(f'''
                INSERT INTO BettingLines ({', '.join(all_fields)})
                VALUES ({placeholders})
            ''', all_values)
            return cursor.lastrowid
    
    def get_betting_lines(self, game_id: int = None, predicted_by_user: str = None,
                         formula_name: str = None) -> List[sqlite3.Row]:
        """Get betting lines with optional filtering"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            base_query = '''
                SELECT bl.*, g.week, g.season, g.date,
                       ht.name as home_team, ht.abbreviation as home_abbr,
                       at.name as away_team, at.abbreviation as away_abbr,
                       g.score_home, g.score_away
                FROM BettingLines bl
                JOIN Games g ON bl.game_id = g.game_id
                JOIN Teams ht ON g.home_team_id = ht.team_id
                JOIN Teams at ON g.away_team_id = at.team_id
            '''
            
            conditions = []
            params = []
            
            if game_id:
                conditions.append('bl.game_id = ?')
                params.append(game_id)
            
            if predicted_by_user:
                conditions.append('bl.predicted_by_user = ?')
                params.append(predicted_by_user)
            
            if formula_name:
                conditions.append('bl.formula_name = ?')
                params.append(formula_name)
            
            if conditions:
                base_query += ' WHERE ' + ' AND '.join(conditions)
            
            base_query += ' ORDER BY bl.line_date DESC'
            
            cursor.execute(base_query, params)
            return cursor.fetchall()
    
    # 📈 ADVANCED ANALYTICS
    def get_user_prediction_accuracy(self, user_name: str) -> Dict:
        """Calculate prediction accuracy for a specific user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get completed games with user predictions
            cursor.execute('''
                SELECT bl.*, g.score_home, g.score_away, g.game_status
                FROM BettingLines bl
                JOIN Games g ON bl.game_id = g.game_id
                WHERE bl.predicted_by_user = ? AND g.game_status = 'Final'
                  AND g.score_home IS NOT NULL AND g.score_away IS NOT NULL
            ''', (user_name,))
            
            predictions = cursor.fetchall()
            
            if not predictions:
                return {"error": "No completed predictions found"}
            
            correct_spreads = 0
            correct_totals = 0
            total_predictions = len(predictions)
            
            for pred in predictions:
                actual_spread = pred['score_home'] - pred['score_away']
                predicted_spread_correct = (
                    (pred['spread'] < 0 and actual_spread > -pred['spread']) or
                    (pred['spread'] > 0 and actual_spread < -pred['spread'])
                )
                
                if predicted_spread_correct:
                    correct_spreads += 1
                
                actual_total = pred['score_home'] + pred['score_away']
                if (pred['total'] > actual_total and actual_total < pred['total']) or \
                   (pred['total'] < actual_total and actual_total > pred['total']):
                    correct_totals += 1
            
            return {
                "user": user_name,
                "total_predictions": total_predictions,
                "spread_accuracy": round(correct_spreads / total_predictions, 3),
                "total_accuracy": round(correct_totals / total_predictions, 3),
                "overall_accuracy": round((correct_spreads + correct_totals) / (total_predictions * 2), 3)
            }
    
    def get_team_performance_vs_spread(self, team_id: int, season: int) -> Dict:
        """Analyze team performance against the spread"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT g.game_id, g.score_home, g.score_away, 
                       g.home_team_id, g.away_team_id,
                       bl.spread, t.name, t.abbreviation
                FROM Games g
                JOIN BettingLines bl ON g.game_id = bl.game_id
                JOIN Teams t ON t.team_id = ?
                WHERE (g.home_team_id = ? OR g.away_team_id = ?)
                  AND g.season = ? AND g.game_status = 'Final'
                  AND g.score_home IS NOT NULL AND g.score_away IS NOT NULL
            ''', (team_id, team_id, team_id, season))
            
            games = cursor.fetchall()
            
            if not games:
                return {"error": "No completed games found"}
            
            ats_wins = 0
            total_games = len(games)
            
            for game in games:
                actual_margin = game['score_home'] - game['score_away']
                
                # Adjust spread based on home/away
                if game['home_team_id'] == team_id:
                    # Team is home, spread is from home perspective
                    cover_spread = actual_margin > game['spread']
                else:
                    # Team is away, flip the spread
                    cover_spread = -actual_margin > game['spread']
                
                if cover_spread:
                    ats_wins += 1
            
            team_info = games[0]  # Get team name from first game
            
            return {
                "team": team_info['name'],
                "abbreviation": team_info['abbreviation'],
                "season": season,
                "games_played": total_games,
                "ats_wins": ats_wins,
                "ats_losses": total_games - ats_wins,
                "ats_percentage": round(ats_wins / total_games, 3) if total_games > 0 else 0
            }
    
    def get_database_summary(self) -> Dict:
        """Get comprehensive database summary"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            summary = {}
            
            # Table counts
            tables = ['Teams', 'Games', 'TeamStats', 'BettingLines', 'UserPredictions', 'SeasonStats']
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                summary[f"{table.lower()}_count"] = cursor.fetchone()['count']
            
            # Latest season
            cursor.execute("SELECT MAX(season) as latest_season FROM Games")
            result = cursor.fetchone()
            summary['latest_season'] = result['latest_season'] if result['latest_season'] else 'N/A'
            
            # User prediction stats
            cursor.execute('''
                SELECT predicted_by_user, COUNT(*) as prediction_count
                FROM BettingLines 
                WHERE predicted_by_user IS NOT NULL
                GROUP BY predicted_by_user
                ORDER BY prediction_count DESC
            ''')
            user_predictions = cursor.fetchall()
            summary['top_predictors'] = [dict(row) for row in user_predictions]
            
            # Conference breakdown
            cursor.execute('''
                SELECT conference, COUNT(*) as team_count
                FROM Teams
                GROUP BY conference
            ''')
            conferences = cursor.fetchall()
            summary['conferences'] = [dict(row) for row in conferences]
            
            return summary

# Testing and demonstration functions
def demonstrate_enhanced_features():
    """Demonstrate the enhanced database features"""
    print("🔬 Enhanced NFL Database Features Demonstration")
    print("=" * 55)
    
    db = EnhancedNFLDatabaseManager()
    
    # Test teams functionality
    print("\n🗃️ TEAMS TABLE OPERATIONS")
    print("-" * 30)
    teams = db.get_teams(conference='AFC')
    print(f"AFC Teams: {len(teams)}")
    for team in teams[:3]:
        print(f"   {team['name']} ({team['abbreviation']}) - {team['division']}")
    
    # Test games functionality  
    print("\n🏈 GAMES TABLE OPERATIONS")
    print("-" * 30)
    games = db.get_games(season=2024, week=1)
    print(f"Week 1, 2024 Games: {len(games)}")
    for game in games:
        print(f"   {game['away_abbr']} @ {game['home_abbr']}: {game['score_away']}-{game['score_home']}")
    
    # Test team stats
    print("\n📊 TEAM STATISTICS")
    print("-" * 20)
    if games:
        stats = db.get_team_stats(game_id=games[0]['game_id'])
        print(f"Game {games[0]['game_id']} statistics: {len(stats)} records")
        for stat in stats:
            print(f"   {stat['abbreviation']}: {stat['offense_yards']} total yards, {stat['turnovers']} turnovers")
    
    # Test betting lines
    print("\n💰 BETTING LINES & PREDICTIONS")
    print("-" * 35)
    lines = db.get_betting_lines(predicted_by_user='H.C. Lombardo')
    print(f"H.C. Lombardo predictions: {len(lines)}")
    for line in lines:
        print(f"   {line['away_abbr']} @ {line['home_abbr']}: {line['spread']}, O/U {line['total']}")
        print(f"      Formula: {line['formula_name']}")
        print(f"      Confidence: {line['prediction_confidence']:.1%}")
    
    # Test analytics
    print("\n📈 ADVANCED ANALYTICS")
    print("-" * 25)
    
    # User accuracy
    accuracy = db.get_user_prediction_accuracy('H.C. Lombardo')
    if 'error' not in accuracy:
        print(f"Prediction Accuracy for {accuracy['user']}:")
        print(f"   Total Predictions: {accuracy['total_predictions']}")
        print(f"   Spread Accuracy: {accuracy['spread_accuracy']:.1%}")
        print(f"   Total Accuracy: {accuracy['total_accuracy']:.1%}")
        print(f"   Overall Accuracy: {accuracy['overall_accuracy']:.1%}")
    
    # Team ATS performance
    if teams:
        ats_performance = db.get_team_performance_vs_spread(teams[0]['team_id'], 2024)
        if 'error' not in ats_performance:
            print(f"\nAgainst the Spread - {ats_performance['team']}:")
            print(f"   ATS Record: {ats_performance['ats_wins']}-{ats_performance['ats_losses']}")
            print(f"   ATS Percentage: {ats_performance['ats_percentage']:.1%}")
    
    # Database summary
    print("\n🏆 DATABASE SUMMARY")
    print("-" * 20)
    summary = db.get_database_summary()
    print(f"Teams: {summary['teams_count']}")
    print(f"Games: {summary['games_count']}")
    print(f"Team Statistics: {summary['teamstats_count']}")
    print(f"Betting Lines: {summary['bettinglines_count']}")
    print(f"User Predictions: {summary['userpredictions_count']}")
    print(f"Season Stats: {summary['seasonstats_count']}")
    print(f"Latest Season: {summary['latest_season']}")
    
    if summary['top_predictors']:
        print("Top Predictors:")
        for predictor in summary['top_predictors'][:3]:
            print(f"   {predictor['predicted_by_user']}: {predictor['prediction_count']} predictions")

if __name__ == "__main__":
    demonstrate_enhanced_features()