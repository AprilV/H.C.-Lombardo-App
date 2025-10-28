"""
Universal NFL Stat Fetcher
Fetches ANY stat from TeamRankings.com using stats_config.py
NO CODE CHANGES needed to add new stats - just update stats_config.py
"""
import requests
from bs4 import BeautifulSoup
from stats_config import AVAILABLE_STATS, get_stat_config
import time

# Team name normalization (same as multi_source_data_fetcher.py)
ALL_32_TEAMS = {
    "Arizona Cardinals": "ARI", "Atlanta Falcons": "ATL", "Baltimore Ravens": "BAL",
    "Buffalo Bills": "BUF", "Carolina Panthers": "CAR", "Chicago Bears": "CHI",
    "Cincinnati Bengals": "CIN", "Cleveland Browns": "CLE", "Dallas Cowboys": "DAL",
    "Denver Broncos": "DEN", "Detroit Lions": "DET", "Green Bay Packers": "GB",
    "Houston Texans": "HOU", "Indianapolis Colts": "IND", "Jacksonville Jaguars": "JAX",
    "Kansas City Chiefs": "KC", "Las Vegas Raiders": "LV", "Los Angeles Chargers": "LAC",
    "Los Angeles Rams": "LAR", "Miami Dolphins": "MIA", "Minnesota Vikings": "MIN",
    "New England Patriots": "NE", "New Orleans Saints": "NO", "New York Giants": "NYG",
    "New York Jets": "NYJ", "Philadelphia Eagles": "PHI", "Pittsburgh Steelers": "PIT",
    "San Francisco 49ers": "SF", "Seattle Seahawks": "SEA", "Tampa Bay Buccaneers": "TB",
    "Tennessee Titans": "TEN", "Washington Commanders": "WAS"
}

# NOTE: NFL teams can tie! Record format is W-L-T (e.g., "5-2-1" = 5 wins, 2 losses, 1 tie)

TEAM_NAME_MAPPINGS = {
    # TeamRankings short names
    "Indianapolis": "Indianapolis Colts",
    "Detroit": "Detroit Lions",
    "Dallas": "Dallas Cowboys",
    "Buffalo": "Buffalo Bills",
    "Seattle": "Seattle Seahawks",
    "Houston": "Houston Texans",
    "Denver": "Denver Broncos",
    "Minnesota": "Minnesota Vikings",
    "Kansas City": "Kansas City Chiefs",
    "Atlanta": "Atlanta Falcons",
    "Philadelphia": "Philadelphia Eagles",
    "Pittsburgh": "Pittsburgh Steelers",
    "Miami": "Miami Dolphins",
    "Baltimore": "Baltimore Ravens",
    "Cleveland": "Cleveland Browns",
    "Cincinnati": "Cincinnati Bengals",
    "Jacksonville": "Jacksonville Jaguars",
    "Tennessee": "Tennessee Titans",
    "Chicago": "Chicago Bears",
    "Green Bay": "Green Bay Packers",
    "Arizona": "Arizona Cardinals",
    "Carolina": "Carolina Panthers",
    "New Orleans": "New Orleans Saints",
    "Tampa Bay": "Tampa Bay Buccaneers",
    # Variations
    "LA Rams": "Los Angeles Rams",
    "LA Chargers": "Los Angeles Chargers",
    "Rams": "Los Angeles Rams", 
    "Chargers": "Los Angeles Chargers",
    "Giants": "New York Giants",
    "Jets": "New York Jets",
    "New York": "New York Giants",  # Default to Giants if just "New York"
    "NY Giants": "New York Giants",
    "NY Jets": "New York Jets",
    "New England": "New England Patriots",
    "Patriots": "New England Patriots",
    "Las Vegas": "Las Vegas Raiders",
    "Raiders": "Las Vegas Raiders",
    "49ers": "San Francisco 49ers",
    "San Francisco": "San Francisco 49ers",
    "Washington": "Washington Commanders",
    "Washington Football Team": "Washington Commanders"
}

def normalize_team_name(team_name):
    """Normalize team name to match our database"""
    team_name = team_name.strip()
    normalized = TEAM_NAME_MAPPINGS.get(team_name, team_name)
    return ALL_32_TEAMS.get(normalized)

