#!/usr/bin/env python3
"""
Complete NFL Teams Loader
Add all 32 NFL teams to both databases
"""

import sqlite3
from datetime import datetime

def get_all_32_nfl_teams():
    """Complete list of all 32 NFL teams with details"""
    return [
        # AFC East
        ("Buffalo Bills", "BUF", "AFC", "East", "Buffalo", "#00338D", "#C60C30"),
        ("Miami Dolphins", "MIA", "AFC", "East", "Miami", "#008E97", "#FC4C02"),
        ("New England Patriots", "NE", "AFC", "East", "Foxborough", "#002244", "#C60C30"),
        ("New York Jets", "NYJ", "AFC", "East", "East Rutherford", "#125740", "#FFFFFF"),
        
        # AFC North
        ("Baltimore Ravens", "BAL", "AFC", "North", "Baltimore", "#241773", "#9E7C0C"),
        ("Cincinnati Bengals", "CIN", "AFC", "North", "Cincinnati", "#FB4F14", "#000000"),
        ("Cleveland Browns", "CLE", "AFC", "North", "Cleveland", "#311D00", "#FF3C00"),
        ("Pittsburgh Steelers", "PIT", "AFC", "North", "Pittsburgh", "#FFB612", "#101820"),
        
        # AFC South
        ("Houston Texans", "HOU", "AFC", "South", "Houston", "#03202F", "#A71930"),
        ("Indianapolis Colts", "IND", "AFC", "South", "Indianapolis", "#002C5F", "#A2AAAD"),
        ("Jacksonville Jaguars", "JAX", "AFC", "South", "Jacksonville", "#006778", "#D7A22A"),
        ("Tennessee Titans", "TEN", "AFC", "South", "Nashville", "#0C2340", "#4B92DB"),
        
        # AFC West
        ("Denver Broncos", "DEN", "AFC", "West", "Denver", "#FB4F14", "#002244"),
        ("Kansas City Chiefs", "KC", "AFC", "West", "Kansas City", "#E31837", "#FFB81C"),
        ("Las Vegas Raiders", "LV", "AFC", "West", "Las Vegas", "#000000", "#A5ACAF"),
        ("Los Angeles Chargers", "LAC", "AFC", "West", "Los Angeles", "#0080C6", "#FFC20E"),
        
        # NFC East
        ("Dallas Cowboys", "DAL", "NFC", "East", "Arlington", "#041E42", "#869397"),
        ("New York Giants", "NYG", "NFC", "East", "East Rutherford", "#0B2265", "#A71930"),
        ("Philadelphia Eagles", "PHI", "NFC", "East", "Philadelphia", "#004C54", "#A5ACAF"),
        ("Washington Commanders", "WSH", "NFC", "East", "Landover", "#5A1414", "#FFB612"),
        
        # NFC North
        ("Chicago Bears", "CHI", "NFC", "North", "Chicago", "#0B162A", "#C83803"),
        ("Detroit Lions", "DET", "NFC", "North", "Detroit", "#0076B6", "#B0B7BC"),
        ("Green Bay Packers", "GB", "NFC", "North", "Green Bay", "#203731", "#FFB612"),
        ("Minnesota Vikings", "MIN", "NFC", "North", "Minneapolis", "#4F2683", "#FFC62F"),
        
        # NFC South
        ("Atlanta Falcons", "ATL", "NFC", "South", "Atlanta", "#A71930", "#000000"),
        ("Carolina Panthers", "CAR", "NFC", "South", "Charlotte", "#0085CA", "#101820"),
        ("New Orleans Saints", "NO", "NFC", "South", "New Orleans", "#D3BC8D", "#101820"),
        ("Tampa Bay Buccaneers", "TB", "NFC", "South", "Tampa", "#D50A0A", "#FF7900"),
        
        # NFC West
        ("Arizona Cardinals", "ARI", "NFC", "West", "Glendale", "#97233F", "#000000"),
        ("Los Angeles Rams", "LAR", "NFC", "West", "Los Angeles", "#003594", "#FFA300"),
        ("San Francisco 49ers", "SF", "NFC", "West", "San Francisco", "#AA0000", "#B3995D"),
        ("Seattle Seahawks", "SEA", "NFC", "West", "Seattle", "#002244", "#69BE28"),
    ]

