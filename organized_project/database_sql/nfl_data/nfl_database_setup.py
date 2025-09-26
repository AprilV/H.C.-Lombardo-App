#!/usr/bin/env python3
"""
NFL Betting Line Predictor Database Setup
Creates SQLite database with tables for teams, games, stats, and betting lines
"""

import sqlite3
import os
from datetime import datetime

class NFLDatabase:
    def __init__(self, db_name="sports_betting.db"):
        """Initialize the NFL betting database"""
        self.db_name = db_name
        self.conn = None
        
    def connect(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            print(f"✓ Connected to database: {self.db_name}")
            return self.conn
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return None
    
    def create_tables(self):
        """Create all required tables for the NFL betting predictor"""
        if not self.conn:
            print("Error: No database connection")
            return False
            
        try:
            cursor = self.conn.cursor()
            
            # 1. Teams table
            print("Creating Teams table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Teams (
                    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    abbreviation VARCHAR(5) NOT NULL UNIQUE,
                    division VARCHAR(20) NOT NULL,
                    conference VARCHAR(10) NOT NULL,
                    city VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT chk_conference CHECK (conference IN ('AFC', 'NFC'))
                )
            ''')
            
            # 2. Games table
            print("Creating Games table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Games (
                    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    week INTEGER NOT NULL,
                    season INTEGER NOT NULL,
                    home_team_id INTEGER NOT NULL,
                    away_team_id INTEGER NOT NULL,
                    game_date DATE NOT NULL,
                    game_time TIME,
                    home_score INTEGER DEFAULT 0,
                    away_score INTEGER DEFAULT 0,
                    game_status VARCHAR(20) DEFAULT 'Scheduled',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (home_team_id) REFERENCES Teams(team_id),
                    FOREIGN KEY (away_team_id) REFERENCES Teams(team_id),
                    CONSTRAINT chk_week CHECK (week BETWEEN 1 AND 22),
                    CONSTRAINT chk_season CHECK (season >= 2020),
                    CONSTRAINT chk_different_teams CHECK (home_team_id != away_team_id)
                )
            ''')
            
            # 3. TeamStats table
            print("Creating TeamStats table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS TeamStats (
                    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER NOT NULL,
                    team_id INTEGER NOT NULL,
                    offense_yards INTEGER DEFAULT 0,
                    defense_yards INTEGER DEFAULT 0,
                    turnovers INTEGER DEFAULT 0,
                    passing_yards INTEGER DEFAULT 0,
                    rushing_yards INTEGER DEFAULT 0,
                    first_downs INTEGER DEFAULT 0,
                    third_down_conversions INTEGER DEFAULT 0,
                    third_down_attempts INTEGER DEFAULT 0,
                    red_zone_conversions INTEGER DEFAULT 0,
                    red_zone_attempts INTEGER DEFAULT 0,
                    penalties INTEGER DEFAULT 0,
                    penalty_yards INTEGER DEFAULT 0,
                    time_of_possession TIME,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES Games(game_id) ON DELETE CASCADE,
                    FOREIGN KEY (team_id) REFERENCES Teams(team_id),
                    UNIQUE(game_id, team_id)
                )
            ''')
            
            # 4. BettingLines table
            print("Creating BettingLines table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS BettingLines (
                    line_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER NOT NULL,
                    spread REAL NOT NULL,
                    total REAL NOT NULL,
                    home_moneyline INTEGER,
                    away_moneyline INTEGER,
                    user_formula_applied BOOLEAN DEFAULT FALSE,
                    prediction_confidence REAL,
                    sportsbook VARCHAR(50),
                    line_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES Games(game_id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes for better performance
            print("Creating indexes...")
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_season_week ON Games(season, week)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_date ON Games(game_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_teamstats_game ON TeamStats(game_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_bettinglines_game ON BettingLines(game_id)')
            
            self.conn.commit()
            print("✓ All tables created successfully!")
            return True
            
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
            self.conn.rollback()
            return False
    
    def insert_sample_data(self):
        """Insert sample data for testing"""
        if not self.conn:
            print("Error: No database connection")
            return False
            
        try:
            cursor = self.conn.cursor()
            
            # Sample teams
            print("Inserting sample teams...")
            teams_data = [
                ('Kansas City Chiefs', 'KC', 'AFC West', 'AFC', 'Kansas City'),
                ('Buffalo Bills', 'BUF', 'AFC East', 'AFC', 'Buffalo'),
                ('Dallas Cowboys', 'DAL', 'NFC East', 'NFC', 'Dallas'),
                ('San Francisco 49ers', 'SF', 'NFC West', 'NFC', 'San Francisco'),
                ('New England Patriots', 'NE', 'AFC East', 'AFC', 'New England'),
                ('Green Bay Packers', 'GB', 'NFC North', 'NFC', 'Green Bay'),
            ]
            
            cursor.executemany('''
                INSERT OR IGNORE INTO Teams (name, abbreviation, division, conference, city)
                VALUES (?, ?, ?, ?, ?)
            ''', teams_data)
            
            # Sample game
            print("Inserting sample game...")
            cursor.execute('''
                INSERT INTO Games (week, season, home_team_id, away_team_id, game_date, game_time)
                VALUES (1, 2024, 1, 2, '2024-09-07', '20:20')
            ''')
            game_id = cursor.lastrowid
            
            # Sample team stats
            print("Inserting sample team stats...")
            stats_data = [
                (game_id, 1, 350, 280, 1, 250, 100, 18, 6, 10, 2, 3, 5, 45),  # Home team stats
                (game_id, 2, 320, 350, 2, 200, 120, 16, 4, 12, 1, 2, 7, 65),  # Away team stats
            ]
            
            cursor.executemany('''
                INSERT INTO TeamStats (
                    game_id, team_id, offense_yards, defense_yards, turnovers,
                    passing_yards, rushing_yards, first_downs, third_down_conversions,
                    third_down_attempts, red_zone_conversions, red_zone_attempts,
                    penalties, penalty_yards
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', stats_data)
            
            # Sample betting line
            print("Inserting sample betting line...")
            cursor.execute('''
                INSERT INTO BettingLines (
                    game_id, spread, total, home_moneyline, away_moneyline,
                    sportsbook, prediction_confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (game_id, -3.5, 47.5, -180, +150, 'DraftKings', 0.75))
            
            self.conn.commit()
            print("✓ Sample data inserted successfully!")
            return True
            
        except sqlite3.Error as e:
            print(f"Error inserting sample data: {e}")
            self.conn.rollback()
            return False
    
    def get_database_info(self):
        """Display information about the database"""
        if not self.conn:
            print("Error: No database connection")
            return
            
        try:
            cursor = self.conn.cursor()
            
            print("\n" + "="*50)
            print("DATABASE INFORMATION")
            print("="*50)
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"Database: {self.db_name}")
            print(f"Tables: {len(tables)}")
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  - {table_name}: {count} records")
            
            # Show sample data
            print(f"\nSample Teams:")
            cursor.execute("SELECT name, abbreviation, conference FROM Teams LIMIT 3")
            teams = cursor.fetchall()
            for team in teams:
                print(f"  - {team[0]} ({team[1]}) - {team[2]}")
                
        except sqlite3.Error as e:
            print(f"Error getting database info: {e}")
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")

def main():
    """Main function to set up the NFL betting database"""
    print("NFL Betting Line Predictor Database Setup")
    print("="*50)
    
    # Initialize database
    nfl_db = NFLDatabase("sports_betting.db")
    
    # Connect to database
    if not nfl_db.connect():
        return
    
    # Create tables
    if nfl_db.create_tables():
        print("\n✓ Database schema created successfully!")
        
        # Insert sample data
        if nfl_db.insert_sample_data():
            print("✓ Sample data inserted!")
            
            # Show database info
            nfl_db.get_database_info()
    
    # Close connection
    nfl_db.close()
    
    print(f"\n✓ Database setup complete!")
    print(f"Database file: {os.path.abspath('sports_betting.db')}")

if __name__ == "__main__":
    main()