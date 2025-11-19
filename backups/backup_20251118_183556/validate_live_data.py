"""
TESTBED: Live Data Validation System
Tests that the app is using LIVE data from ESPN API, not hardcoded data

This script:
1. Checks that NO hardcoded data scripts exist in production
2. Verifies database data is recent (updated within last 24 hours)
3. Compares database against ESPN API to ensure they match
4. FAILS LOUDLY if any hardcoded data is detected

Date: October 21, 2025
"""
import os
import sys
import psycopg2
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Dict, List, Tuple

load_dotenv()

# CRITICAL: List of files that should NEVER exist in production
FORBIDDEN_FILES = [
    'update_current_standings.py',
    'manual_update.py',
    'temp_update.py',
    'hardcoded_data.py',
    'test_data_update.py'
]

# ESPN API endpoint
ESPN_API = "http://site.api.espn.com/apis/v2/sports/football/nfl/standings"

class DataValidationError(Exception):
    """Raised when hardcoded data or stale data is detected"""
    pass


def check_forbidden_files() -> List[str]:
    """Check if any forbidden hardcoded data files exist"""
    found_files = []
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up from testbed
    
    for filename in FORBIDDEN_FILES:
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            found_files.append(filename)
    
    return found_files


def get_database_data() -> Dict[str, dict]:
    """Get all team data from database"""
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'nfl_analytics'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD')
    )
    
    cur = conn.cursor()
    cur.execute("""
        SELECT abbreviation, wins, losses, ties, last_updated
        FROM teams
        ORDER BY abbreviation
    """)
    
    teams = {}
    for row in cur.fetchall():
        abbr, wins, losses, ties, last_updated = row
        teams[abbr] = {
            'wins': wins,
            'losses': losses,
            'ties': ties,
            'last_updated': last_updated
        }
    
    cur.close()
    conn.close()
    
    return teams


def get_espn_data() -> Dict[str, dict]:
    """Get current data from ESPN API"""
    response = requests.get(ESPN_API)
    response.raise_for_status()
    data = response.json()
    
    teams = {}
    for team in data['children']:
        for standing in team['standings']['entries']:
            stats = standing['stats']
            abbr = standing['team']['abbreviation']
            
            # Find wins, losses, ties
            wins = next(s['value'] for s in stats if s['name'] == 'wins')
            losses = next(s['value'] for s in stats if s['name'] == 'losses')
            ties = next(s['value'] for s in stats if s['name'] == 'ties')
            
            teams[abbr] = {
                'wins': int(wins),
                'losses': int(losses),
                'ties': int(ties)
            }
    
    return teams


def validate_data_freshness(db_teams: Dict[str, dict]) -> Tuple[bool, str]:
    """Check if database data is recent (within last 24 hours)"""
    oldest_update = None
    
    for abbr, data in db_teams.items():
        if data['last_updated']:
            if oldest_update is None or data['last_updated'] < oldest_update:
                oldest_update = data['last_updated']
    
    if oldest_update is None:
        return False, "❌ No timestamp data found - database has never been updated!"
    
    cutoff = datetime.now() - timedelta(hours=24)
    
    if oldest_update < cutoff:
        hours_old = (datetime.now() - oldest_update).total_seconds() / 3600
        return False, f"❌ Data is STALE! Last update: {oldest_update} ({hours_old:.1f} hours ago)"
    
    return True, f"✅ Data is fresh (last update: {oldest_update})"


def compare_with_espn(db_teams: Dict[str, dict], espn_teams: Dict[str, dict]) -> Tuple[bool, List[str]]:
    """Compare database against ESPN API"""
    mismatches = []
    
    # Abbreviation mappings (ESPN vs Database)
    abbr_map = {
        'WSH': 'WAS'  # ESPN uses WSH, we use WAS for Washington
    }
    
    for espn_abbr in sorted(espn_teams.keys()):
        # Check if we need to map the abbreviation
        db_abbr = abbr_map.get(espn_abbr, espn_abbr)
        
        if db_abbr not in db_teams:
            mismatches.append(f"❌ {espn_abbr} (maps to {db_abbr}): Missing from database!")
            continue
        
        db = db_teams[db_abbr]
        espn = espn_teams[espn_abbr]
        
        if (db['wins'] != espn['wins'] or 
            db['losses'] != espn['losses'] or 
            db['ties'] != espn['ties']):
            mismatches.append(
                f"❌ {espn_abbr}: DB={db['wins']}-{db['losses']}-{db['ties']} "
                f"vs ESPN={espn['wins']}-{espn['losses']}-{espn['ties']}"
            )
    
    if mismatches:
        return False, mismatches
    
    return True, [f"✅ All {len(espn_teams)} teams match ESPN API"]


def run_validation() -> bool:
    """Run full validation suite"""
    print("=" * 80)
    print("LIVE DATA VALIDATION SYSTEM")
    print("=" * 80)
    print()
    
    all_passed = True
    
    # Test 1: Check for forbidden hardcoded files
    print("TEST 1: Checking for hardcoded data scripts...")
    forbidden = check_forbidden_files()
    if forbidden:
        print(f"❌ FAILED: Found forbidden files: {', '.join(forbidden)}")
        print("   These files contain hardcoded data and must be deleted!")
        all_passed = False
    else:
        print("✅ PASSED: No hardcoded data scripts found")
    print()
    
    # Test 2: Check data freshness
    print("TEST 2: Checking database data freshness...")
    try:
        db_teams = get_database_data()
        is_fresh, message = validate_data_freshness(db_teams)
        print(message)
        if not is_fresh:
            all_passed = False
    except Exception as e:
        print(f"❌ FAILED: Could not check database: {e}")
        all_passed = False
    print()
    
    # Test 3: Compare against ESPN API
    print("TEST 3: Comparing database against ESPN API...")
    try:
        espn_teams = get_espn_data()
        matches, messages = compare_with_espn(db_teams, espn_teams)
        
        for msg in messages:
            print(msg)
        
        if not matches:
            print()
            print("⚠️  DATABASE DOES NOT MATCH ESPN API!")
            print("⚠️  This indicates hardcoded or stale data!")
            all_passed = False
    except Exception as e:
        print(f"❌ FAILED: Could not compare with ESPN API: {e}")
        all_passed = False
    print()
    
    # Final verdict
    print("=" * 80)
    if all_passed:
        print("✅ ✅ ✅  ALL TESTS PASSED - LIVE DATA CONFIRMED  ✅ ✅ ✅")
        print()
        print("Your app is using LIVE data from ESPN API.")
        print("Safe to demonstrate or deploy!")
    else:
        print("❌ ❌ ❌  VALIDATION FAILED - HARDCODED DATA DETECTED  ❌ ❌ ❌")
        print()
        print("DO NOT demonstrate or deploy until this is fixed!")
        print("Run: python multi_source_data_fetcher.py")
    print("=" * 80)
    
    return all_passed


if __name__ == '__main__':
    try:
        success = run_validation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ VALIDATION ERROR: {e}")
        sys.exit(1)
