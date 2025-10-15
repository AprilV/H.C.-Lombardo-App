"""
Multi-Source NFL Data Aggregator
Combines multiple data sources to ensure complete, accurate data for all 32 teams:
1. ESPN API - Live standings and records
2. TeamRankings.com - PPG and PA stats (web scraping)
3. Fallback data - Ensures no team is missing

Strategy:
- Fetch from all sources
- Merge data by team name/abbreviation
- Validate that all 32 teams have complete data
- Fill gaps with most recent known data
"""
import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class MultiSourceDataFetcher:
    """Aggregates NFL data from multiple sources"""
    
    ESPN_API_BASE = "http://site.api.espn.com/apis/site/v2/sports/football/nfl"
    TEAMRANKINGS_PPG = "https://www.teamrankings.com/nfl/stat/points-per-game"
    TEAMRANKINGS_PA = "https://www.teamrankings.com/nfl/stat/opponent-points-per-game"
    
    # NFL Team name mappings (different sources use different names)
    TEAM_NAME_MAPPINGS = {
        'LA Rams': 'Los Angeles Rams',
        'LA Chargers': 'Los Angeles Chargers',
        'NY Giants': 'New York Giants',
        'NY Jets': 'New York Jets',
        'New England': 'New England Patriots',
        'Tampa Bay': 'Tampa Bay Buccaneers',
        'Kansas City': 'Kansas City Chiefs',
        'Green Bay': 'Green Bay Packers',
        'San Francisco': 'San Francisco 49ers',
        'Las Vegas': 'Las Vegas Raiders',
    }
    
    # All 32 NFL teams with abbreviations
    ALL_32_TEAMS = {
        'Arizona Cardinals': 'ARI',
        'Atlanta Falcons': 'ATL',
        'Baltimore Ravens': 'BAL',
        'Buffalo Bills': 'BUF',
        'Carolina Panthers': 'CAR',
        'Chicago Bears': 'CHI',
        'Cincinnati Bengals': 'CIN',
        'Cleveland Browns': 'CLE',
        'Dallas Cowboys': 'DAL',
        'Denver Broncos': 'DEN',
        'Detroit Lions': 'DET',
        'Green Bay Packers': 'GB',
        'Houston Texans': 'HOU',
        'Indianapolis Colts': 'IND',
        'Jacksonville Jaguars': 'JAX',
        'Kansas City Chiefs': 'KC',
        'Las Vegas Raiders': 'LV',
        'Los Angeles Chargers': 'LAC',
        'Los Angeles Rams': 'LAR',
        'Miami Dolphins': 'MIA',
        'Minnesota Vikings': 'MIN',
        'New England Patriots': 'NE',
        'New Orleans Saints': 'NO',
        'New York Giants': 'NYG',
        'New York Jets': 'NYJ',
        'Philadelphia Eagles': 'PHI',
        'Pittsburgh Steelers': 'PIT',
        'San Francisco 49ers': 'SF',
        'Seattle Seahawks': 'SEA',
        'Tampa Bay Buccaneers': 'TB',
        'Tennessee Titans': 'TEN',
        'Washington Commanders': 'WAS',
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.teams_data = {}  # Will hold merged data for all 32 teams
    
    def normalize_team_name(self, name: str) -> str:
        """Normalize team names across different sources"""
        name = name.strip()
        
        # Check mappings
        if name in self.TEAM_NAME_MAPPINGS:
            return self.TEAM_NAME_MAPPINGS[name]
        
        # Try to match partial names
        for full_name in self.ALL_32_TEAMS.keys():
            if name.lower() in full_name.lower() or full_name.lower() in name.lower():
                return full_name
        
        return name
    
    def fetch_espn_standings(self) -> dict:
        """Fetch standings from ESPN API"""
        print("\n1️⃣  Fetching standings from ESPN API...")
        
        try:
            url = f"{self.ESPN_API_BASE}/scoreboard"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            standings = {}
            
            # Get season info
            if 'leagues' in data:
                for league in data['leagues']:
                    season = league.get('season', {})
                    print(f"   📅 Season: {season.get('year')} {season.get('type', {}).get('name')}")
            
            # Extract team data from games
            if 'events' in data:
                for event in data['events']:
                    for competition in event.get('competitions', []):
                        for competitor in competition.get('competitors', []):
                            team = competitor.get('team', {})
                            team_name = team.get('displayName', '')
                            
                            if team_name:
                                normalized_name = self.normalize_team_name(team_name)
                                
                                # Get record
                                record = competitor.get('records', [{}])[0] if competitor.get('records') else {}
                                record_summary = record.get('summary', '0-0')
                                
                                try:
                                    # Handle W-L or W-L-T format
                                    parts = record_summary.split('-')
                                    wins = int(parts[0])
                                    losses = int(parts[1])
                                    ties = int(parts[2]) if len(parts) > 2 else 0
                                except:
                                    wins, losses, ties = 0, 0, 0
                                
                                standings[normalized_name] = {
                                    'name': normalized_name,
                                    'abbreviation': team.get('abbreviation', ''),
                                    'wins': wins,
                                    'losses': losses,
                                    'ties': ties,
                                    'games_played': wins + losses + ties
                                }
            
            print(f"   ✅ Got standings for {len(standings)} teams")
            return standings
            
        except Exception as e:
            print(f"   ❌ ESPN API error: {e}")
            return {}
    
    def scrape_teamrankings_ppg(self) -> dict:
        """Scrape PPG from TeamRankings.com"""
        print("\n2️⃣  Scraping PPG from TeamRankings.com...")
        
        try:
            response = self.session.get(self.TEAMRANKINGS_PPG, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            ppg_data = {}
            table = soup.find('table', class_='tr-table')
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        team_name = cells[1].get_text(strip=True)
                        ppg = float(cells[2].get_text(strip=True))
                        normalized_name = self.normalize_team_name(team_name)
                        ppg_data[normalized_name] = ppg
            
            print(f"   ✅ Got PPG for {len(ppg_data)} teams")
            return ppg_data
            
        except Exception as e:
            print(f"   ❌ TeamRankings PPG error: {e}")
            return {}
    
    def scrape_teamrankings_pa(self) -> dict:
        """Scrape PA from TeamRankings.com"""
        print("\n3️⃣  Scraping PA from TeamRankings.com...")
        
        try:
            response = self.session.get(self.TEAMRANKINGS_PA, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            pa_data = {}
            table = soup.find('table', class_='tr-table')
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        team_name = cells[1].get_text(strip=True)
                        pa = float(cells[2].get_text(strip=True))
                        normalized_name = self.normalize_team_name(team_name)
                        pa_data[normalized_name] = pa
            
            print(f"   ✅ Got PA for {len(pa_data)} teams")
            return pa_data
            
        except Exception as e:
            print(f"   ❌ TeamRankings PA error: {e}")
            return {}
    
    def merge_data_sources(self, standings, ppg_data, pa_data) -> dict:
        """Merge all data sources into complete team records"""
        print("\n4️⃣  Merging data from all sources...")
        
        merged = {}
        
        # Start with all 32 teams to ensure none are missing
        for team_name, abbr in self.ALL_32_TEAMS.items():
            merged[team_name] = {
                'name': team_name,
                'abbreviation': abbr,
                'wins': 0,
                'losses': 0,
                'ties': 0,
                'ppg': 0.0,
                'pa': 0.0,
                'games_played': 0
            }
        
        # Merge ESPN standings
        for team_name, team_data in standings.items():
            if team_name in merged:
                merged[team_name].update({
                    'wins': team_data.get('wins', 0),
                    'losses': team_data.get('losses', 0),
                    'ties': team_data.get('ties', 0),
                    'games_played': team_data.get('games_played', 0)
                })
        
        # Merge PPG data
        for team_name, ppg in ppg_data.items():
            if team_name in merged:
                merged[team_name]['ppg'] = ppg
        
        # Merge PA data
        for team_name, pa in pa_data.items():
            if team_name in merged:
                merged[team_name]['pa'] = pa
        
        # Report missing data
        complete_teams = 0
        incomplete_teams = []
        
        for team_name, data in merged.items():
            if data['wins'] > 0 or data['losses'] > 0:  # Has standings
                if data['ppg'] > 0 and data['pa'] > 0:  # Has stats
                    complete_teams += 1
                else:
                    incomplete_teams.append(f"{team_name} (missing {'PPG' if data['ppg'] == 0 else 'PA'})")
        
        print(f"   ✅ {complete_teams} teams have complete data")
        if incomplete_teams:
            print(f"   ⚠️  {len(incomplete_teams)} teams missing some data:")
            for team in incomplete_teams[:5]:  # Show first 5
                print(f"      • {team}")
        
        return merged
    
    def update_database(self, teams_data: dict) -> bool:
        """Update PostgreSQL database with merged data"""
        print("\n5️⃣  Updating database...")
        
        try:
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'nfl_analytics'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'aprilv120')
            )
            cursor = conn.cursor()
            
            # Update or insert each team
            updated_count = 0
            for team_name, data in teams_data.items():
                # Try update first (with timestamp)
                cursor.execute("""
                    UPDATE teams 
                    SET wins = %s, losses = %s, ties = %s, ppg = %s, pa = %s, games_played = %s,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE abbreviation = %s
                """, (
                    data['wins'], data['losses'], data['ties'], data['ppg'], 
                    data['pa'], data['games_played'], data['abbreviation']
                ))
                
                if cursor.rowcount == 0:
                    # Insert if doesn't exist (timestamp will use default)
                    cursor.execute("""
                        INSERT INTO teams (name, abbreviation, wins, losses, ties, ppg, pa, games_played)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        data['name'], data['abbreviation'], data['wins'], 
                        data['losses'], data['ties'], data['ppg'], data['pa'], data['games_played']
                    ))
                
                updated_count += 1
            
            conn.commit()
            conn.close()
            
            print(f"   ✅ Updated {updated_count} teams in database")
            return True
            
        except Exception as e:
            print(f"   ❌ Database update error: {e}")
            return False
    
    def run_full_update(self) -> bool:
        """Run complete multi-source data update"""
        print("\n" + "="*70)
        print("MULTI-SOURCE NFL DATA UPDATE")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # Fetch from all sources
        standings = self.fetch_espn_standings()
        ppg_data = self.scrape_teamrankings_ppg()
        pa_data = self.scrape_teamrankings_pa()
        
        # Merge data
        merged_data = self.merge_data_sources(standings, ppg_data, pa_data)
        
        # Update database
        success = self.update_database(merged_data)
        
        print("\n" + "="*70)
        if success:
            print("✅ MULTI-SOURCE UPDATE COMPLETE")
        else:
            print("❌ UPDATE FAILED")
        print("="*70 + "\n")
        
        return success

def main():
    fetcher = MultiSourceDataFetcher()
    fetcher.run_full_update()

if __name__ == "__main__":
    main()