def load_teams_to_main_database():
    """Load all teams to main database"""
    print("🏈 Loading Teams to Main Database...")
    
    try:
        from nfl_database_utils import NFLDatabaseManager
        db = NFLDatabaseManager()
        
        teams_data = get_all_32_nfl_teams()
        added_count = 0
        
        for name, abbr, conference, division, city, primary_color, secondary_color in teams_data:
            try:
                team_id = db.add_team(
                    name=name,
                    abbreviation=abbr,
                    division=division,
                    conference=conference,
                    city=city
                )
                added_count += 1
                print(f"   ✅ Added: {name} ({abbr})")
                
            except Exception as e:
                if "UNIQUE constraint failed" in str(e):
                    print(f"   ⏭️ Exists: {name} ({abbr})")
                else:
                    print(f"   ❌ Error adding {name}: {e}")
        
        print(f"\n📊 Main Database: {added_count} teams processed")
        
        # Verify final count
        all_teams = db.get_teams()
        print(f"📈 Total teams in database: {len(all_teams)}")
        
        return len(all_teams)
        
    except Exception as e:
        print(f"❌ Error with main database: {e}")
        return 0

def load_teams_to_user_schema():
    """Load all teams to user schema database"""
    print("\n🗃️ Loading Teams to User Schema Database...")
    
    try:
        conn = sqlite3.connect("user_schema_nfl.db")
        cursor = conn.cursor()
        
        teams_data = get_all_32_nfl_teams()
        added_count = 0
        
        for name, abbr, conference, division, city, primary_color, secondary_color in teams_data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO Teams (name, abbreviation, conference, division)
                    VALUES (?, ?, ?, ?)
                ''', (name, abbr, conference, division))
                
                if cursor.rowcount > 0:
                    added_count += 1
                    print(f"   ✅ Added: {name} ({abbr})")
                else:
                    print(f"   ⏭️ Exists: {name} ({abbr})")
                    
            except Exception as e:
                print(f"   ❌ Error adding {name}: {e}")
        
        conn.commit()
        
        # Verify final count
        cursor.execute("SELECT COUNT(*) FROM Teams")
        total_count = cursor.fetchone()[0]
        
        print(f"\n📊 User Schema: {added_count} new teams added")
        print(f"📈 Total teams in database: {total_count}")
        
        conn.close()
        return total_count
        
    except Exception as e:
        print(f"❌ Error with user schema database: {e}")
        return 0

def verify_all_teams_loaded():
    """Verify all 32 teams are loaded"""
    print("\n🔍 Verification Check")
    print("=" * 25)
    
    # Check main database
    try:
        from nfl_database_utils import NFLDatabaseManager
        db = NFLDatabaseManager()
        main_teams = db.get_teams()
        main_count = len(main_teams)
    except:
        main_count = 0
    
    # Check user schema
    try:
        conn = sqlite3.connect("user_schema_nfl.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Teams")
        user_count = cursor.fetchone()[0]
        conn.close()
    except:
        user_count = 0
    
    print(f"📊 Main Database: {main_count}/32 teams ({main_count/32*100:.1f}%)")
    print(f"📊 User Schema: {user_count}/32 teams ({user_count/32*100:.1f}%)")
    
    if main_count == 32 and user_count == 32:
        print("\n🎉 SUCCESS! All 32 NFL teams loaded in both databases!")
        return True
    else:
        missing = 32 - min(main_count, user_count)
        print(f"\n⚠️ Still missing {missing} teams in at least one database")
        return False

def show_division_breakdown():
    """Show teams by division"""
    print("\n📋 Division Breakdown (After Loading)")
    print("=" * 40)
    
    try:
        from nfl_database_utils import NFLDatabaseManager
        db = NFLDatabaseManager()
        teams = db.get_teams()
        
        # Group by conference and division
        divisions = {}
        for team in teams:
            conf = team['conference']
            div = team['division']
            key = f"{conf} {div}"
            
            if key not in divisions:
                divisions[key] = []
            divisions[key].append(f"{team['name']} ({team['abbreviation']})")
        
        for division, team_list in sorted(divisions.items()):
            print(f"\n🏈 {division} ({len(team_list)} teams):")
            for team in sorted(team_list):
                print(f"   {team}")
                
    except Exception as e:
        print(f"❌ Error showing breakdown: {e}")

def main():
    """Load all 32 NFL teams"""
    print("🏈 Complete NFL Teams Loader")
    print("Adding All 32 Teams to Databases")
    print("=" * 50)
    
    print("📊 Current Status: 6/32 teams (18.8%)")
    print("🎯 Target: 32/32 teams (100%)")
    print("\n🚀 Starting team loading process...")
    
    # Load to both databases
    main_count = load_teams_to_main_database()
    user_count = load_teams_to_user_schema()
    
    # Verify success
    all_loaded = verify_all_teams_loaded()
    
    if all_loaded:
        show_division_breakdown()
        print("\n🏆 COMPLETE! Your NFL databases now have all 32 teams!")
        print("✅ Ready for full league analysis and betting predictions")
    else:
        print("\n🔄 Some teams may need manual addition")
        print("💡 Check error messages above for details")
    
    print(f"\n🎯 Next Steps:")
    print("• Test with: python nfl_analysis_tool.py")
    print("• Run launcher.py → Option 15 for full analysis")
    print("• All 32 teams now available for betting predictions!")

if __name__ == "__main__":
    main()