"""
Extensible NFL Data Fetcher - SCALABLE for 100+ stats
Uses JSONB column to store unlimited stats without schema changes

ADDING NEW STATS IS EASY:
1. Add fetcher function (fetch_passing_stats, fetch_rushing_stats, etc.)
2. Add to stats_definitions list
3. Add to merge_all_stats function
That's it! No database changes needed.
"""
import requests
from bs4 import BeautifulSoup
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

# ============================================================================
# TEAM MAPPINGS (same as before)
# ============================================================================
ALL_32_TEAMS = {
    "Arizona Cardinals": "ARI",
    "Atlanta Falcons": "ATL",
    "Baltimore Ravens": "BAL",
    "Buffalo Bills": "BUF",
    "Carolina Panthers": "CAR",
    "Chicago Bears": "CHI",
    "Cincinnati Bengals": "CIN",
    "Cleveland Browns": "CLE",
    "Dallas Cowboys": "DAL",
    "Denver Broncos": "DEN",
    "Detroit Lions": "DET",
    "Green Bay Packers": "GB",
    "Houston Texans": "HOU",
    "Indianapolis Colts": "IND",
    "Jacksonville Jaguars": "JAX",
    "Kansas City Chiefs": "KC",
    "Las Vegas Raiders": "LV",
    "Los Angeles Chargers": "LAC",
    "Los Angeles Rams": "LAR",
    "Miami Dolphins": "MIA",
    "Minnesota Vikings": "MIN",
    "New England Patriots": "NE",
    "New Orleans Saints": "NO",
    "New York Giants": "NYG",
    "New York Jets": "NYJ",
    "Philadelphia Eagles": "PHI",
    "Pittsburgh Steelers": "PIT",
    "San Francisco 49ers": "SF",
    "Seattle Seahawks": "SEA",
    "Tampa Bay Buccaneers": "TB",
    "Tennessee Titans": "TEN",
    "Washington Commanders": "WAS"
}

TEAM_NAME_MAPPINGS = {
    "LA Rams": "Los Angeles Rams",
    "LA Chargers": "Los Angeles Chargers",
    "Rams": "Los Angeles Rams",
    "Chargers": "Los Angeles Chargers",
    "Giants": "New York Giants",
    "Jets": "New York Jets",
    "Washington": "Washington Commanders",
    "Washington Football Team": "Washington Commanders",
    "San Francisco": "San Francisco 49ers",
    "49ers": "San Francisco 49ers"
}

# ============================================================================
# DATA FETCHERS (Add more as needed!)
# ============================================================================

def fetch_espn_standings():
    """Fetch standings from ESPN API"""
    print("\n1️⃣  Fetching standings from ESPN API...")
    try:
        url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        standings = {}
        season_type = data.get('season', {}).get('type', {}).get('name', 'Unknown')
        print(f"   📅 Season: {data.get('season', {}).get('year', '2025')} {season_type}")
        
        for event in data.get('events', []):
            for competition in event.get('competitions', []):
                for competitor in competition.get('competitors', []):
                    team = competitor.get('team', {})
                    team_name = team.get('displayName', '')
                    
                    normalized_name = TEAM_NAME_MAPPINGS.get(team_name, team_name)
                    abbreviation = ALL_32_TEAMS.get(normalized_name)
                    
                    if abbreviation:
                        record = competitor.get('records', [{}])[0]
                        summary = record.get('summary', '0-0')
                        
                        if '-' in summary:
                            wins, losses = summary.split('-')
                            standings[abbreviation] = {
                                'wins': int(wins),
                                'losses': int(losses),
                                'games_played': int(wins) + int(losses)
                            }
        
        print(f"   ✅ Got standings for {len(standings)} teams")
        return standings
    
    except Exception as e:
        print(f"   ⚠️  ESPN API failed: {e}")
        return {}

