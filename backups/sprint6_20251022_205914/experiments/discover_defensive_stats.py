"""
H.C. Lombardo - Defensive Statistics Discovery
TESTBED EXPERIMENT: Auto-discover defensive stats from TeamRankings.com

Purpose:
- Automatically find all defensive statistics available
- Test defensive stat categories and subcategories
- Verify scraping capabilities for defensive metrics
- Document all available defensive data

SAFE TESTING - Does NOT modify production database
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

def discover_defensive_stats():
    """Systematically discover defensive statistics"""
    
    print("🛡️  DISCOVERING DEFENSIVE STATISTICS ON TEAMRANKINGS.COM")
    print("=" * 70)
    
    # Common defensive stat patterns to test
    defensive_patterns = {
        # Basic Defensive Stats
        "Opponent Points per Game": "opponent-points-per-game",
        "Opponent Total Yards per Game": "opponent-total-yards-per-game",
        "Opponent Passing Yards per Game": "opponent-passing-yards-per-game",
        "Opponent Rushing Yards per Game": "opponent-rushing-yards-per-game",
        
        # Defensive Efficiency
        "Opponent Yards per Point": "opponent-yards-per-point",
        "Opponent Points per Play": "opponent-points-per-play",
        "Opponent Yards per Play": "opponent-yards-per-play",
        
        # Turnovers & Takeaways
        "Opponent Turnovers per Game": "opponent-turnovers-per-game",
        "Interceptions per Game": "interceptions-per-game",
        "Fumbles Recovered per Game": "fumbles-recovered-per-game",
        "Defensive Turnovers per Game": "defensive-turnovers-per-game",
        "Takeaways per Game": "takeaways-per-game",
        
        # Red Zone Defense
        "Opponent Red Zone Scoring Attempts per Game": "opponent-red-zone-scoring-attempts-per-game",
        "Opponent Red Zone Scores per Game": "opponent-red-zone-scores-per-game",
        "Opponent Red Zone Scoring Percentage": "opponent-red-zone-scoring-pct",
        "Red Zone Defense Percentage": "red-zone-defense-pct",
        
        # Third Down Defense
        "Opponent Third Down Conversion Pct": "opponent-third-down-conversion-pct",
        "Third Down Defense Percentage": "third-down-defense-pct",
        "Opponent Third Down Attempts per Game": "opponent-third-down-attempts-per-game",
        
        # Sacks & Pressure
        "Sacks per Game": "sacks-per-game",
        "Sack Yards per Game": "sack-yards-per-game",
        "Quarterback Hits per Game": "quarterback-hits-per-game",
        
        # Passing Defense
        "Opponent Pass Attempts per Game": "opponent-pass-attempts-per-game",
        "Opponent Pass Completions per Game": "opponent-pass-completions-per-game",
        "Opponent Completion Percentage": "opponent-completion-pct",
        "Opponent Yards per Pass Attempt": "opponent-yards-per-pass-attempt",
        "Opponent Passing Touchdowns per Game": "opponent-passing-touchdowns-per-game",
        "Pass Interceptions per Game": "pass-interceptions-per-game",
        
        # Rushing Defense  
        "Opponent Rush Attempts per Game": "opponent-rush-attempts-per-game",
        "Opponent Yards per Rush Attempt": "opponent-yards-per-rush-attempt",
        "Opponent Rushing Touchdowns per Game": "opponent-rushing-touchdowns-per-game",
        
        # Penalties
        "Opponent Penalty Yards per Game": "opponent-penalty-yards-per-game",
        "Opponent Penalties per Game": "opponent-penalties-per-game",
        
        # Time of Possession Defense
        "Opponent Time of Possession": "opponent-time-of-possession",
        "Opponent Plays per Game": "opponent-plays-per-game",
        
        # Special Teams Defense
        "Opponent Punt Return Yards per Game": "opponent-punt-return-yards-per-game",
        "Opponent Kickoff Return Yards per Game": "opponent-kickoff-return-yards-per-game"
    }
    
    base_url = "https://www.teamrankings.com/nfl/stat/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    available_defensive_stats = {}
    failed_defensive_stats = []
    
    for stat_name, stat_url in defensive_patterns.items():
        full_url = base_url + stat_url
        print(f"\n🔍 Testing: {stat_name}")
        print(f"    URL: {full_url}")
        
        try:
            response = requests.get(full_url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                table = soup.find('table', class_='tr-table')
                
                if table:
                    rows = table.find_all('tr')[1:]  # Skip header
                    if len(rows) >= 30:  # Should have most/all 32 teams
                        sample_data = []
                        for i, row in enumerate(rows[:3]):  # Get first 3 teams
                            cells = row.find_all('td')
                            if len(cells) >= 3:
                                team = cells[1].get_text(strip=True)
                                value = cells[2].get_text(strip=True)
                                sample_data.append(f"{team}: {value}")
                        
                        available_defensive_stats[stat_name] = {
                            'url': stat_url,
                            'full_url': full_url,
                            'teams_found': len(rows),
                            'sample_data': sample_data,
                            'status': 'SUCCESS'
                        }
                        print(f"    ✅ SUCCESS - Found {len(rows)} teams")
                        print(f"    🛡️  Sample: {sample_data[0] if sample_data else 'No data'}")
                    else:
                        failed_defensive_stats.append((stat_name, f"Only {len(rows)} teams found"))
                        print(f"    ❌ FAILED - Only {len(rows)} teams found")
                else:
                    failed_defensive_stats.append((stat_name, "No table found"))
                    print(f"    ❌ FAILED - No data table found")
            else:
                failed_defensive_stats.append((stat_name, f"HTTP {response.status_code}"))
                print(f"    ❌ FAILED - HTTP {response.status_code}")
                
        except Exception as e:
            failed_defensive_stats.append((stat_name, str(e)))
            print(f"    ❌ ERROR - {e}")
        
        # Be respectful to the server
        time.sleep(1)
    
    return available_defensive_stats, failed_defensive_stats

def generate_defensive_database_schema(available_stats):
    """Generate SQL schema for defensive statistics"""
    
    print("\n\n🏗️  GENERATING DEFENSIVE DATABASE SCHEMA")
    print("=" * 70)
    
    base_columns = [
        "id SERIAL PRIMARY KEY",
        "name TEXT NOT NULL",
        "abbreviation TEXT"
    ]
    
    defensive_columns = []
    for stat_name in available_stats.keys():
        column_name = stat_name.lower().replace(' ', '_').replace('%', 'pct').replace('-', '_')
        defensive_columns.append(f"{column_name} REAL")
    
    all_columns = base_columns + defensive_columns
    columns_joined = ',\n    '.join(all_columns)
    
    schema = f"""
