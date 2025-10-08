"""
H.C. Lombardo - Live Data Scraper with Auto-Update
Scrapes REAL NFL stats from TeamRankings.com
Updates PostgreSQL database automatically
"""
import requests
from bs4 import BeautifulSoup
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime
from logging_config import setup_logging, log_activity

# Load environment variables
load_dotenv()

# Initialize logging
loggers = setup_logging()
log_activity('scraper', 'info', 'Scraper module initialized', source='TeamRankings.com')

def get_db_connection():
    """Get PostgreSQL database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'nfl_analytics'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '')
    )

def scrape_offense_stats():
    """Scrape PPG from TeamRankings.com"""
    url = "https://www.teamrankings.com/nfl/stat/points-per-game"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    log_activity('scraper', 'info', 'Starting offensive stats scrape', url=url)
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    teams = []
    table = soup.find('table', class_='tr-table')
    
    if table:
        rows = table.find_all('tr')[1:]  # Skip header
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                team_name = cells[1].get_text(strip=True)
                ppg = float(cells[2].get_text(strip=True))
                teams.append({'name': team_name, 'ppg': ppg})
    
    log_activity('scraper', 'info', 'Offensive stats scraped successfully', 
                teams_count=len(teams), stat_type='PPG')
    return teams

def scrape_defense_stats():
    """Scrape PA from TeamRankings.com"""
    url = "https://www.teamrankings.com/nfl/stat/opponent-points-per-game"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    log_activity('scraper', 'info', 'Starting defensive stats scrape', url=url)
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    teams = []
    table = soup.find('table', class_='tr-table')
    
    if table:
        rows = table.find_all('tr')[1:]  # Skip header
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                team_name = cells[1].get_text(strip=True)
                pa = float(cells[2].get_text(strip=True))
                teams.append({'name': team_name, 'pa': pa})
    
    print(f"✓ Scraped {len(teams)} teams - Defense (PA)")
    return teams

def combine_stats():
    """Combine offense and defense stats"""
    print("\n" + "="*70)
    print("SCRAPING LIVE NFL DATA FROM TEAMRANKINGS.COM")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    offense = scrape_offense_stats()
    defense = scrape_defense_stats()
    
    # Combine by team name
    combined = []
    for off_team in offense:
        # Find matching defense stats
        def_team = next((d for d in defense if d['name'] == off_team['name']), None)
        
        if def_team:
            combined.append({
                'name': off_team['name'],
                'ppg': off_team['ppg'],
                'pa': def_team['pa']
            })
    
    print(f"\n✓ Combined data for {len(combined)} teams")
    return combined

def get_team_abbreviation(team_name):
    """Map full team name to abbreviation"""
    abbr_map = {
        'Detroit Lions': 'DET', 'Indianapolis Colts': 'IND', 'Buffalo Bills': 'BUF',
        'Dallas Cowboys': 'DAL', 'San Francisco 49ers': 'SF', 'Baltimore Ravens': 'BAL',
        'Tampa Bay Buccaneers': 'TB', 'Washington Commanders': 'WAS', 'Green Bay Packers': 'GB',
        'Jacksonville Jaguars': 'JAX', 'Chicago Bears': 'CHI', 'New England Patriots': 'NE',
        'Kansas City Chiefs': 'KC', 'Philadelphia Eagles': 'PHI', 'Los Angeles Rams': 'LAR',
        'Minnesota Vikings': 'MIN', 'Pittsburgh Steelers': 'PIT', 'Denver Broncos': 'DEN',
        'New York Jets': 'NYJ', 'Houston Texans': 'HOU', 'Miami Dolphins': 'MIA',
        'Arizona Cardinals': 'ARI', 'Carolina Panthers': 'CAR', 'Atlanta Falcons': 'ATL',
        'Seattle Seahawks': 'SEA', 'Las Vegas Raiders': 'LV', 'Cincinnati Bengals': 'CIN',
        'Tennessee Titans': 'TEN', 'New York Giants': 'NYG', 'Cleveland Browns': 'CLE',
        'New Orleans Saints': 'NO', 'Los Angeles Chargers': 'LAC'
    }
    return abbr_map.get(team_name, team_name[:3].upper())

def update_database():
    """Scrape data and update PostgreSQL database"""
    teams = combine_stats()
    
    if not teams:
        print("❌ No data scraped, database not updated")
        return False
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM teams")
        
        # Insert fresh data
        for team in teams:
            cursor.execute("""
                INSERT INTO teams (name, abbreviation, wins, losses, ppg, pa, games_played)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                team['name'],
                get_team_abbreviation(team['name']),
                0,  # Wins not scraped (would need separate page)
                0,  # Losses not scraped
                round(team['ppg'], 1),
                round(team['pa'], 1),
                5   # Assuming 5 games played (current 2025 season)
            ))
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Database updated with {len(teams)} teams")
        print("="*70 + "\n")
        
        # Record update time
        record_update()
        
        return True
        
    except Exception as e:
        print(f"❌ Database update failed: {e}")
        return False

def record_update():
    """Record that an update occurred"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create metadata table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS update_metadata (
                id SERIAL PRIMARY KEY,
                last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO update_metadata (last_update) 
            VALUES (CURRENT_TIMESTAMP)
        """)
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"⚠️  Error recording update: {e}")

if __name__ == "__main__":
    # Update database with fresh data
    success = update_database()
    
    if success:
        print("✅ TeamRankings data refresh complete!")
    else:
        print("❌ Data refresh failed!")

