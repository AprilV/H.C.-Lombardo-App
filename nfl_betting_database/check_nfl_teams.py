#!/usr/bin/env python3
"""
NFL Teams Checker
Check which teams are included in the database and system
"""

def check_current_teams():
    """Check teams in current database"""
    print("🏈 NFL Teams in Current Database")
    print("=" * 40)
    
    try:
        from nfl_database_utils import NFLDatabaseManager
        db = NFLDatabaseManager()
        teams = db.get_teams()
        
        print(f"📊 Total Teams: {len(teams)}")
        print("\n🏪 Current Teams:")
        
        # Group by conference
        afc_teams = [team for team in teams if team['conference'] == 'AFC']
        nfc_teams = [team for team in teams if team['conference'] == 'NFC']
        
        print(f"\n🔷 AFC Conference ({len(afc_teams)} teams):")
        for team in afc_teams:
            print(f"   {team['name']} ({team['abbreviation']}) - {team['division']}")
        
        print(f"\n🔶 NFC Conference ({len(nfc_teams)} teams):")
        for team in nfc_teams:
            print(f"   {team['name']} ({team['abbreviation']}) - {team['division']}")
            
        return teams
        
    except Exception as e:
        print(f"❌ Error checking database teams: {e}")
        return []

def check_user_schema_teams():
    """Check teams in user schema database"""
    print(f"\n🗃️ NFL Teams in User Schema Database")
    print("=" * 45)
    
    try:
        import sqlite3
        conn = sqlite3.connect("user_schema_nfl.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM Teams ORDER BY conference, division, name")
        teams = cursor.fetchall()
        
        print(f"📊 Total Teams: {len(teams)}")
        
        # Group by conference
        afc_teams = [team for team in teams if team['conference'] == 'AFC']
        nfc_teams = [team for team in teams if team['conference'] == 'NFC']
        
        print(f"\n🔷 AFC Conference ({len(afc_teams)} teams):")
        for team in afc_teams:
            print(f"   {team['name']} ({team['abbreviation']}) - {team['division']}")
        
        print(f"\n🔶 NFC Conference ({len(nfc_teams)} teams):")
        for team in nfc_teams:
            print(f"   {team['name']} ({team['abbreviation']}) - {team['division']}")
        
        conn.close()
        return list(teams)
        
    except Exception as e:
        print(f"❌ Error checking user schema: {e}")
        return []

def show_all_32_nfl_teams():
    """Show complete list of all 32 NFL teams"""
    print(f"\n📋 Complete NFL Team List (All 32 Teams)")
    print("=" * 45)
    
    all_nfl_teams = {
        "AFC": {
            "East": [
                ("Buffalo Bills", "BUF"),
                ("Miami Dolphins", "MIA"), 
                ("New England Patriots", "NE"),
                ("New York Jets", "NYJ")
            ],
            "North": [
                ("Baltimore Ravens", "BAL"),
                ("Cincinnati Bengals", "CIN"),
                ("Cleveland Browns", "CLE"), 
                ("Pittsburgh Steelers", "PIT")
            ],
            "South": [
                ("Houston Texans", "HOU"),
                ("Indianapolis Colts", "IND"),
                ("Jacksonville Jaguars", "JAX"),
                ("Tennessee Titans", "TEN")
            ],
            "West": [
                ("Denver Broncos", "DEN"),
                ("Kansas City Chiefs", "KC"),
                ("Las Vegas Raiders", "LV"),
                ("Los Angeles Chargers", "LAC")
            ]
        },
        "NFC": {
            "East": [
                ("Dallas Cowboys", "DAL"),
                ("New York Giants", "NYG"),
                ("Philadelphia Eagles", "PHI"),
                ("Washington Commanders", "WSH")
            ],
            "North": [
                ("Chicago Bears", "CHI"),
                ("Detroit Lions", "DET"),
                ("Green Bay Packers", "GB"),
                ("Minnesota Vikings", "MIN")
            ],
            "South": [
                ("Atlanta Falcons", "ATL"),
                ("Carolina Panthers", "CAR"),
                ("New Orleans Saints", "NO"),
                ("Tampa Bay Buccaneers", "TB")
            ],
            "West": [
                ("Arizona Cardinals", "ARI"),
                ("Los Angeles Rams", "LAR"),
                ("San Francisco 49ers", "SF"),
                ("Seattle Seahawks", "SEA")
            ]
        }
    }
    
    total_teams = 0
    for conference, divisions in all_nfl_teams.items():
        print(f"\n🏈 {conference} Conference:")
        for division, teams in divisions.items():
            print(f"\n   {division} Division:")
            for name, abbr in teams:
                print(f"     {name} ({abbr})")
                total_teams += 1
    
    print(f"\n📊 Total: {total_teams} teams")
    return all_nfl_teams

def compare_coverage(current_teams, all_teams):
    """Compare current teams vs all NFL teams"""
    print(f"\n🔍 Coverage Analysis")
    print("=" * 25)
    
    current_abbrs = {team['abbreviation'] if isinstance(team, dict) else team['abbreviation'] for team in current_teams}
    
    all_abbrs = set()
    for conference, divisions in all_teams.items():
        for division, teams in divisions.items():
            for name, abbr in teams:
                all_abbrs.add(abbr)
    
    missing_teams = all_abbrs - current_abbrs
    coverage_pct = (len(current_abbrs) / len(all_abbrs)) * 100
    
    print(f"📊 Current Coverage: {len(current_abbrs)}/32 teams ({coverage_pct:.1f}%)")
    
    if missing_teams:
        print(f"\n❌ Missing Teams ({len(missing_teams)}):")
        # Get full names for missing teams
        for conference, divisions in all_teams.items():
            for division, teams in divisions.items():
                for name, abbr in teams:
                    if abbr in missing_teams:
                        print(f"   {name} ({abbr}) - {conference} {division}")
    else:
        print("\n✅ All 32 NFL teams are included!")

def main():
    """Main team checker"""
    print("🏈 NFL Teams Coverage Analysis")
    print("H.C. Lombardo App Database Check")
    print("=" * 50)
    
    # Check current databases
    current_teams = check_current_teams()
    user_schema_teams = check_user_schema_teams()
    
    # Show all 32 teams
    all_teams = show_all_32_nfl_teams()
    
    # Compare coverage
    if current_teams:
        print(f"\n📈 Main Database Analysis:")
        compare_coverage(current_teams, all_teams)
    
    if user_schema_teams:
        print(f"\n📈 User Schema Database Analysis:")
        compare_coverage(user_schema_teams, all_teams)
    
    print(f"\n🎯 Summary:")
    print("The current databases have sample teams for development.")
    print("Would you like me to add all 32 NFL teams?")

if __name__ == "__main__":
    main()