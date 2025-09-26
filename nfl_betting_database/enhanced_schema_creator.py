#!/usr/bin/env python3
"""
Enhanced NFL Database Schema
Implements the exact database structure requested by the user
"""

import sqlite3
import os
from datetime import datetime, date
from typing import List, Dict, Optional

class EnhancedNFLDatabase:
    """Enhanced NFL Database with user-specified schema"""
    
    def __init__(self, db_name="enhanced_nfl_betting.db"):
        """Initialize the enhanced NFL database"""
        self.db_name = db_name
        self.conn = None
        
    def connect(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
            print(f"✓ Connected to enhanced database: {self.db_name}")
            return self.conn
        except sqlite3.Error as e:
            print(f"❌ Error connecting to database: {e}")
            return None
    
    def create_enhanced_schema(self):
        """Create the enhanced database schema as specified"""
        if not self.conn:
            print("❌ Error: No database connection")
            return False
            
        try:
            cursor = self.conn.cursor()
            print("🗃️ Creating Enhanced NFL Database Schema...")
            print("=" * 50)
            
            # 🗃️ Teams Table (Exactly as specified)
            print("Creating 🗃️ Teams table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Teams (
                    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    abbreviation VARCHAR(5) NOT NULL UNIQUE,
                    conference VARCHAR(10) NOT NULL CHECK (conference IN ('AFC', 'NFC')),
                    division VARCHAR(20) NOT NULL,
                    city VARCHAR(50),
                    logo_url VARCHAR(200),
                    primary_color VARCHAR(7),
                    secondary_color VARCHAR(7),
                    founded_year INTEGER,
                    stadium_name VARCHAR(100),
                    stadium_capacity INTEGER,
                    head_coach VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 🏈 Games Table (Enhanced with your specifications)
            print("Creating 🏈 Games table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Games (
                    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    week INTEGER NOT NULL CHECK (week BETWEEN 1 AND 22),
                    season INTEGER NOT NULL CHECK (season >= 2020),
                    home_team_id INTEGER NOT NULL,
                    away_team_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    time TIME,
                    score_home INTEGER DEFAULT NULL,
                    score_away INTEGER DEFAULT NULL,
                    game_status VARCHAR(20) DEFAULT 'Scheduled',
                    weather_conditions VARCHAR(100),
                    temperature INTEGER,
                    wind_speed INTEGER,
                    is_playoff_game BOOLEAN DEFAULT FALSE,
                    attendance INTEGER,
                    tv_network VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (home_team_id) REFERENCES Teams(team_id),
                    FOREIGN KEY (away_team_id) REFERENCES Teams(team_id),
                    CONSTRAINT chk_different_teams CHECK (home_team_id != away_team_id),
                    UNIQUE(week, season, home_team_id, away_team_id)
                )
            ''')
            
            # 📊 TeamStats Table (Enhanced with comprehensive stats)
            print("Creating 📊 TeamStats table...")
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
                    fourth_down_conversions INTEGER DEFAULT 0,
                    fourth_down_attempts INTEGER DEFAULT 0,
                    red_zone_conversions INTEGER DEFAULT 0,
                    red_zone_attempts INTEGER DEFAULT 0,
                    penalties INTEGER DEFAULT 0,
                    penalty_yards INTEGER DEFAULT 0,
                    sacks INTEGER DEFAULT 0,
                    sack_yards INTEGER DEFAULT 0,
                    interceptions INTEGER DEFAULT 0,
                    fumbles_lost INTEGER DEFAULT 0,
                    time_of_possession TIME,
                    completion_percentage REAL,
                    quarterback_rating REAL,
                    rushing_average REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES Games(game_id) ON DELETE CASCADE,
                    FOREIGN KEY (team_id) REFERENCES Teams(team_id),
                    UNIQUE(game_id, team_id)
                )
            ''')
            
            # 💰 BettingLines Table (Enhanced with your specifications)
            print("Creating 💰 BettingLines table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS BettingLines (
                    line_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER NOT NULL,
                    spread REAL NOT NULL,
                    total REAL NOT NULL,
                    home_moneyline INTEGER,
                    away_moneyline INTEGER,
                    formula_name VARCHAR(100),
                    predicted_by_user VARCHAR(100),
                    prediction_confidence REAL CHECK (prediction_confidence BETWEEN 0 AND 1),
                    sportsbook VARCHAR(50),
                    line_movement REAL,
                    opening_spread REAL,
                    opening_total REAL,
                    closing_spread REAL,
                    closing_total REAL,
                    is_user_prediction BOOLEAN DEFAULT FALSE,
                    algorithm_used VARCHAR(100),
                    model_accuracy REAL,
                    line_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES Games(game_id) ON DELETE CASCADE
                )
            ''')
            
            # Additional Enhancement Tables
            
            # 🎯 UserPredictions Table (Track user predictions)
            print("Creating 🎯 UserPredictions table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS UserPredictions (
                    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER NOT NULL,
                    user_name VARCHAR(100) NOT NULL,
                    predicted_home_score INTEGER,
                    predicted_away_score INTEGER,
                    predicted_spread REAL,
                    predicted_total REAL,
                    confidence_level INTEGER CHECK (confidence_level BETWEEN 1 AND 10),
                    reasoning TEXT,
                    formula_used VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES Games(game_id) ON DELETE CASCADE
                )
            ''')
            
            # 📈 SeasonStats Table (Aggregate season statistics)
            print("Creating 📈 SeasonStats table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS SeasonStats (
                    season_stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id INTEGER NOT NULL,
                    season INTEGER NOT NULL,
                    games_played INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    ties INTEGER DEFAULT 0,
                    points_for INTEGER DEFAULT 0,
                    points_against INTEGER DEFAULT 0,
                    total_yards_for INTEGER DEFAULT 0,
                    total_yards_against INTEGER DEFAULT 0,
                    turnovers_forced INTEGER DEFAULT 0,
                    turnovers_committed INTEGER DEFAULT 0,
                    playoff_appearance BOOLEAN DEFAULT FALSE,
                    division_winner BOOLEAN DEFAULT FALSE,
                    conference_winner BOOLEAN DEFAULT FALSE,
                    super_bowl_winner BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (team_id) REFERENCES Teams(team_id),
                    UNIQUE(team_id, season)
                )
            ''')
            
            # Create Performance Indexes
            print("Creating performance indexes...")
            indexes = [
                'CREATE INDEX IF NOT EXISTS idx_games_season_week ON Games(season, week)',
                'CREATE INDEX IF NOT EXISTS idx_games_date ON Games(date)',
                'CREATE INDEX IF NOT EXISTS idx_games_teams ON Games(home_team_id, away_team_id)',
                'CREATE INDEX IF NOT EXISTS idx_teamstats_game_team ON TeamStats(game_id, team_id)',
                'CREATE INDEX IF NOT EXISTS idx_bettinglines_game ON BettingLines(game_id)',
                'CREATE INDEX IF NOT EXISTS idx_bettinglines_user ON BettingLines(predicted_by_user)',
                'CREATE INDEX IF NOT EXISTS idx_userpredictions_game ON UserPredictions(game_id)',
                'CREATE INDEX IF NOT EXISTS idx_userpredictions_user ON UserPredictions(user_name)',
                'CREATE INDEX IF NOT EXISTS idx_seasonstats_team_season ON SeasonStats(team_id, season)',
                'CREATE INDEX IF NOT EXISTS idx_teams_conference_division ON Teams(conference, division)'
            ]
            
            for index in indexes:
                cursor.execute(index)
            
            # Create Views for Common Queries
            print("Creating helpful database views...")
            
            # Game Summary View
            cursor.execute('''
                CREATE VIEW IF NOT EXISTS GameSummary AS
                SELECT 
                    g.game_id,
                    g.week,
                    g.season,
                    g.date,
                    ht.name as home_team,
                    ht.abbreviation as home_abbr,
                    at.name as away_team,
                    at.abbreviation as away_abbr,
                    g.score_home,
                    g.score_away,
                    g.game_status,
                    bl.spread,
                    bl.total,
                    bl.predicted_by_user
                FROM Games g
                JOIN Teams ht ON g.home_team_id = ht.team_id
                JOIN Teams at ON g.away_team_id = at.team_id
                LEFT JOIN BettingLines bl ON g.game_id = bl.game_id
            ''')
            
            # Team Performance View
            cursor.execute('''
                CREATE VIEW IF NOT EXISTS TeamPerformance AS
                SELECT 
                    t.team_id,
                    t.name,
                    t.abbreviation,
                    t.conference,
                    t.division,
                    ss.season,
                    ss.wins,
                    ss.losses,
                    ss.points_for,
                    ss.points_against,
                    (ss.points_for - ss.points_against) as point_differential,
                    CASE 
                        WHEN ss.games_played > 0 THEN ROUND((ss.wins * 1.0 / ss.games_played), 3)
                        ELSE 0 
                    END as win_percentage
                FROM Teams t
                LEFT JOIN SeasonStats ss ON t.team_id = ss.team_id
            ''')
            
            self.conn.commit()
            print("✅ Enhanced database schema created successfully!")
            print("\n📊 Schema Summary:")
            print("   🗃️ Teams - Team information with enhanced details")
            print("   🏈 Games - Game data with weather and attendance")
            print("   📊 TeamStats - Comprehensive team statistics")
            print("   💰 BettingLines - Betting data with user predictions")
            print("   🎯 UserPredictions - Individual user predictions")
            print("   📈 SeasonStats - Aggregated season performance")
            print("   🔍 Performance indexes for fast queries")
            print("   👁️ Helpful views for common operations")
            
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Error creating enhanced schema: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def insert_comprehensive_sample_data(self):
        """Insert comprehensive sample data matching the enhanced schema"""
        if not self.conn:
            print("❌ Error: No database connection")
            return False
            
        try:
            cursor = self.conn.cursor()
            print("\n📥 Inserting Comprehensive Sample Data...")
            print("=" * 45)
            
            # Enhanced Teams Data
            print("Inserting 🗃️ Teams data...")
            teams_data = [
                ('Kansas City Chiefs', 'KC', 'AFC', 'West', 'Kansas City', 
                 'https://logos.com/kc.png', '#E31837', '#FFB81C', 1960, 
                 'Arrowhead Stadium', 76416, 'Andy Reid'),
                ('Buffalo Bills', 'BUF', 'AFC', 'East', 'Buffalo',
                 'https://logos.com/buf.png', '#00338D', '#C60C30', 1960,
                 'Highmark Stadium', 71608, 'Sean McDermott'),
                ('Dallas Cowboys', 'DAL', 'NFC', 'East', 'Dallas',
                 'https://logos.com/dal.png', '#041E42', '#869397', 1960,
                 'AT&T Stadium', 80000, 'Mike McCarthy'),
                ('San Francisco 49ers', 'SF', 'NFC', 'West', 'San Francisco',
                 'https://logos.com/sf.png', '#AA0000', '#B3995D', 1946,
                 'Levi\'s Stadium', 68500, 'Kyle Shanahan'),
                ('New England Patriots', 'NE', 'AFC', 'East', 'New England',
                 'https://logos.com/ne.png', '#002244', '#C60C30', 1960,
                 'Gillette Stadium', 65878, 'Bill Belichick'),
                ('Green Bay Packers', 'GB', 'NFC', 'North', 'Green Bay',
                 'https://logos.com/gb.png', '#203731', '#FFB612', 1919,
                 'Lambeau Field', 81441, 'Matt LaFleur'),
                ('Philadelphia Eagles', 'PHI', 'NFC', 'East', 'Philadelphia',
                 'https://logos.com/phi.png', '#004C54', '#A5ACAF', 1933,
                 'Lincoln Financial Field', 69596, 'Nick Sirianni'),
                ('Miami Dolphins', 'MIA', 'AFC', 'East', 'Miami',
                 'https://logos.com/mia.png', '#008E97', '#FC4C02', 1966,
                 'Hard Rock Stadium', 65326, 'Mike McDaniel')
            ]
            
            cursor.executemany('''
                INSERT OR IGNORE INTO Teams 
                (name, abbreviation, conference, division, city, logo_url, 
                 primary_color, secondary_color, founded_year, stadium_name, 
                 stadium_capacity, head_coach)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', teams_data)
            
            # Sample Games with Enhanced Data
            print("Inserting 🏈 Games data...")
            games_data = [
                (1, 2024, 1, 2, '2024-09-07', '20:20', 31, 17, 'Final', 
                 'Clear', 72, 5, False, 76416, 'NBC'),
                (2, 2024, 3, 4, '2024-09-15', '13:00', 24, 21, 'Final',
                 'Partly Cloudy', 68, 8, False, 80000, 'FOX'),
                (3, 2024, 5, 6, '2024-09-22', '16:25', 14, 28, 'Final',
                 'Rain', 45, 12, False, 65878, 'CBS')
            ]
            
            for game_data in games_data:
                cursor.execute('''
                    INSERT INTO Games 
                    (week, season, home_team_id, away_team_id, date, time, 
                     score_home, score_away, game_status, weather_conditions,
                     temperature, wind_speed, is_playoff_game, attendance, tv_network)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', game_data)
            
            # Enhanced Team Statistics
            print("Inserting 📊 TeamStats data...")
            team_stats_data = [
                # Game 1 - KC vs BUF
                (1, 1, 425, 280, 0, 285, 140, 22, 8, 12, 1, 2, 3, 4, 25, 2, 8, 0, 0, '32:15', 68.5, 98.2, 4.2),
                (1, 2, 312, 425, 2, 195, 117, 18, 4, 11, 2, 4, 6, 45, 1, 2, 15, 1, 1, '27:45', 58.3, 76.4, 3.9),
                # Game 2 - DAL vs SF  
                (2, 3, 378, 295, 1, 245, 133, 20, 6, 10, 2, 3, 4, 35, 3, 1, 5, 0, 1, '30:22', 65.2, 89.1, 4.1),
                (2, 4, 410, 378, 0, 278, 132, 24, 9, 13, 3, 3, 2, 15, 4, 0, 0, 1, 0, '29:38', 71.4, 104.3, 3.8),
                # Game 3 - NE vs GB
                (3, 5, 298, 385, 3, 178, 120, 16, 3, 12, 1, 3, 8, 68, 2, 3, 20, 2, 1, '28:45', 52.1, 65.7, 3.5),
                (3, 6, 385, 298, 1, 298, 87, 21, 7, 11, 2, 2, 5, 42, 3, 1, 8, 1, 0, '31:15', 69.7, 95.8, 2.9)
            ]
            
            cursor.executemany('''
                INSERT INTO TeamStats 
                (game_id, team_id, offense_yards, defense_yards, turnovers,
                 passing_yards, rushing_yards, first_downs, third_down_conversions,
                 third_down_attempts, red_zone_conversions, red_zone_attempts,
                 penalties, penalty_yards, sacks, sack_yards, interceptions,
                 fumbles_lost, time_of_possession, completion_percentage,
                 quarterback_rating, rushing_average)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', team_stats_data)
            
            # Enhanced Betting Lines
            print("Inserting 💰 BettingLines data...")
            betting_data = [
                (1, -6.5, 48.5, -280, +220, 'ML Power Rating System', 'H.C. Lombardo', 
                 0.78, 'DraftKings', -1.0, -5.5, 49.0, -6.5, 48.5, True, 'Advanced Analytics', 0.82),
                (2, +2.5, 51.0, +110, -130, 'Home Field Algorithm', 'H.C. Lombardo',
                 0.65, 'FanDuel', +0.5, +2.0, 50.5, +2.5, 51.0, True, 'Regression Model', 0.74),
                (3, -3.0, 44.0, -150, +130, 'Weather Impact Model', 'H.C. Lombardo',
                 0.71, 'BetMGM', -0.5, -2.5, 45.0, -3.0, 44.0, True, 'Neural Network', 0.69)
            ]
            
            cursor.executemany('''
                INSERT INTO BettingLines 
                (game_id, spread, total, home_moneyline, away_moneyline,
                 formula_name, predicted_by_user, prediction_confidence,
                 sportsbook, line_movement, opening_spread, opening_total,
                 closing_spread, closing_total, is_user_prediction,
                 algorithm_used, model_accuracy)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', betting_data)
            
            # User Predictions
            print("Inserting 🎯 UserPredictions data...")
            prediction_data = [
                (1, 'H.C. Lombardo', 28, 21, -7.0, 49.0, 8, 
                 'Chiefs at home in primetime, strong offensive showing expected', 'Power Rating + Home Field'),
                (2, 'H.C. Lombardo', 27, 24, +3.0, 51.0, 6,
                 'Close divisional matchup, expect high-scoring affair', 'Historical Trends'),
                (3, 'H.C. Lombardo', 17, 20, -3.0, 37.0, 7,
                 'Weather impact significant, under conditions favor defense', 'Weather Model')
            ]
            
            cursor.executemany('''
                INSERT INTO UserPredictions 
                (game_id, user_name, predicted_home_score, predicted_away_score,
                 predicted_spread, predicted_total, confidence_level, reasoning, formula_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', prediction_data)
            
            # Season Statistics
            print("Inserting 📈 SeasonStats data...")
            season_stats_data = [
                (1, 2024, 3, 2, 1, 0, 72, 51, 1247, 956, 3, 1, False, False, False, False),  # KC
                (2, 2024, 3, 1, 2, 0, 58, 63, 1089, 1203, 2, 4, False, False, False, False),  # BUF
                (3, 2024, 3, 2, 1, 0, 69, 54, 1156, 1098, 4, 2, False, False, False, False),  # DAL
                (4, 2024, 3, 2, 1, 0, 75, 48, 1289, 1034, 3, 1, False, False, False, False),  # SF
                (5, 2024, 3, 1, 2, 0, 45, 71, 987, 1278, 1, 5, False, False, False, False),  # NE
                (6, 2024, 3, 2, 1, 0, 68, 52, 1198, 1067, 4, 2, False, False, False, False),  # GB
            ]
            
            cursor.executemany('''
                INSERT INTO SeasonStats 
                (team_id, season, games_played, wins, losses, ties,
                 points_for, points_against, total_yards_for, total_yards_against,
                 turnovers_forced, turnovers_committed, playoff_appearance,
                 division_winner, conference_winner, super_bowl_winner)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', season_stats_data)
            
            self.conn.commit()
            print("✅ Comprehensive sample data inserted successfully!")
            print("\n📊 Data Summary:")
            print("   🗃️ 8 NFL Teams with complete information")
            print("   🏈 3 Games with weather and attendance data")
            print("   📊 6 Complete team stat records")
            print("   💰 3 Betting lines with user predictions")
            print("   🎯 3 Detailed user predictions")
            print("   📈 6 Season statistics records")
            
            return True
            
        except sqlite3.Error as e:
            print(f"❌ Error inserting sample data: {e}")
            if self.conn:
                self.conn.rollback()
            return False
    
    def get_schema_info(self):
        """Get detailed information about the database schema"""
        if not self.conn:
            print("❌ Error: No database connection")
            return None
            
        cursor = self.conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        schema_info = {}
        
        for table in tables:
            table_name = table['name']
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            row_count = cursor.fetchone()['count']
            
            schema_info[table_name] = {
                'columns': [dict(col) for col in columns],
                'row_count': row_count
            }
        
        return schema_info
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")

def main():
    """Create and populate the enhanced NFL database"""
    print("🏈 Enhanced NFL Betting Database Creator")
    print("=" * 50)
    print("Implementing user-specified schema:")
    print("🗃️ Teams | 🏈 Games | 📊 TeamStats | 💰 BettingLines")
    print("=" * 50)
    
    # Create database
    db = EnhancedNFLDatabase()
    
    if not db.connect():
        return
    
    # Create schema
    if not db.create_enhanced_schema():
        return
    
    # Insert sample data
    if not db.insert_comprehensive_sample_data():
        return
    
    # Show schema information
    print("\n🔍 Database Schema Information:")
    print("=" * 40)
    schema_info = db.get_schema_info()
    
    if schema_info:
        for table_name, info in schema_info.items():
            print(f"\n📋 {table_name} ({info['row_count']} records)")
            for col in info['columns'][:3]:  # Show first 3 columns
                print(f"   • {col['name']} ({col['type']})")
            if len(info['columns']) > 3:
                print(f"   • ... and {len(info['columns']) - 3} more columns")
    
    print(f"\n✅ Enhanced database created successfully!")
    print(f"📁 Database file: {db.db_name}")
    print(f"🎯 Ready for advanced betting predictions!")
    
    db.close()

if __name__ == "__main__":
    main()