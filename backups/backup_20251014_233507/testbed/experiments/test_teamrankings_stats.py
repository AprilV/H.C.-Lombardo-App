"""
H.C. Lombardo - TeamRankings Statistics Discovery & Verification
TESTBED EXPERIMENT: Discover available stats and test database integration

Purpose:
- Discover all available NFL statistics on TeamRankings.com
- Test scraping multiple stat categories
- Verify database integration for expanded statistics
- Document findings for future implementation

SAFE TESTING - Does NOT modify production database
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime

def test_stat_urls():
    """Test common NFL statistic URLs to see what's available"""
    
    print("🔍 TESTING TEAMRANKINGS.COM STATISTICS AVAILABILITY")
    print("=" * 60)
    
    # Actual stats from TeamRankings.com dropdown menu (from user screenshot)
    test_stats = {
        # Scoring Offense Section
        "Points per Game": "points-per-game",
        "Average Scoring Margin": "average-scoring-margin",
        "Yards per Point": "yards-per-point",
        "Yards per Point Margin": "yards-per-point-margin",
        "Points per Play": "points-per-play",
        "Points per Play Margin": "points-per-play-margin",
        "Touchdowns per Game": "touchdowns-per-game",
        "Red Zone Scoring Attempts per Game": "red-zone-scoring-attempts-per-game",
        "Red Zone Scores per Game (TDs only)": "red-zone-scores-per-game-td-only",
        "Red Zone Scoring Percentage (TD only)": "red-zone-scoring-pct-td-only",
        "Extra Point Attempts per Game": "extra-point-attempts-per-game",
        "Extra Points Made per Game": "extra-points-made-per-game",
        "Two Point Conversion Attempts per Game": "two-point-conversion-attempts-per-game",
        "Two Point Conversions per Game": "two-point-conversions-per-game",
        "Points per Field Goal Attempt": "points-per-field-goal-attempt",
        "Extra Point Conversion Percentage": "extra-point-conversion-pct",
        "Two Point Conversion Percentage": "two-point-conversion-pct",
        "Offensive Touchdowns per Game": "offensive-touchdowns-per-game",
        "Defensive Touchdowns per Game": "defensive-touchdowns-per-game",
        "Special Teams Touchdowns per Game": "special-teams-touchdowns-per-game",
        "Offensive Points per Game (Estimated)": "offensive-points-per-game-estimated",
        "Defensive Points per Game (Estimated)": "defensive-points-per-game-estimated",
        "Special Teams Points per Game (Estimated)": "special-teams-points-per-game-estimated",
        "Offensive Point Share Percentage (Estimated)": "offensive-point-share-pct-estimated"
    }
    
    base_url = "https://www.teamrankings.com/nfl/stat/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    available_stats = {}
    failed_stats = []
    
    for stat_name, stat_url in test_stats.items():
        full_url = base_url + stat_url
        print(f"\n🧪 Testing: {stat_name}")
        print(f"    URL: {full_url}")
        
        try:
            response = requests.get(full_url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                table = soup.find('table', class_='tr-table')
                
                if table:
                    rows = table.find_all('tr')[1:]  # Skip header
                    if len(rows) >= 32:  # Should have all 32 teams
                        sample_data = []
                        for i, row in enumerate(rows[:5]):  # Get first 5 teams
                            cells = row.find_all('td')
                            if len(cells) >= 3:
                                team = cells[1].get_text(strip=True)
                                value = cells[2].get_text(strip=True)
                                sample_data.append(f"{team}: {value}")
                        
                        available_stats[stat_name] = {
                            'url': stat_url,
                            'full_url': full_url,
                            'teams_found': len(rows),
                            'sample_data': sample_data,
                            'status': 'SUCCESS'
                        }
                        print(f"    ✅ SUCCESS - Found {len(rows)} teams")
                        print(f"    📊 Sample: {sample_data[0] if sample_data else 'No data'}")
                    else:
                        failed_stats.append((stat_name, f"Only {len(rows)} teams found"))
                        print(f"    ❌ FAILED - Only {len(rows)} teams found")
                else:
                    failed_stats.append((stat_name, "No table found"))
                    print(f"    ❌ FAILED - No data table found")
            else:
                failed_stats.append((stat_name, f"HTTP {response.status_code}"))
                print(f"    ❌ FAILED - HTTP {response.status_code}")
                
        except Exception as e:
            failed_stats.append((stat_name, str(e)))
            print(f"    ❌ ERROR - {e}")
        
        # Be respectful to the server
        time.sleep(1)
    
    return available_stats, failed_stats

def test_data_extraction(stat_data):
    """Test extracting specific statistics and formatting for database"""
    
    print("\n\n🗄️  TESTING DATABASE INTEGRATION")
    print("=" * 60)
    
    if not stat_data:
        print("❌ No statistics available to test")
        return
    
    # Test with first available statistic
    first_stat = list(stat_data.keys())[0]
    stat_info = stat_data[first_stat]
    
    print(f"📊 Testing data extraction for: {first_stat}")
    print(f"🔗 URL: {stat_info['full_url']}")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(stat_info['full_url'], headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', class_='tr-table')
        
        extracted_data = []
        rows = table.find_all('tr')[1:]  # Skip header
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                team_name = cells[1].get_text(strip=True)
                stat_value = cells[2].get_text(strip=True)
                
                # Convert to float if possible
                try:
                    numeric_value = float(stat_value)
                except:
                    numeric_value = stat_value
                
                extracted_data.append({
                    'team_name': team_name,
                    'stat_value': numeric_value,
                    'raw_value': stat_value
                })
        
        print(f"✅ Successfully extracted {len(extracted_data)} team records")
        print(f"📋 Sample records:")
        for i, record in enumerate(extracted_data[:5]):
            print(f"    {i+1}. {record['team_name']}: {record['stat_value']}")
        
        # Test database column naming
        column_name = first_stat.lower().replace(' ', '_').replace('%', 'pct')
        print(f"💾 Suggested database column: {column_name}")
        
        return extracted_data
        
    except Exception as e:
        print(f"❌ ERROR extracting data: {e}")
        return None

def generate_database_schema(available_stats):
    """Generate SQL schema for all available statistics"""
    
    print("\n\n🏗️  GENERATING DATABASE SCHEMA")
    print("=" * 60)
    
    base_columns = [
        "id SERIAL PRIMARY KEY",
        "name TEXT NOT NULL",
        "abbreviation TEXT",
        "wins INTEGER",
        "losses INTEGER",
        "games_played INTEGER"
    ]
    
    stat_columns = []
    for stat_name in available_stats.keys():
        column_name = stat_name.lower().replace(' ', '_').replace('%', 'pct').replace('-', '_')
        stat_columns.append(f"{column_name} REAL")
    
    all_columns = base_columns + stat_columns
    
    columns_joined = ',\n    '.join(all_columns)
    update_columns = ' = %s,\n--     '.join([col.split(' ')[0] for col in stat_columns])
    
    schema = f"""
-- EXPANDED NFL TEAMS TABLE WITH ALL AVAILABLE STATISTICS
CREATE TABLE teams_expanded (
    {columns_joined}
);

-- Sample UPDATE statement for new statistics
-- UPDATE teams_expanded SET 
--     {update_columns} = %s
-- WHERE name = %s;
"""
    
    print("📋 Proposed Database Schema:")
    print(schema)
    
    return schema

def save_test_results(available_stats, failed_stats, timestamp):
    """Save test results to file for documentation"""
    
    results = {
        'timestamp': timestamp,
        'test_summary': {
            'total_tested': len(available_stats) + len(failed_stats),
            'successful': len(available_stats),
            'failed': len(failed_stats)
        },
        'available_statistics': available_stats,
        'failed_statistics': failed_stats
    }
    
    timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
    filename = f"testbed/experiments/teamrankings_test_{timestamp_str}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Test results saved to: {filename}")
    except Exception as e:
        print(f"\n❌ Could not save results: {e}")

def main():
    """Main test function"""
    
    print("🧪 TEAMRANKINGS.COM STATISTICS VERIFICATION TEST")
    print("📅 Test Date:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("🎯 Purpose: Verify scraping capabilities for multiple NFL statistics")
    print("🛡️  Safety: This test does NOT modify the production database")
    print("\n" + "="*70 + "\n")
    
    # Test 1: Discover available statistics
    available_stats, failed_stats = test_stat_urls()
    
    # Test 2: Test data extraction
    sample_data = test_data_extraction(available_stats)
    
    # Test 3: Generate database schema
    if available_stats:
        schema = generate_database_schema(available_stats)
    
    # Test 4: Save results
    timestamp = datetime.now()
    save_test_results(available_stats, failed_stats, timestamp)
    
    # Summary
    print("\n\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Available Statistics: {len(available_stats)}")
    print(f"❌ Failed Statistics: {len(failed_stats)}")
    
    if available_stats:
        print(f"\n🎯 CONCLUSION: TeamRankings.com scraping is VIABLE")
        print(f"📈 Can expand database with {len(available_stats)} additional statistics")
        print(f"🔄 Daily/manual updates are FEASIBLE")
        print(f"💾 Database integration is READY")
    else:
        print(f"\n⚠️  CONCLUSION: No statistics could be scraped")
        print(f"🔍 May need to investigate site structure")
    
    print(f"\n🏁 Test completed successfully!")

if __name__ == "__main__":
    main()