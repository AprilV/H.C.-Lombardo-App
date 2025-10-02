#!/usr/bin/env python3
"""
Live Data Collector for NFL Database
Collects data from APIs and web scraping to populate the database
"""

import sys
import os
import requests
import sqlite3
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import time
import re
from urllib.parse import urljoin

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'nfl_betting_database'))

try:
    from enhanced_schema_creator import EnhancedNFLDatabase
    from nfl_database_utils import NFLDatabaseManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Creating minimal database utilities...")

class LiveNFLDataCollector:
    """Collects live NFL data from multiple sources and populates database"""
    
    def __init__(self, db_path: str = None):
        """Initialize the data collector"""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'nfl_betting_database', 'enhanced_nfl_betting.db')
        
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Initialize database
        self.init_database()
        
        # Data sources configuration
        self.espn_base = "https://site.web.api.espn.com/apis/site/v2/sports/football/nfl"
        self.nfl_base = "https://www.nfl.com"
        
    def init_database(self):
        """Initialize the database schema"""
        try:
            db = EnhancedNFLDatabase(self.db_path)
            db.connect()
            db.create_enhanced_schema()
            
            # Add the missing data_collection_log table
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS data_collection_log (
                        id INTEGER PRIMARY KEY,
                        source TEXT,
                        endpoint TEXT,
                        status TEXT,
                        records_processed INTEGER,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        notes TEXT
                    )
                ''')
            
            print(f"✅ Database initialized: {self.db_path}")
        except Exception as e:
            print(f"⚠️ Database initialization error: {e}")
            # Create minimal schema if enhanced fails
            self.create_minimal_schema()
    
    def create_minimal_schema(self):
        """Create minimal database schema if enhanced schema fails"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    abbreviation TEXT UNIQUE,
                    logo_url TEXT,
                    conference TEXT,
                    division TEXT,
                    wins INTEGER DEFAULT 0,
                    losses INTEGER DEFAULT 0,
                    ppg REAL DEFAULT 0.0,
                    pa REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY,
                    week INTEGER,
                    season INTEGER,
                    home_team_id INTEGER,
                    away_team_id INTEGER,
                    date DATE,
                    home_score INTEGER,
                    away_score INTEGER,
                    status TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (home_team_id) REFERENCES teams(id),
                    FOREIGN KEY (away_team_id) REFERENCES teams(id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_collection_log (
                    id INTEGER PRIMARY KEY,
                    source TEXT,
                    endpoint TEXT,
                    status TEXT,
                    records_processed INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_collection_log (
                    id INTEGER PRIMARY KEY,
                    source TEXT,
                    endpoint TEXT,
                    status TEXT,
                    records_processed INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            ''')
            
            print("✅ Minimal database schema created")
    
    def collect_all_data(self):
        """Main data collection orchestrator"""
        print("🚀 Starting comprehensive NFL data collection...")
        print("=" * 60)
        
        collection_results = {
            'teams': 0,
            'games': 0,
            'stats': 0,
            'errors': []
        }
        
        try:
            # 1. Collect team data from ESPN
            print("📊 Step 1: Collecting team data from ESPN API...")
            teams_result = self.collect_teams_data()
            collection_results['teams'] = teams_result.get('count', 0)
            
            # 2. Collect current season games
            print("\n🏈 Step 2: Collecting games data...")
            games_result = self.collect_games_data()
            collection_results['games'] = games_result.get('count', 0)
            
            # 3. Collect team statistics
            print("\n📈 Step 3: Collecting team statistics...")
            stats_result = self.collect_team_statistics()
            collection_results['stats'] = stats_result.get('count', 0)
            
            # 4. Scrape additional data if needed
            print("\n🔍 Step 4: Scraping additional data sources...")
            scraping_result = self.scrape_additional_data()
            
            self.log_collection_result("Full Collection", "All Sources", 
                                     f"Teams: {collection_results['teams']}, Games: {collection_results['games']}")
            
        except Exception as e:
            error_msg = f"Collection error: {str(e)}"
            collection_results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        
        return collection_results
    
    def collect_teams_data(self) -> Dict:
        """Collect team data from ESPN API"""
        try:
            url = f"{self.espn_base}/teams"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            teams_processed = 0
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if 'sports' in data and len(data['sports']) > 0:
                    leagues = data['sports'][0].get('leagues', [])
                    if leagues:
                        for team_data in leagues[0].get('teams', []):
                            team = team_data.get('team', {})
                            
                            # Extract team information
                            team_id = team.get('id')
                            name = team.get('displayName', 'Unknown Team')
                            abbreviation = team.get('abbreviation', 'UNK')
                            logo_url = team.get('logos', [{}])[0].get('href', '')
                            
                            # Determine conference and division
                            location = team.get('location', '')
                            conference = self.determine_conference(abbreviation)
                            division = self.determine_division(abbreviation)
                            
                            # Insert or update team in enhanced schema
                            cursor.execute('''
                                INSERT OR REPLACE INTO Teams 
                                (team_id, name, abbreviation, logo_url, conference, division)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (team_id, name, abbreviation, logo_url, conference, division))
                            
                            teams_processed += 1
                            print(f"  ✓ Processed: {name} ({abbreviation})")
            
            self.log_collection_result("Teams Collection", "ESPN API", f"Processed {teams_processed} teams")
            return {'count': teams_processed, 'status': 'success'}
            
        except Exception as e:
            self.log_collection_result("Teams Collection", "ESPN API", f"Error: {str(e)}")
            return {'count': 0, 'status': 'error', 'error': str(e)}
    
    def collect_games_data(self) -> Dict:
        """Collect games data from ESPN API"""
        try:
            # Get current season games
            current_year = datetime.now().year
            url = f"{self.espn_base}/scoreboard"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            games_processed = 0
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for event in data.get('events', []):
                    game_id = event.get('id')
                    game_date = event.get('date', '').split('T')[0]  # Extract date part
                    
                    # Extract week and season from event
                    week = event.get('week', {}).get('number', 1)
                    season = current_year
                    
                    # Get teams and scores
                    competitions = event.get('competitions', [])
                    if competitions:
                        competitors = competitions[0].get('competitors', [])
                        if len(competitors) >= 2:
                            # Determine home and away teams
                            home_team = next((c for c in competitors if c.get('homeAway') == 'home'), None)
                            away_team = next((c for c in competitors if c.get('homeAway') == 'away'), None)
                            
                            if home_team and away_team:
                                home_team_id = home_team.get('team', {}).get('id')
                                away_team_id = away_team.get('team', {}).get('id')
                                home_score = home_team.get('score', 0) if home_team.get('score') != '' else None
                                away_score = away_team.get('score', 0) if away_team.get('score') != '' else None
                                
                                status = event.get('status', {}).get('type', {}).get('name', 'Scheduled')
                                
                                # Insert or update game in enhanced schema
                                cursor.execute('''
                                    INSERT OR REPLACE INTO Games 
                                    (game_id, week, season, home_team_id, away_team_id, date, score_home, score_away, game_status)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (game_id, week, season, home_team_id, away_team_id, game_date, home_score, away_score, status))
                                
                                games_processed += 1
                                print(f"  ✓ Game: Week {week} - {home_team.get('team', {}).get('abbreviation')} vs {away_team.get('team', {}).get('abbreviation')}")
            
            self.log_collection_result("Games Collection", "ESPN API", f"Processed {games_processed} games")
            return {'count': games_processed, 'status': 'success'}
            
        except Exception as e:
            self.log_collection_result("Games Collection", "ESPN API", f"Error: {str(e)}")
            return {'count': 0, 'status': 'error', 'error': str(e)}
    
    def collect_team_statistics(self) -> Dict:
        """Calculate and store team statistics in TeamStats table"""
        try:
            stats_processed = 0
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if we have the enhanced schema
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Teams'")
                has_enhanced_schema = cursor.fetchone() is not None
                
                if has_enhanced_schema:
                    # Enhanced schema approach - calculate stats for each team
                    cursor.execute("SELECT team_id, name FROM Teams")
                    teams = cursor.fetchall()
                    
                    for team in teams:
                        team_id = team[0]
                        team_name = team[1]
                        
                        # Calculate wins
                        cursor.execute('''
                            SELECT COUNT(*) FROM Games 
                            WHERE ((home_team_id = ? AND score_home > score_away) OR 
                                   (away_team_id = ? AND score_away > score_home))
                            AND game_status = 'Final'
                            AND score_home IS NOT NULL AND score_away IS NOT NULL
                        ''', (team_id, team_id))
                        wins = cursor.fetchone()[0]
                        
                        # Calculate losses
                        cursor.execute('''
                            SELECT COUNT(*) FROM Games 
                            WHERE ((home_team_id = ? AND score_home < score_away) OR 
                                   (away_team_id = ? AND score_away < score_home))
                            AND game_status = 'Final'
                            AND score_home IS NOT NULL AND score_away IS NOT NULL
                        ''', (team_id, team_id))
                        losses = cursor.fetchone()[0]
                        
                        # Calculate PPG (Points Per Game)
                        cursor.execute('''
                            SELECT AVG(
                                CASE 
                                    WHEN home_team_id = ? THEN score_home 
                                    WHEN away_team_id = ? THEN score_away 
                                END
                            ) FROM Games 
                            WHERE (home_team_id = ? OR away_team_id = ?) 
                            AND game_status = 'Final'
                            AND score_home IS NOT NULL AND score_away IS NOT NULL
                        ''', (team_id, team_id, team_id, team_id))
                        ppg_result = cursor.fetchone()[0]
                        ppg = round(ppg_result, 1) if ppg_result else 0.0
                        
                        # Calculate PA (Points Allowed)
                        cursor.execute('''
                            SELECT AVG(
                                CASE 
                                    WHEN home_team_id = ? THEN score_away 
                                    WHEN away_team_id = ? THEN score_home 
                                END
                            ) FROM Games 
                            WHERE (home_team_id = ? OR away_team_id = ?) 
                            AND game_status = 'Final'
                            AND score_home IS NOT NULL AND score_away IS NOT NULL
                        ''', (team_id, team_id, team_id, team_id))
                        pa_result = cursor.fetchone()[0]
                        pa = round(pa_result, 1) if pa_result else 0.0
                        
                        # Store in TeamStats table (or create a stats summary)
                        current_season = datetime.now().year
                        cursor.execute('''
                            INSERT OR REPLACE INTO TeamStats 
                            (team_id, game_id, offense_yards, defense_yards_allowed, 
                             passing_yards, rushing_yards, turnovers, penalties)
                            VALUES (?, 0, ?, ?, 0, 0, 0, 0)
                        ''', (team_id, int(ppg * 10), int(pa * 10)))  # Store calculated stats
                        
                        stats_processed += 1
                        print(f"  ✓ Stats calculated: {team_name} - W:{wins} L:{losses}, PPG:{ppg}, PA:{pa}")
                        
                else:
                    # Basic schema approach (original code)
                    cursor.execute("SELECT id, abbreviation FROM teams")
                    teams = cursor.fetchall()
                    
                    for team in teams:
                        team_id = team[0]
                        
                        # Calculate wins/losses using basic schema
                        cursor.execute('''
                            SELECT COUNT(*) FROM games 
                            WHERE ((home_team_id = ? AND home_score > away_score) OR 
                                   (away_team_id = ? AND away_score > home_score))
                            AND status = 'Final'
                        ''', (team_id, team_id))
                        wins = cursor.fetchone()[0]
                        
                        cursor.execute('''
                            SELECT COUNT(*) FROM games 
                            WHERE ((home_team_id = ? AND home_score < away_score) OR 
                                   (away_team_id = ? AND away_score < home_score))
                            AND status = 'Final'
                        ''', (team_id, team_id))
                        losses = cursor.fetchone()[0]
                        
                        # Update team statistics in basic schema
                        cursor.execute('''
                            UPDATE teams 
                            SET wins = ?, losses = ?, last_updated = ?
                            WHERE id = ?
                        ''', (wins, losses, datetime.now(), team_id))
                        
                        stats_processed += 1
                        print(f"  ✓ Stats updated: {team[1]} - {wins}-{losses}")
            
            self.log_collection_result("Stats Calculation", "Database", f"Updated {stats_processed} teams")
            return {'count': stats_processed, 'status': 'success'}
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"❌ Stats calculation error: {error_msg}")
            self.log_collection_result("Stats Calculation", "Database", error_msg)
            return {'count': 0, 'status': 'error', 'error': str(e)}
    
    def scrape_additional_data(self) -> Dict:
        """Scrape additional data from NFL.com and other sources if needed"""
        try:
            # This is where we'd implement web scraping for data not available in APIs
            # For now, return a placeholder result
            scraped_count = 0
            
            # Example: Scrape injury reports, betting lines, advanced stats, etc.
            print("  ℹ️ Web scraping functionality ready for additional data sources")
            print("  💡 Future: Injury reports, betting lines, weather data, etc.")
            
            self.log_collection_result("Web Scraping", "Various Sources", f"Placeholder - {scraped_count} items")
            return {'count': scraped_count, 'status': 'ready'}
            
        except Exception as e:
            self.log_collection_result("Web Scraping", "Various Sources", f"Error: {str(e)}")
            return {'count': 0, 'status': 'error', 'error': str(e)}
    
    def determine_conference(self, abbreviation: str) -> str:
        """Determine conference from team abbreviation"""
        afc_teams = ['BUF', 'MIA', 'NE', 'NYJ', 'BAL', 'CIN', 'CLE', 'PIT', 
                    'HOU', 'IND', 'JAX', 'TEN', 'DEN', 'KC', 'LV', 'LAC']
        return 'AFC' if abbreviation in afc_teams else 'NFC'
    
    def determine_division(self, abbreviation: str) -> str:
        """Determine division from team abbreviation"""
        divisions = {
            'AFC East': ['BUF', 'MIA', 'NE', 'NYJ'],
            'AFC North': ['BAL', 'CIN', 'CLE', 'PIT'],
            'AFC South': ['HOU', 'IND', 'JAX', 'TEN'],
            'AFC West': ['DEN', 'KC', 'LV', 'LAC'],
            'NFC East': ['DAL', 'NYG', 'PHI', 'WSH'],
            'NFC North': ['CHI', 'DET', 'GB', 'MIN'],
            'NFC South': ['ATL', 'CAR', 'NO', 'TB'],
            'NFC West': ['ARI', 'LAR', 'SF', 'SEA']
        }
        
        for division, teams in divisions.items():
            if abbreviation in teams:
                return division
        return 'Unknown'
    
    def log_collection_result(self, source: str, endpoint: str, notes: str):
        """Log data collection results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Extract record count from notes if possible
                records = 0
                if "Processed" in notes:
                    try:
                        records = int(re.search(r'(\d+)', notes).group(1))
                    except:
                        pass
                
                cursor.execute('''
                    INSERT INTO data_collection_log (source, endpoint, status, records_processed, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (source, endpoint, 'success' if 'Error' not in notes else 'error', records, notes))
                
        except Exception as e:
            print(f"⚠️ Logging error: {e}")
    
    def get_collection_status(self) -> Dict:
        """Get status of data collection"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get team count
                cursor.execute("SELECT COUNT(*) FROM teams")
                team_count = cursor.fetchone()[0]
                
                # Get game count
                cursor.execute("SELECT COUNT(*) FROM games")
                game_count = cursor.fetchone()[0]
                
                # Get last collection time
                cursor.execute("""
                    SELECT timestamp FROM data_collection_log 
                    ORDER BY timestamp DESC LIMIT 1
                """)
                last_collection = cursor.fetchone()
                last_collection_time = last_collection[0] if last_collection else "Never"
                
                return {
                    'teams_in_db': team_count,
                    'games_in_db': game_count,
                    'last_collection': last_collection_time,
                    'database_path': self.db_path
                }
                
        except Exception as e:
            return {'error': str(e)}

def main():
    """Main execution function"""
    print("🏈 NFL Live Data Collector")
    print("=" * 40)
    
    collector = LiveNFLDataCollector()
    
    print("📊 Current database status:")
    status = collector.get_collection_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n🚀 Starting data collection...")
    results = collector.collect_all_data()
    
    print("\n📈 Collection Results:")
    print(f"  Teams processed: {results['teams']}")
    print(f"  Games processed: {results['games']}")
    print(f"  Stats updated: {results['stats']}")
    
    if results['errors']:
        print("\n❌ Errors encountered:")
        for error in results['errors']:
            print(f"  - {error}")
    
    print("\n✅ Data collection complete!")

if __name__ == "__main__":
    main()