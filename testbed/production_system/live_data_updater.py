"""
Live Data Updater - Fetches fresh NFL data from ESPN API
Runs on schedule or on-demand to keep database current
"""
import requests
import psycopg2
from datetime import datetime
import time
import sys
from typing import Dict, List, Optional

class LiveDataUpdater:
    """Fetches and updates NFL data from ESPN API"""
    
    ESPN_API_BASE = "http://site.api.espn.com/apis/site/v2/sports/football/nfl"
    
    def __init__(self, db_config: Optional[Dict] = None):
        self.db_config = db_config or {
            'host': 'localhost',
            'port': 5432,
            'database': 'nfl_analytics',
            'user': 'postgres',
            'password': 'aprilv120'
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)
    
    def fetch_current_standings(self) -> List[Dict]:
        """Fetch current NFL standings from ESPN API"""
        print("\n📡 Fetching live data from ESPN API...")
        
        try:
            # Get scoreboard which includes current standings
            url = f"{self.ESPN_API_BASE}/scoreboard"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            standings = []
            
            # Extract season info
            season_info = {}
            if 'leagues' in data:
                for league in data['leagues']:
                    season = league.get('season', {})
                    season_info = {
                        'year': season.get('year'),
                        'type': season.get('type', {}).get('name', 'Regular Season')
                    }
            
            print(f"   📅 Season: {season_info.get('year')} {season_info.get('type')}")
            
            # Extract team standings from events
            teams_data = {}
            if 'events' in data:
                for event in data['events']:
                    for competition in event.get('competitions', []):
                        for competitor in competition.get('competitors', []):
                            team = competitor.get('team', {})
                            team_id = team.get('id')
                            
                            if team_id not in teams_data:
                                # Get record
                                record = competitor.get('records', [{}])[0] if competitor.get('records') else {}
                                summary = record.get('summary', '0-0')
                                wins, losses = 0, 0
                                
                                try:
                                    parts = summary.split('-')
                                    wins = int(parts[0])
                                    losses = int(parts[1]) if len(parts) > 1 else 0
                                except:
                                    pass
                                
                                # Get statistics
                                stats = competitor.get('statistics', [])
                                ppg = 0.0
                                pa = 0.0
                                
                                for stat in stats:
                                    name = stat.get('name', '').lower()
                                    value = float(stat.get('displayValue', 0))
                                    
                                    if 'points' in name and 'per game' in name:
                                        ppg = value
                                    elif 'points allowed' in name:
                                        pa = value
                                
                                teams_data[team_id] = {
                                    'id': team_id,
                                    'name': team.get('displayName', team.get('name', 'Unknown')),
                                    'abbreviation': team.get('abbreviation', 'UNK'),
                                    'wins': wins,
                                    'losses': losses,
                                    'ppg': ppg,
                                    'pa': pa
                                }
            
            standings = list(teams_data.values())
            print(f"   ✅ Fetched data for {len(standings)} teams")
            
            return standings
            
        except Exception as e:
            print(f"   ❌ Error fetching ESPN data: {str(e)}")
            return []
    
    def update_database(self, standings: List[Dict]) -> bool:
        """Update database with current standings"""
        if not standings:
            print("❌ No standings data to update")
            return False
        
        print(f"\n💾 Updating database with {len(standings)} teams...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            updated_count = 0
            for team in standings:
                games_played = team['wins'] + team['losses']
                
                # Update existing team or insert if not exists
                cursor.execute("""
                    INSERT INTO teams (name, abbreviation, wins, losses, ppg, pa, games_played)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (abbreviation) 
                    DO UPDATE SET
                        wins = EXCLUDED.wins,
                        losses = EXCLUDED.losses,
                        ppg = EXCLUDED.ppg,
                        pa = EXCLUDED.pa,
                        games_played = EXCLUDED.games_played
                """, (
                    team['name'],
                    team['abbreviation'],
                    team['wins'],
                    team['losses'],
                    round(team['ppg'], 1),
                    round(team['pa'], 1),
                    games_played
                ))
                
                updated_count += 1
            
            conn.commit()
            conn.close()
            
            print(f"   ✅ Updated {updated_count} teams in database")
            
            # Show sample of updated data
            self._show_sample_teams()
            
            return True
            
        except Exception as e:
            print(f"   ❌ Database update failed: {str(e)}")
            return False
    
    def _show_sample_teams(self):
        """Show sample of updated teams"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name, abbreviation, wins, losses
                FROM teams
                ORDER BY wins DESC, losses ASC
                LIMIT 5
            """)
            
            print("\n   📊 Top 5 Teams (by record):")
            for row in cursor.fetchall():
                print(f"      • {row[0]:30s} {row[1]:3s}  {row[2]}-{row[3]}")
            
            conn.close()
            
        except Exception as e:
            print(f"   ⚠️  Could not fetch sample: {str(e)}")
    
    def run_update(self) -> bool:
        """Run complete data update process"""
        print("\n" + "="*70)
        print(f"🔄 LIVE DATA UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Fetch latest standings
        standings = self.fetch_current_standings()
        
        if not standings:
            print("\n❌ Update failed: No data fetched from ESPN")
            return False
        
        # Update database
        success = self.update_database(standings)
        
        print("\n" + "="*70)
        if success:
            print("✅ LIVE DATA UPDATE COMPLETE")
        else:
            print("❌ LIVE DATA UPDATE FAILED")
        print("="*70 + "\n")
        
        return success
    
    def run_continuous(self, interval_minutes: int = 30):
        """Run continuous updates at specified interval"""
        print(f"\n🔁 Starting continuous updates (every {interval_minutes} minutes)")
        print("   Press Ctrl+C to stop")
        
        try:
            while True:
                self.run_update()
                
                print(f"\n⏰ Next update in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Continuous updates stopped by user")

if __name__ == "__main__":
    updater = LiveDataUpdater()
    
    # Check for continuous mode
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        updater.run_continuous(interval)
    else:
        success = updater.run_update()
        exit(0 if success else 1)
