#!/usr/bin/env python3
"""
User Schema Implementation and Demo
Exactly implements your specified schema:
🗃️ Teams (team_id PK, name, abbreviation, conference, division)
🏈 Games (game_id PK, week, season, home_team_id FK, away_team_id FK, date, score_home, score_away)  
📊 TeamStats (stat_id PK, game_id FK, team_id FK, offense_yards, defense_yards, turnovers, etc.)
💰 BettingLines (line_id PK, game_id FK, spread, total, formula_name, predicted_by_user)
"""

import sqlite3
from datetime import datetime
import os

def create_user_specified_schema():
    """Create database with your exact schema specifications"""
    
    db_name = "user_schema_nfl.db"
    print("🏈 Creating Your Exact Database Schema")
    print("=" * 45)
    print("🗃️ Teams - team_id (PK), name, abbreviation, conference, division")
    print("🏈 Games - game_id (PK), week, season, home_team_id (FK), away_team_id (FK), date, score_home, score_away")
    print("📊 TeamStats - stat_id (PK), game_id (FK), team_id (FK), offense_yards, defense_yards, turnovers, etc.")
    print("💰 BettingLines - line_id (PK), game_id (FK), spread, total, formula_name, predicted_by_user")
    print("=" * 45)
    
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 🗃️ Teams Table (Exactly as you specified)
        print("Creating 🗃️ Teams table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Teams (
                team_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                abbreviation TEXT NOT NULL,
                conference TEXT NOT NULL,
                division TEXT NOT NULL
            )
        ''')
        
        # 🏈 Games Table (Exactly as you specified)
        print("Creating 🏈 Games table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Games (
                game_id INTEGER PRIMARY KEY,
                week INTEGER NOT NULL,
                season INTEGER NOT NULL,
                home_team_id INTEGER NOT NULL,
                away_team_id INTEGER NOT NULL,
                date DATE NOT NULL,
                score_home INTEGER,
                score_away INTEGER,
                FOREIGN KEY (home_team_id) REFERENCES Teams(team_id),
                FOREIGN KEY (away_team_id) REFERENCES Teams(team_id)
            )
        ''')
        
        # 📊 TeamStats Table (Exactly as you specified)
        print("Creating 📊 TeamStats table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS TeamStats (
                stat_id INTEGER PRIMARY KEY,
                game_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                offense_yards INTEGER,
                defense_yards INTEGER,
                turnovers INTEGER,
                passing_yards INTEGER,
                rushing_yards INTEGER,
                first_downs INTEGER,
                third_down_conversions INTEGER,
                third_down_attempts INTEGER,
                red_zone_conversions INTEGER,
                red_zone_attempts INTEGER,
                penalties INTEGER,
                penalty_yards INTEGER,
                FOREIGN KEY (game_id) REFERENCES Games(game_id),
                FOREIGN KEY (team_id) REFERENCES Teams(team_id)
            )
        ''')
        
        # 💰 BettingLines Table (Exactly as you specified)
        print("Creating 💰 BettingLines table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS BettingLines (
                line_id INTEGER PRIMARY KEY,
                game_id INTEGER NOT NULL,
                spread REAL NOT NULL,
                total REAL NOT NULL,
                formula_name TEXT,
                predicted_by_user TEXT,
                home_moneyline INTEGER,
                away_moneyline INTEGER,
                sportsbook TEXT,
                prediction_confidence REAL,
                FOREIGN KEY (game_id) REFERENCES Games(game_id)
            )
        ''')
        
        # Insert sample data
        print("\nInserting sample data...")
        
        # Teams data
        teams_data = [
            (1, 'Kansas City Chiefs', 'KC', 'AFC', 'West'),
            (2, 'Buffalo Bills', 'BUF', 'AFC', 'East'),
            (3, 'Dallas Cowboys', 'DAL', 'NFC', 'East'),
            (4, 'San Francisco 49ers', 'SF', 'NFC', 'West'),
            (5, 'New England Patriots', 'NE', 'AFC', 'East'),
            (6, 'Green Bay Packers', 'GB', 'NFC', 'North')
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO Teams (team_id, name, abbreviation, conference, division)
            VALUES (?, ?, ?, ?, ?)
        ''', teams_data)
        
        # Games data
        games_data = [
            (1, 1, 2024, 1, 2, '2024-09-07', 31, 17),  # KC vs BUF
            (2, 2, 2024, 3, 4, '2024-09-15', 24, 21),  # DAL vs SF
            (3, 3, 2024, 5, 6, '2024-09-22', 14, 28)   # NE vs GB
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO Games (game_id, week, season, home_team_id, away_team_id, date, score_home, score_away)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', games_data)
        
        # TeamStats data
        stats_data = [
            # Game 1 - KC (home) vs BUF (away)
            (1, 1, 1, 425, 280, 0, 285, 140, 22, 8, 12, 3, 4, 5, 45),    # KC stats
            (2, 1, 2, 312, 425, 2, 195, 117, 18, 4, 11, 2, 4, 6, 65),    # BUF stats
            # Game 2 - DAL (home) vs SF (away) 
            (3, 2, 3, 378, 295, 1, 245, 133, 20, 6, 10, 2, 3, 4, 35),    # DAL stats
            (4, 2, 4, 410, 378, 0, 278, 132, 24, 9, 13, 3, 3, 2, 15),    # SF stats
            # Game 3 - NE (home) vs GB (away)
            (5, 3, 5, 298, 385, 3, 178, 120, 16, 3, 12, 1, 3, 8, 68),    # NE stats
            (6, 3, 6, 385, 298, 1, 298, 87, 21, 7, 11, 2, 2, 5, 42)      # GB stats
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO TeamStats 
            (stat_id, game_id, team_id, offense_yards, defense_yards, turnovers,
             passing_yards, rushing_yards, first_downs, third_down_conversions,
             third_down_attempts, red_zone_conversions, red_zone_attempts, penalties, penalty_yards)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', stats_data)
        
        # BettingLines data  
        betting_data = [
            (1, 1, -6.5, 48.5, 'Power Rating System', 'H.C. Lombardo', -280, 220, 'DraftKings', 0.78),
            (2, 2, +2.5, 51.0, 'Home Field Algorithm', 'H.C. Lombardo', 110, -130, 'FanDuel', 0.65),
            (3, 3, -3.0, 44.0, 'Weather Impact Model', 'H.C. Lombardo', -150, 130, 'BetMGM', 0.71)
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO BettingLines 
            (line_id, game_id, spread, total, formula_name, predicted_by_user,
             home_moneyline, away_moneyline, sportsbook, prediction_confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', betting_data)
        
        conn.commit()
        
        print("✅ Database created successfully!")
        print(f"📁 Database file: {db_name}")
        
        # Demonstrate the schema
        print("\n🔍 Schema Verification:")
        print("=" * 30)
        
        # Show teams
        cursor.execute("SELECT * FROM Teams")
        teams = cursor.fetchall()
        print(f"\n🗃️ Teams Table ({len(teams)} records):")
        for team in teams:
            print(f"   {team['team_id']}: {team['name']} ({team['abbreviation']}) - {team['conference']} {team['division']}")
        
        # Show games
        cursor.execute('''
            SELECT g.*, ht.abbreviation as home_abbr, at.abbreviation as away_abbr
            FROM Games g
            JOIN Teams ht ON g.home_team_id = ht.team_id  
            JOIN Teams at ON g.away_team_id = at.team_id
        ''')
        games = cursor.fetchall()
        print(f"\n🏈 Games Table ({len(games)} records):")
        for game in games:
            print(f"   Week {game['week']}: {game['away_abbr']} @ {game['home_abbr']} ({game['score_away']}-{game['score_home']})")
        
        # Show team stats
        cursor.execute('''
            SELECT ts.*, t.abbreviation 
            FROM TeamStats ts
            JOIN Teams t ON ts.team_id = t.team_id
            ORDER BY ts.game_id, ts.team_id
        ''')
        stats = cursor.fetchall()
        print(f"\n📊 TeamStats Table ({len(stats)} records):")
        for stat in stats:
            print(f"   Game {stat['game_id']} - {stat['abbreviation']}: {stat['offense_yards']} total yards, {stat['turnovers']} turnovers")
        
        # Show betting lines
        cursor.execute('''
            SELECT bl.*, ht.abbreviation as home_abbr, at.abbreviation as away_abbr
            FROM BettingLines bl
            JOIN Games g ON bl.game_id = g.game_id
            JOIN Teams ht ON g.home_team_id = ht.team_id
            JOIN Teams at ON g.away_team_id = at.team_id
        ''')
        lines = cursor.fetchall()
        print(f"\n💰 BettingLines Table ({len(lines)} records):")
        for line in lines:
            print(f"   {line['away_abbr']} @ {line['home_abbr']}: {line['spread']} spread, {line['total']} total")
            print(f"      Formula: {line['formula_name']} by {line['predicted_by_user']}")
            print(f"      Confidence: {line['prediction_confidence']:.1%}")
        
        print("\n🎯 Your Exact Schema Implementation Complete!")
        print("   ✅ Teams table with team_id PK, name, abbreviation, conference, division")
        print("   ✅ Games table with game_id PK, week, season, team FKs, date, scores")
        print("   ✅ TeamStats table with stat_id PK, game_id FK, team_id FK, comprehensive stats")
        print("   ✅ BettingLines table with line_id PK, game_id FK, spread, total, formula_name, predicted_by_user")
        
        conn.close()
        return db_name
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.close()
        return None

def query_examples(db_name):
    """Show examples of querying your schema"""
    print(f"\n🔎 Query Examples for Your Schema")
    print("=" * 35)
    
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Example 1: Get all AFC teams
    print("\n1. All AFC Teams:")
    cursor.execute("SELECT name, abbreviation, division FROM Teams WHERE conference = 'AFC'")
    afc_teams = cursor.fetchall()
    for team in afc_teams:
        print(f"   {team['name']} ({team['abbreviation']}) - {team['division']}")
    
    # Example 2: Games with scores
    print("\n2. Games with Final Scores:")
    cursor.execute('''
        SELECT g.week, ht.abbreviation as home, at.abbreviation as away,
               g.score_home, g.score_away, g.date
        FROM Games g
        JOIN Teams ht ON g.home_team_id = ht.team_id
        JOIN Teams at ON g.away_team_id = at.team_id
        WHERE g.score_home IS NOT NULL
    ''')
    games = cursor.fetchall()
    for game in games:
        print(f"   Week {game['week']}: {game['away']} {game['score_away']} @ {game['home']} {game['score_home']}")
    
    # Example 3: Team offensive performance
    print("\n3. Team Offensive Yards (Highest to Lowest):")
    cursor.execute('''
        SELECT t.abbreviation, ts.offense_yards, g.week
        FROM TeamStats ts
        JOIN Teams t ON ts.team_id = t.team_id
        JOIN Games g ON ts.game_id = g.game_id
        ORDER BY ts.offense_yards DESC
    ''')
    offense = cursor.fetchall()
    for off in offense:
        print(f"   {off['abbreviation']} Week {off['week']}: {off['offense_yards']} yards")
    
    # Example 4: Betting predictions by user
    print("\n4. H.C. Lombardo's Predictions:")
    cursor.execute('''
        SELECT ht.abbreviation as home, at.abbreviation as away,
               bl.spread, bl.total, bl.formula_name, bl.prediction_confidence
        FROM BettingLines bl
        JOIN Games g ON bl.game_id = g.game_id
        JOIN Teams ht ON g.home_team_id = ht.team_id
        JOIN Teams at ON g.away_team_id = at.team_id
        WHERE bl.predicted_by_user = 'H.C. Lombardo'
    ''')
    predictions = cursor.fetchall()
    for pred in predictions:
        print(f"   {pred['away']} @ {pred['home']}: {pred['spread']}, O/U {pred['total']}")
        print(f"      Method: {pred['formula_name']} ({pred['prediction_confidence']:.1%} confidence)")
    
    conn.close()

def main():
    """Main execution"""
    db_name = create_user_specified_schema()
    if db_name:
        query_examples(db_name)

if __name__ == "__main__":
    main()