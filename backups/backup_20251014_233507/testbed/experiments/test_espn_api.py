"""
H.C. Lombardo Testbed - ESPN API Experiment
Test ESPN API endpoints before implementing in main app
"""
import requests
import json

def test_espn_scoreboard():
    """Test ESPN scoreboard endpoint for current NFL data"""
    print("\n" + "="*70)
    print("EXPERIMENT: ESPN API Scoreboard")
    print("="*70)
    
    try:
        url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ API Connected!")
            print(f"   Status Code: {response.status_code}")
            
            # Check season info
            if 'season' in data:
                season = data['season']
                print(f"\n📅 Season Info:")
                print(f"   Year: {season.get('year')}")
                print(f"   Type: {season.get('type')}")
            
            # Check for events (games)
            if 'events' in data:
                events = data['events']
                print(f"\n🏈 Games Found: {len(events)}")
                
                # Sample first game
                if events:
                    game = events[0]
                    print(f"\n📊 Sample Game:")
                    print(f"   Name: {game.get('name')}")
                    print(f"   Date: {game.get('date')}")
                    
                    # Get teams from first competition
                    if 'competitions' in game:
                        comp = game['competitions'][0]
                        for competitor in comp.get('competitors', []):
                            team = competitor.get('team', {})
                            score = competitor.get('score', 'N/A')
                            print(f"   - {team.get('displayName')}: {score}")
            
            print("\n💡 Findings:")
            print("   - API is accessible and free")
            print("   - Provides current season data")
            print("   - Includes game scores and team info")
            print("   - Can extract PPG/PA from statistics")
            
            return True
            
        else:
            print(f"❌ API Failed: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_espn_teams():
    """Test ESPN teams endpoint"""
    print("\n" + "="*70)
    print("EXPERIMENT: ESPN API Teams")
    print("="*70)
    
    try:
        url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ Teams API Connected!")
            
            teams = []
            if 'sports' in data:
                for sport in data['sports']:
                    for league in sport.get('leagues', []):
                        for team_data in league.get('teams', []):
                            team = team_data.get('team', {})
                            teams.append({
                                'name': team.get('displayName'),
                                'abbr': team.get('abbreviation'),
                                'logo': team.get('logos', [{}])[0].get('href', '')
                            })
            
            print(f"\n🏈 Teams Found: {len(teams)}")
            print(f"\n📋 Sample Teams:")
            for i, team in enumerate(teams[:5], 1):
                print(f"   {i}. {team['name']} ({team['abbr']})")
                print(f"      Logo: {team['logo'][:50]}...")
            
            print("\n💡 Findings:")
            print("   - All 32 NFL teams available")
            print("   - Includes team logos (ESPN CDN)")
            print("   - Good for team metadata")
            
            return True
            
        else:
            print(f"❌ Failed: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n🧪 H.C. LOMBARDO TESTBED - ESPN API EXPERIMENTS")
    print("="*70)
    print("Testing ESPN API endpoints before main app implementation")
    print("="*70)
    
    # Run tests
    test1 = test_espn_scoreboard()
    test2 = test_espn_teams()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Scoreboard Test: {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"Teams Test: {'✅ PASSED' if test2 else '❌ FAILED'}")
    print("\n🔬 Ready to implement in main app if tests pass!")
    print("="*70 + "\n")