def fetch_stat_from_teamrankings(category, stat_key):
    """
    Fetch ANY stat from TeamRankings.com
    
    Args:
        category (str): 'offense', 'defense', or 'special_teams'
        stat_key (str): The stat key from stats_config.py (e.g., 'points_per_game')
    
    Returns:
        dict: {team_abbreviation: stat_value} for all 32 teams
    """
    # Get stat configuration
    stat_config = get_stat_config(category, stat_key)
    
    if not stat_config:
        print(f"❌ Stat not found: {category}.{stat_key}")
        return {}
    
    url = f"https://www.teamrankings.com/nfl/stat/{stat_config['url_slug']}"
    
    print(f"📊 Fetching {stat_config['name']} from TeamRankings...")
    print(f"   URL: {url}")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='tr-table')
        
        if not table:
            print(f"❌ Could not find stats table")
            return {}
        
        stats = {}
        rows_processed = 0
        teams_not_found = []
        
        for row in table.find_all('tr')[1:]:  # Skip header row
            cols = row.find_all('td')
            if len(cols) >= 3:  # Need at least rank, team, stat
                # TeamRankings format: [Rank, Team, Stat Value, ...]
                team_name = cols[1].text.strip()  # Team is in column 1
                abbreviation = normalize_team_name(team_name)
                
                if abbreviation:
                    value_text = cols[2].text.strip()  # Stat value is in column 2
                    
                    # Parse value based on data type
                    try:
                        if stat_config['data_type'] == 'float':
                            stats[abbreviation] = float(value_text.replace(',', ''))
                        elif stat_config['data_type'] == 'int':
                            stats[abbreviation] = int(value_text.replace(',', ''))
                        elif stat_config['data_type'] == 'percentage':
                            # Remove % sign and convert to float
                            stats[abbreviation] = float(value_text.replace('%', '').strip())
                        elif stat_config['data_type'] == 'string':
                            stats[abbreviation] = value_text
                        
                        rows_processed += 1
                    except ValueError as e:
                        print(f"⚠️  Could not parse value '{value_text}' for {team_name}: {e}")
                else:
                    teams_not_found.append(team_name)
        
        if teams_not_found:
            print(f"   ⚠️  Could not normalize {len(teams_not_found)} team names: {teams_not_found[:5]}")
        
        print(f"   ✅ Got {stat_config['name']} for {rows_processed} teams")
        return stats
    
    except requests.RequestException as e:
        print(f"❌ Failed to fetch {stat_config['name']}: {e}")
        return {}
    except Exception as e:
        print(f"❌ Error processing {stat_config['name']}: {e}")
        return {}

def fetch_multiple_stats(stats_list, delay=1):
    """
    Fetch multiple stats at once
    
    Args:
        stats_list (list): List of tuples [(category, stat_key), ...]
        delay (int): Delay in seconds between requests (be nice to TeamRankings)
    
    Returns:
        dict: {stat_key: {team_abbreviation: value}}
    """
    all_stats = {}
    
    print(f"\n📥 Fetching {len(stats_list)} stats from TeamRankings.com...")
    print("=" * 70)
    
    for i, (category, stat_key) in enumerate(stats_list, 1):
        print(f"\n[{i}/{len(stats_list)}]")
        stat_data = fetch_stat_from_teamrankings(category, stat_key)
        
        if stat_data:
            all_stats[f"{category}.{stat_key}"] = stat_data
        
        # Be polite - don't hammer their server
        if i < len(stats_list):
            time.sleep(delay)
    
    print("\n" + "=" * 70)
    print(f"✅ Fetched {len(all_stats)} stats successfully")
    
    return all_stats

def get_all_offense_stats():
    """Fetch all offensive stats"""
    stats_list = [(f'offense', key) for key in AVAILABLE_STATS['offense'].keys()]
    return fetch_multiple_stats(stats_list)

def get_all_defense_stats():
    """Fetch all defensive stats"""
    stats_list = [('defense', key) for key in AVAILABLE_STATS['defense'].keys()]
    return fetch_multiple_stats(stats_list)

def get_all_special_teams_stats():
    """Fetch all special teams stats"""
    stats_list = [('special_teams', key) for key in AVAILABLE_STATS['special_teams'].keys()]
    return fetch_multiple_stats(stats_list)

def get_all_stats():
    """Fetch ALL 37 stats"""
    all_stats_list = []
    
    for category in ['offense', 'defense', 'special_teams']:
        for stat_key in AVAILABLE_STATS[category].keys():
            all_stats_list.append((category, stat_key))
    
    return fetch_multiple_stats(all_stats_list, delay=2)

# Test function
if __name__ == "__main__":
    print("=" * 70)
    print("UNIVERSAL STAT FETCHER TEST")
    print("=" * 70)
    
    # Test 1: Fetch single stat
    print("\nTest 1: Fetch Points Per Game")
    ppg = fetch_stat_from_teamrankings('offense', 'points_per_game')
    print(f"\nSample results:")
    for i, (team, value) in enumerate(list(ppg.items())[:5], 1):
        print(f"   {i}. {team}: {value}")
    
    # Test 2: Fetch multiple stats
    print("\n\nTest 2: Fetch 3 stats at once")
    stats = fetch_multiple_stats([
        ('offense', 'points_per_game'),
        ('defense', 'opponent_points_per_game'),
        ('offense', 'yards_per_game')
    ])
    
    print(f"\nFetched {len(stats)} stat categories")
    for stat_key in stats.keys():
        print(f"   - {stat_key}: {len(stats[stat_key])} teams")
    
    print("\nAll tests complete!")
    print("\nTo fetch a stat in your code:")
    print("   from universal_stat_fetcher import fetch_stat_from_teamrankings")
    print("   ppg_data = fetch_stat_from_teamrankings('offense', 'points_per_game')")