-- DEFENSIVE STATISTICS TABLE
CREATE TABLE defensive_stats (
    {columns_joined}
);

-- Sample INSERT for defensive stats
-- INSERT INTO defensive_stats (name, abbreviation, {', '.join([col.split(' ')[0] for col in defensive_columns])})
-- VALUES (%s, %s, {', '.join(['%s'] * len(defensive_columns))});
"""
    
    print("📋 Proposed Defensive Database Schema:")
    print(schema)
    
    return schema

def categorize_defensive_stats(available_stats):
    """Categorize defensive statistics by type"""
    
    print("\n\n📊 CATEGORIZING DEFENSIVE STATISTICS")
    print("=" * 70)
    
    categories = {
        "Basic Defense": [],
        "Turnover Defense": [],
        "Red Zone Defense": [],
        "Passing Defense": [],
        "Rushing Defense": [],
        "Third Down Defense": [],
        "Pressure Defense": [],
        "Special Teams Defense": [],
        "Other Defense": []
    }
    
    for stat_name in available_stats.keys():
        if any(word in stat_name.lower() for word in ['turnover', 'interception', 'fumble', 'takeaway']):
            categories["Turnover Defense"].append(stat_name)
        elif 'red zone' in stat_name.lower():
            categories["Red Zone Defense"].append(stat_name)
        elif any(word in stat_name.lower() for word in ['pass', 'completion', 'yards per pass']):
            categories["Passing Defense"].append(stat_name)
        elif any(word in stat_name.lower() for word in ['rush', 'yards per rush']):
            categories["Rushing Defense"].append(stat_name)
        elif 'third down' in stat_name.lower():
            categories["Third Down Defense"].append(stat_name)
        elif any(word in stat_name.lower() for word in ['sack', 'quarterback', 'pressure']):
            categories["Pressure Defense"].append(stat_name)
        elif any(word in stat_name.lower() for word in ['punt', 'kickoff', 'return']):
            categories["Special Teams Defense"].append(stat_name)
        elif any(word in stat_name.lower() for word in ['points', 'yards', 'total']):
            categories["Basic Defense"].append(stat_name)
        else:
            categories["Other Defense"].append(stat_name)
    
    for category, stats in categories.items():
        if stats:
            print(f"\n🛡️  {category}:")
            for stat in stats:
                print(f"    • {stat}")
    
    return categories

def save_defensive_results(available_stats, failed_stats, categories, timestamp):
    """Save defensive test results"""
    
    results = {
        'timestamp': timestamp,
        'test_type': 'defensive_statistics_discovery',
        'summary': {
            'total_tested': len(available_stats) + len(failed_stats),
            'successful': len(available_stats),
            'failed': len(failed_stats)
        },
        'available_defensive_stats': available_stats,
        'failed_defensive_stats': failed_stats,
        'stat_categories': categories
    }
    
    timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
    filename = f"testbed/experiments/defensive_stats_test_{timestamp_str}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Defensive test results saved to: {filename}")
    except Exception as e:
        print(f"\n❌ Could not save results: {e}")

def main():
    """Main defensive stats discovery function"""
    
    print("🛡️  TEAMRANKINGS.COM DEFENSIVE STATISTICS DISCOVERY")
    print("📅 Test Date:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("🎯 Purpose: Auto-discover all available defensive NFL statistics")
    print("🔍 Method: Systematic testing of defensive stat URL patterns")
    print("🛡️  Safety: This test does NOT modify the production database")
    print("\n" + "="*80 + "\n")
    
    # Discover defensive statistics
    available_stats, failed_stats = discover_defensive_stats()
    
    # Categorize the statistics
    if available_stats:
        categories = categorize_defensive_stats(available_stats)
        
        # Generate database schema
        schema = generate_defensive_database_schema(available_stats)
    else:
        categories = {}
    
    # Save results
    timestamp = datetime.now()
    save_defensive_results(available_stats, failed_stats, categories, timestamp)
    
    # Summary
    print("\n\n🛡️  DEFENSIVE STATS DISCOVERY SUMMARY")
    print("=" * 70)
    print(f"✅ Available Defensive Stats: {len(available_stats)}")
    print(f"❌ Failed Tests: {len(failed_stats)}")
    
    if available_stats:
        print(f"\n🎯 CONCLUSION: Defensive stats scraping is VIABLE")
        print(f"📈 Can create comprehensive defensive analytics")
        print(f"🛡️  Database ready for defensive metrics")
        print(f"🔄 Daily defensive updates are FEASIBLE")
        
        print(f"\n🏆 Top Defensive Categories Found:")
        if categories:
            for category, stats in categories.items():
                if stats:
                    print(f"    • {category}: {len(stats)} stats")
    else:
        print(f"\n⚠️  CONCLUSION: No defensive statistics found")
        print(f"🔍 May need different URL patterns")
    
    print(f"\n🏁 Defensive discovery completed!")

if __name__ == "__main__":
    main()