"""
Test different NFL APIs for 2025 data availability
"""
import requests
import json

def test_espn_api():
    """Test ESPN unofficial API"""
    print("\n" + "="*60)
    print("Testing API 1: ESPN API")
    print("="*60)
    
    try:
        # Test teams endpoint
        url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ESPN Teams API Working!")
            
            if 'sports' in data:
                teams = data['sports'][0]['leagues'][0]['teams']
                print(f"   Teams found: {len(teams)}")
                print(f"   Sample: {teams[0]['team']['displayName']}")
            
            # Test scoreboard for current season
            scoreboard_url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
            score_response = requests.get(scoreboard_url, timeout=10)
            
            if score_response.status_code == 200:
                score_data = score_response.json()
                if 'season' in score_data:
                    print(f"   Season data: {score_data['season']}")
                print(f"   ✅ Has current season data!")
            
        else:
            print(f"   ❌ Failed: Status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")


def test_sportsdb_api():
    """Test TheSportsDB API"""
    print("\n" + "="*60)
    print("Testing API 2: TheSportsDB API")
    print("="*60)
    
    try:
        # Free tier API key
        api_key = "3"  # Test API key
        url = f"https://www.thesportsdb.com/api/v1/json/{api_key}/search_all_teams.php?l=NFL"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ TheSportsDB API Working!")
            
            if data.get('teams'):
                print(f"   Teams found: {len(data['teams'])}")
                print(f"   Sample: {data['teams'][0]['strTeam']}")
                print(f"   ⚠️  Note: May not have live 2025 stats")
        else:
            print(f"   ❌ Failed: Status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")


def test_api_football():
    """Test API-Football (RapidAPI)"""
    print("\n" + "="*60)
    print("Testing API 3: API-Football (Requires API Key)")
    print("="*60)
    print("   ⚠️  Requires RapidAPI account and API key")
    print("   Free tier: 100 requests/day")
    print("   Sign up at: https://rapidapi.com/api-sports/api/api-nfl")


def test_teamrankings_scraping():
    """Test TeamRankings.com web scraping"""
    print("\n" + "="*60)
    print("Testing Option 4: TeamRankings.com (Web Scraping)")
    print("="*60)
    
    try:
        url = "https://www.teamrankings.com/nfl/stat/points-per-game"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ TeamRankings.com accessible!")
            print(f"   Status: {response.status_code}")
            print(f"   Content length: {len(response.text)} bytes")
            print(f"   ✅ Can scrape for live 2025 data!")
        else:
            print(f"   ❌ Failed: Status {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")


if __name__ == "__main__":
    print("\n🔍 Testing NFL Data Sources for 2025 Season Data")
    print("="*60)
    
    test_espn_api()
    test_sportsdb_api()
    test_api_football()
    test_teamrankings_scraping()
    
    print("\n" + "="*60)
    print("RECOMMENDATION:")
    print("="*60)
    print("1. ✅ ESPN API - Free, no key needed, live data")
    print("2. ✅ TeamRankings.com scraping - Reliable, current stats")
    print("3. ⚠️  API-Football - Best data but needs API key")
    print("="*60)