def fetch_teamrankings_stat(url, stat_name):
    """Generic TeamRankings scraper"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        stats = {}
        table = soup.find('table', class_='tr-table')
        if not table:
            return stats
        
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 2:
                team_link = cols[0].find('a')
                if team_link:
                    team_name = team_link.text.strip()
                    normalized_name = TEAM_NAME_MAPPINGS.get(team_name, team_name)
                    abbreviation = ALL_32_TEAMS.get(normalized_name)
                    
                    if abbreviation:
                        value = cols[1].text.strip()
                        try:
                            stats[abbreviation] = float(value)
                        except:
                            pass
        
        return stats
    
    except Exception as e:
        print(f"   ⚠️  Failed to scrape {stat_name}: {e}")
        return {}

def fetch_offensive_stats():
    """Fetch all offensive stats"""
    print("\n2️⃣  Fetching OFFENSIVE stats...")
    
    offensive_stats = {}
    
    # Points Per Game
    print("   📊 Points Per Game...")
    ppg = fetch_teamrankings_stat(
        "https://www.teamrankings.com/nfl/stat/points-per-game",
        "PPG"
    )
    print(f"      ✅ {len(ppg)} teams")
    
    # Total Yards Per Game
    print("   📊 Total Yards Per Game...")
    ypg = fetch_teamrankings_stat(
        "https://www.teamrankings.com/nfl/stat/yards-per-game",
        "YPG"
    )
    print(f"      ✅ {len(ypg)} teams")
    
    # Passing Yards Per Game
    print("   📊 Passing Yards Per Game...")
    pass_ypg = fetch_teamrankings_stat(
        "https://www.teamrankings.com/nfl/stat/passing-yards-per-game",
        "Pass YPG"
    )
    print(f"      ✅ {len(pass_ypg)} teams")
    
    # Rushing Yards Per Game
    print("   📊 Rushing Yards Per Game...")
    rush_ypg = fetch_teamrankings_stat(
        "https://www.teamrankings.com/nfl/stat/rushing-yards-per-game",
        "Rush YPG"
    )
    print(f"      ✅ {len(rush_ypg)} teams")
    
    # Merge all offensive stats
    for team_abbr in ALL_32_TEAMS.values():
        offensive_stats[team_abbr] = {
            'points_per_game': ppg.get(team_abbr),
            'yards_per_game': ypg.get(team_abbr),
            'passing_yards_per_game': pass_ypg.get(team_abbr),
            'rushing_yards_per_game': rush_ypg.get(team_abbr)
        }
    
    return offensive_stats

def fetch_defensive_stats():
    """Fetch all defensive stats"""
    print("\n3️⃣  Fetching DEFENSIVE stats...")
    
    defensive_stats = {}
    
    # Points Allowed Per Game
    print("   📊 Points Allowed Per Game...")
    pa = fetch_teamrankings_stat(
        "https://www.teamrankings.com/nfl/stat/opponent-points-per-game",
        "PA"
    )
    print(f"      ✅ {len(pa)} teams")
    
    # Yards Allowed Per Game
    print("   📊 Yards Allowed Per Game...")
    ya = fetch_teamrankings_stat(
        "https://www.teamrankings.com/nfl/stat/opponent-yards-per-game",
        "Yards Allowed"
    )
    print(f"      ✅ {len(ya)} teams")
    
    # Merge all defensive stats
    for team_abbr in ALL_32_TEAMS.values():
        defensive_stats[team_abbr] = {
            'points_allowed_per_game': pa.get(team_abbr),
            'yards_allowed_per_game': ya.get(team_abbr)
        }
    
    return defensive_stats

# ============================================================================
# DATA MERGING
# ============================================================================

def merge_all_stats(espn_standings, offensive_stats, defensive_stats):
    """Merge all stats into JSONB structure"""
    print("\n4️⃣  Merging all stats...")
    
    merged = {}
    complete_count = 0
    
    for team_name, team_abbr in ALL_32_TEAMS.items():
        # Start with team basics
        team_data = {
            'name': team_name,
            'abbreviation': team_abbr,
            'stats': {}
        }
        
        # Add record stats
        if team_abbr in espn_standings:
            team_data['wins'] = espn_standings[team_abbr]['wins']
            team_data['losses'] = espn_standings[team_abbr]['losses']
            team_data['games_played'] = espn_standings[team_abbr]['games_played']
            team_data['stats']['record'] = espn_standings[team_abbr]
        else:
            team_data['wins'] = 0
            team_data['losses'] = 0
            team_data['games_played'] = 0
            team_data['stats']['record'] = {'wins': 0, 'losses': 0, 'games_played': 0}
        
        # Add offensive stats
        if team_abbr in offensive_stats:
            team_data['stats']['offense'] = offensive_stats[team_abbr]
            # Calculate totals
            ppg = offensive_stats[team_abbr].get('points_per_game')
            if ppg and team_data['games_played'] > 0:
                team_data['stats']['offense']['total_points'] = round(ppg * team_data['games_played'], 1)
        
        # Add defensive stats
        if team_abbr in defensive_stats:
            team_data['stats']['defense'] = defensive_stats[team_abbr]
            # Calculate totals
            pa = defensive_stats[team_abbr].get('points_allowed_per_game')
            if pa and team_data['games_played'] > 0:
                team_data['stats']['defense']['total_points_allowed'] = round(pa * team_data['games_played'], 1)
        
        # Keep legacy columns for backward compatibility
        if 'offense' in team_data['stats']:
            team_data['ppg'] = team_data['stats']['offense'].get('points_per_game', 0)
        if 'defense' in team_data['stats']:
            team_data['pa'] = team_data['stats']['defense'].get('points_allowed_per_game', 0)
        
        # Check completeness
        has_offense = 'offense' in team_data['stats'] and team_data['stats']['offense'].get('points_per_game') is not None
        has_defense = 'defense' in team_data['stats'] and team_data['stats']['defense'].get('points_allowed_per_game') is not None
        
        if has_offense and has_defense:
            complete_count += 1
        
        merged[team_abbr] = team_data
    
    print(f"   ✅ {complete_count} teams have complete stats")
    print(f"   📊 Total stat categories: record, offense (4 stats), defense (2 stats)")
    
    return merged

# ============================================================================
# DATABASE UPDATE
# ============================================================================

def update_database(merged_data):
    """Update database with new JSONB stats"""
    print("\n5️⃣  Updating database...")
    
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'nfl_analytics'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'aprilv120')
    )
    cursor = conn.cursor()
    
    updated = 0
    inserted = 0
    
    for team_abbr, team_data in merged_data.items():
        # Convert stats to JSON string
        stats_json = json.dumps(team_data['stats'])
        
        # Try UPDATE first
        cursor.execute("""
            UPDATE teams 
            SET wins = %s, losses = %s, games_played = %s,
                ppg = %s, pa = %s, stats = %s::jsonb
            WHERE abbreviation = %s
        """, (
            team_data['wins'],
            team_data['losses'],
            team_data['games_played'],
            team_data.get('ppg', 0),
            team_data.get('pa', 0),
            stats_json,
            team_abbr
        ))
        
        if cursor.rowcount > 0:
            updated += 1
        else:
            # INSERT if not exists
            cursor.execute("""
                INSERT INTO teams (name, abbreviation, wins, losses, games_played, ppg, pa, stats)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            """, (
                team_data['name'],
                team_abbr,
                team_data['wins'],
                team_data['losses'],
                team_data['games_played'],
                team_data.get('ppg', 0),
                team_data.get('pa', 0),
                stats_json
            ))
            inserted += 1
    
    conn.commit()
    conn.close()
    
    print(f"   ✅ Updated {updated} teams, inserted {inserted} teams")
    
    return updated + inserted

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("EXTENSIBLE NFL DATA FETCHER")
    print("Scalable for 100+ stats using JSONB")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Fetch all data sources
    espn_standings = fetch_espn_standings()
    offensive_stats = fetch_offensive_stats()
    defensive_stats = fetch_defensive_stats()
    
    # Merge everything
    merged_data = merge_all_stats(espn_standings, offensive_stats, defensive_stats)
    
    # Update database
    total_updated = update_database(merged_data)
    
    print("\n" + "=" * 70)
    print("✅ EXTENSIBLE UPDATE COMPLETE")
    print("=" * 70)
    print(f"\n📊 Current stats tracked:")
    print("   • Record: wins, losses, games_played")
    print("   • Offense: PPG, yards/game, passing yards/game, rushing yards/game")
    print("   • Defense: PA, yards allowed/game")
    print(f"\n🎯 Ready to add MORE stats!")
    print("   Just add fetcher functions and update merge_all_stats()")
    print("   NO database schema changes needed!")

if __name__ == "__main__":
    main()
