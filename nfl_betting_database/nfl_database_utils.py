#!/usr/bin/env python3
"""
NFL Database Utilities
Helper functions for working with the NFL betting database
"""

import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple

class NFLDatabaseManager:
    """Utility class for NFL database operations"""
    
    def __init__(self, db_path="sports_betting.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def add_team(self, name: str, abbreviation: str, division: str, 
                 conference: str, city: str = None) -> int:
        """Add a new team to the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Teams (name, abbreviation, division, conference, city)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, abbreviation, division, conference, city))
            return cursor.lastrowid
    
    def add_game(self, week: int, season: int, home_team_id: int, 
                 away_team_id: int, game_date: str, game_time: str = None) -> int:
        """Add a new game to the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Games (week, season, home_team_id, away_team_id, game_date, game_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (week, season, home_team_id, away_team_id, game_date, game_time))
            return cursor.lastrowid
    
    def add_team_stats(self, game_id: int, team_id: int, stats: Dict) -> int:
        """Add team statistics for a game"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO TeamStats (
                    game_id, team_id, offense_yards, defense_yards, turnovers,
                    passing_yards, rushing_yards, first_downs, third_down_conversions,
                    third_down_attempts, red_zone_conversions, red_zone_attempts,
                    penalties, penalty_yards
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                game_id, team_id,
                stats.get('offense_yards', 0),
                stats.get('defense_yards', 0),
                stats.get('turnovers', 0),
                stats.get('passing_yards', 0),
                stats.get('rushing_yards', 0),
                stats.get('first_downs', 0),
                stats.get('third_down_conversions', 0),
                stats.get('third_down_attempts', 0),
                stats.get('red_zone_conversions', 0),
                stats.get('red_zone_attempts', 0),
                stats.get('penalties', 0),
                stats.get('penalty_yards', 0)
            ))
            return cursor.lastrowid
    
    def add_betting_line(self, game_id: int, spread: float, total: float,
                        home_moneyline: int = None, away_moneyline: int = None,
                        sportsbook: str = None) -> int:
        """Add betting line for a game"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO BettingLines (
                    game_id, spread, total, home_moneyline, away_moneyline, sportsbook
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (game_id, spread, total, home_moneyline, away_moneyline, sportsbook))
            return cursor.lastrowid
    
    def get_teams(self) -> List[sqlite3.Row]:
        """Get all teams"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT team_id, name, abbreviation, division, conference, city
                FROM Teams ORDER BY conference, division, name
            ''')
            return cursor.fetchall()
    
    def get_games_by_week(self, season: int, week: int) -> List[sqlite3.Row]:
        """Get all games for a specific week"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT g.game_id, g.week, g.season, g.game_date, g.game_time,
                       ht.name as home_team, ht.abbreviation as home_abbr,
                       at.name as away_team, at.abbreviation as away_abbr,
                       g.home_score, g.away_score, g.game_status
                FROM Games g
                JOIN Teams ht ON g.home_team_id = ht.team_id
                JOIN Teams at ON g.away_team_id = at.team_id
                WHERE g.season = ? AND g.week = ?
                ORDER BY g.game_date, g.game_time
            ''', (season, week))
            return cursor.fetchall()
    
    def get_team_stats(self, game_id: int) -> List[sqlite3.Row]:
        """Get team statistics for a specific game"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ts.*, t.name, t.abbreviation
                FROM TeamStats ts
                JOIN Teams t ON ts.team_id = t.team_id
                WHERE ts.game_id = ?
            ''', (game_id,))
            return cursor.fetchall()
    
    def get_betting_lines(self, game_id: int) -> List[sqlite3.Row]:
        """Get betting lines for a specific game"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT bl.*, g.week, g.season,
                       ht.abbreviation as home_team,
                       at.abbreviation as away_team
                FROM BettingLines bl
                JOIN Games g ON bl.game_id = g.game_id
                JOIN Teams ht ON g.home_team_id = ht.team_id
                JOIN Teams at ON g.away_team_id = at.team_id
                WHERE bl.game_id = ?
                ORDER BY bl.line_date DESC
            ''', (game_id,))
            return cursor.fetchall()
    
    def update_game_score(self, game_id: int, home_score: int, away_score: int):
        """Update game score"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE Games 
                SET home_score = ?, away_score = ?, game_status = 'Final'
                WHERE game_id = ?
            ''', (home_score, away_score, game_id))
            conn.commit()
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Count records in each table
            tables = ['Teams', 'Games', 'TeamStats', 'BettingLines']
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table.lower()] = cursor.fetchone()[0]
            
            # Get latest season
            cursor.execute("SELECT MAX(season) FROM Games")
            result = cursor.fetchone()
            stats['latest_season'] = result[0] if result[0] else 'N/A'
            
            return stats

# Example usage and testing functions
def test_database_operations():
    """Test various database operations"""
    print("Testing NFL Database Operations")
    print("=" * 40)
    
    db_manager = NFLDatabaseManager()
    
    # Test getting teams
    print("Teams in database:")
    teams = db_manager.get_teams()
    for team in teams[:5]:  # Show first 5 teams
        print(f"  {team['name']} ({team['abbreviation']}) - {team['conference']} {team['division']}")
    
    # Test getting games
    print(f"\nGames for Week 1, 2024:")
    games = db_manager.get_games_by_week(2024, 1)
    for game in games:
        print(f"  {game['away_abbr']} @ {game['home_abbr']} - {game['game_date']}")
    
    # Test database stats
    print(f"\nDatabase Statistics:")
    stats = db_manager.get_database_stats()
    for key, value in stats.items():
        print(f"  {key.title()}: {value}")

if __name__ == "__main__":
    test_database_operations()