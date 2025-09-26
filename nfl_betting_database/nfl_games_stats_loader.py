#!/usr/bin/env python3
"""
NFL Games and Stats Loader
Create sample games and load team stats into proper schema
"""

import requests
import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sys
import os
import random

# Add external_apis to path for API configuration
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'external_apis'))

try:
    from api_config import APIKeys
except ImportError:
    print("⚠️ API configuration not found. Using fallback mode.")
    APIKeys = None

class NFLGamesStatsLoader:
    """Load NFL games and team stats from API-SPORTS into SQLite database"""
    
    def __init__(self, db_path: str = "user_schema_nfl.db"):
        self.db_path = db_path
        self.api_keys = APIKeys() if APIKeys else None
        self.base_url = "https://v1.american-football.api-sports.io"
        self.session = requests.Session()
        
        # Set up API headers
        if self.api_keys and hasattr(self.api_keys, 'api_sports'):
            headers = self.api_keys.get_headers('api_sports')
            self.session.headers.update(headers)
            print("✅ API-SPORTS configured with authentication")
        else:
            print("⚠️ No API key found - using mock data fallback")
    
    def get_teams(self) -> List[Dict]:
        """Get all teams from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT team_id, name, abbreviation FROM Teams")
            teams = [{'id': tid, 'name': name, 'abbr': abbr} for tid, name, abbr in cursor.fetchall()]
            
            conn.close()
            return teams
            
        except Exception as e:
            print(f"❌ Error getting teams: {e}")
            return []
    
    def create_sample_games(self, season: int = 2024, num_weeks: int = 4) -> List[int]:
        """Create sample games for the season"""
        teams = self.get_teams()
        if len(teams) < 4:
            print("❌ Need at least 4 teams to create games")
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            game_ids = []
            game_date = datetime(2024, 9, 8)  # Start of 2024 NFL season
            
            print(f"🏈 Creating sample games for {num_weeks} weeks...")
            
            for week in range(1, num_weeks + 1):
                # Create 2-3 games per week with available teams
                games_this_week = min(3, len(teams) // 2)
                
                for game_num in range(games_this_week):
                    # Pick random teams
                    available_teams = teams.copy()
                    home_team = available_teams.pop(random.randint(0, len(available_teams) - 1))
                    away_team = available_teams.pop(random.randint(0, len(available_teams) - 1))
                    
                    # Generate realistic scores
                    home_score = random.randint(14, 42)
                    away_score = random.randint(10, 35)
                    
                    cursor.execute('''
                        INSERT INTO Games (week, season, home_team_id, away_team_id, date, score_home, score_away)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (week, season, home_team['id'], away_team['id'], game_date.strftime('%Y-%m-%d'), home_score, away_score))
                    
                    game_id = cursor.lastrowid
                    game_ids.append(game_id)
                    
                    print(f"   Week {week}: {away_team['name']} @ {home_team['name']} ({away_score}-{home_score})")
                
                game_date += timedelta(days=7)  # Next week
            
            conn.commit()
            conn.close()
            
            print(f"✅ Created {len(game_ids)} sample games")
            return game_ids
            
        except Exception as e:
            print(f"❌ Error creating games: {e}")
            return []
    
    def fetch_team_stats(self, season: int = 2024) -> List[Dict]:
        """Generate realistic mock team statistics for all games"""
        teams = self.get_teams()
        
        # Get games to link stats to
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT game_id, home_team_id, away_team_id FROM Games WHERE season = ?", (season,))
            games = cursor.fetchall()
            conn.close()
        except:
            games = []
        
        if not games:
            print("❌ No games found - create games first")
            return []
        
        mock_stats = []
        
        print(f"📊 Generating team stats for {len(games)} games...")
        
        for game_id, home_team_id, away_team_id in games:
            # Generate stats for home team
            home_stats = self._generate_team_game_stats(game_id, home_team_id)
            away_stats = self._generate_team_game_stats(game_id, away_team_id)
            
            mock_stats.extend([home_stats, away_stats])
        
        print(f"✅ Generated stats for {len(mock_stats)} team-game combinations")
        return mock_stats
    
    def _generate_team_game_stats(self, game_id: int, team_id: int) -> Dict:
        """Generate realistic stats for one team in one game"""
        random.seed(game_id * 100 + team_id)  # Consistent but varied
        
        # Generate realistic game stats
        offense_yards = random.randint(250, 450)
        defense_yards = random.randint(220, 400)
        passing_yards = int(offense_yards * random.uniform(0.6, 0.8))
        rushing_yards = offense_yards - passing_yards
        turnovers = random.randint(0, 4)
        first_downs = random.randint(15, 28)
        third_down_attempts = random.randint(8, 15)
        third_down_conversions = random.randint(2, min(8, third_down_attempts))
        red_zone_attempts = random.randint(2, 6)
        red_zone_conversions = random.randint(1, red_zone_attempts)
        penalties = random.randint(4, 12)
        penalty_yards = penalties * random.randint(8, 15)
        
        return {
            'game_id': game_id,
            'team_id': team_id,
            'offense_yards': offense_yards,
            'defense_yards': defense_yards,
            'turnovers': turnovers,
            'passing_yards': passing_yards,
            'rushing_yards': rushing_yards,
            'first_downs': first_downs,
            'third_down_conversions': third_down_conversions,
            'third_down_attempts': third_down_attempts,
            'red_zone_conversions': red_zone_conversions,
            'red_zone_attempts': red_zone_attempts,
            'penalties': penalties,
            'penalty_yards': penalty_yards
        }
    
    def insert_team_stats(self, stats: List[Dict]) -> int:
        """Insert team statistics into TeamStats table"""
        if not stats:
            print("⚠️ No stats to insert")
            return 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            inserted_count = 0
            
            for stat in stats:
                try:
                    cursor.execute('''
                        INSERT INTO TeamStats (
                            game_id, team_id, offense_yards, defense_yards, turnovers,
                            passing_yards, rushing_yards, first_downs,
                            third_down_conversions, third_down_attempts,
                            red_zone_conversions, red_zone_attempts,
                            penalties, penalty_yards
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        stat['game_id'], stat['team_id'], stat['offense_yards'],
                        stat['defense_yards'], stat['turnovers'], stat['passing_yards'],
                        stat['rushing_yards'], stat['first_downs'],
                        stat['third_down_conversions'], stat['third_down_attempts'],
                        stat['red_zone_conversions'], stat['red_zone_attempts'],
                        stat['penalties'], stat['penalty_yards']
                    ))
                    
                    inserted_count += 1
                    
                except Exception as e:
                    print(f"❌ Error inserting stat: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            print(f"✅ Inserted {inserted_count} team stats records")
            return inserted_count
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return 0
    
    def create_sample_betting_lines(self) -> int:
        """Create sample betting lines for games"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT game_id FROM Games")
            games = [row[0] for row in cursor.fetchall()]
            
            inserted_count = 0
            
            print(f"💰 Creating betting lines for {len(games)} games...")
            
            for game_id in games:
                # Generate realistic betting lines
                spread = random.uniform(-14.0, 14.0)
                total = random.uniform(38.5, 58.5)
                home_moneyline = random.randint(-300, 300)
                away_moneyline = -home_moneyline + random.randint(-50, 50)
                
                cursor.execute('''
                    INSERT INTO BettingLines (
                        game_id, spread, total, formula_name, predicted_by_user,
                        home_moneyline, away_moneyline, sportsbook, prediction_confidence
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    game_id, round(spread, 1), round(total, 1), 
                    'API_Mock_Formula', 'System', 
                    home_moneyline, away_moneyline, 'DraftKings', 
                    random.uniform(0.6, 0.9)
                ))
                
                inserted_count += 1
            
            conn.commit()
            conn.close()
            
            print(f"✅ Created {inserted_count} betting lines")
            return inserted_count
            
        except Exception as e:
            print(f"❌ Error creating betting lines: {e}")
            return 0
    
    def show_database_summary(self):
        """Show summary of loaded data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            print("\n📊 Database Summary")
            print("=" * 30)
            
            # Count each table
            tables = ['Teams', 'Games', 'TeamStats', 'BettingLines']
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   {table}: {count} records")
            
            # Show sample data
            print("\n🏈 Recent Games:")
            cursor.execute('''
                SELECT g.week, ht.name, at.name, g.score_home, g.score_away
                FROM Games g
                JOIN Teams ht ON g.home_team_id = ht.team_id
                JOIN Teams at ON g.away_team_id = at.team_id
                ORDER BY g.game_id DESC LIMIT 5
            ''')
            
            for week, home, away, h_score, a_score in cursor.fetchall():
                print(f"   Week {week}: {away} @ {home} ({a_score}-{h_score})")
            
            print("\n📊 Team Stats Sample:")
            cursor.execute('''
                SELECT t.name, ts.offense_yards, ts.defense_yards, ts.turnovers
                FROM TeamStats ts
                JOIN Teams t ON ts.team_id = t.team_id
                ORDER BY ts.stat_id DESC LIMIT 5
            ''')
            
            for name, off, def_, to in cursor.fetchall():
                print(f"   {name}: {off} OFF, {def_} DEF, {to} TO")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error showing summary: {e}")
    
    def load_complete_data(self, season: int = 2024) -> Dict:
        """Complete workflow: create games, generate stats, create betting lines"""
        print("🏈 NFL Complete Data Loader")
        print("=" * 50)
        
        results = {'games': 0, 'stats': 0, 'betting_lines': 0}
        
        # Step 1: Create sample games
        print("🔄 Step 1: Creating sample games...")
        game_ids = self.create_sample_games(season)
        results['games'] = len(game_ids)
        
        if not game_ids:
            print("❌ Failed to create games")
            return results
        
        # Step 2: Generate team stats
        print("🔄 Step 2: Generating team statistics...")
        stats = self.fetch_team_stats(season)
        
        if stats:
            print("🔄 Step 3: Inserting team statistics...")
            results['stats'] = self.insert_team_stats(stats)
        
        # Step 3: Create betting lines
        print("🔄 Step 4: Creating betting lines...")
        results['betting_lines'] = self.create_sample_betting_lines()
        
        # Show summary
        self.show_database_summary()
        
        print("\n🎉 Complete data loading finished!")
        print(f"   📊 Games: {results['games']}")
        print(f"   📊 Team Stats: {results['stats']}")
        print(f"   💰 Betting Lines: {results['betting_lines']}")
        
        return results

def main():
    print("🏈 NFL Games & Stats Loader")
    print("Create complete NFL data with games, stats, and betting lines")
    print("=" * 65)
    
    loader = NFLGamesStatsLoader()
    results = loader.load_complete_data()
    
    if results['stats'] > 0:
        print("\n🎯 Ready for Analysis!")
        print("• Your database now has complete NFL data")
        print("• Teams, Games, TeamStats, and BettingLines populated")
        print("• Run betting predictions with realistic data")

if __name__ == "__main__":
    main()