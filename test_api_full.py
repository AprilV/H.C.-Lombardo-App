import requests
import json
import time

# Wait for server to be ready
time.sleep(3)

try:
    # Test the API endpoint
    response = requests.get('http://127.0.0.1:5000/api/hcl/teams/ATL?season=2024', timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nSuccess: {data.get('success')}")
        
        if data.get('success') and data.get('team'):
            team_data = data['team']
            print(f"\nTeam: {team_data.get('team')}")
            print(f"Season: {team_data.get('season')}")
            print(f"Games Played: {team_data.get('games_played')}")
            print(f"Wins: {team_data.get('wins')}")
            print(f"PPG: {team_data.get('ppg')}")
            print(f"Total Yards/Game: {team_data.get('total_yards_per_game')}")
            print(f"Passing Yards/Game: {team_data.get('passing_yards_per_game')}")
            print(f"Rushing Yards/Game: {team_data.get('rushing_yards_per_game')}")
            
            # Count how many stats are available
            total_stats = len([k for k in team_data.keys() if team_data[k] is not None])
            print(f"\nTotal non-null stats: {total_stats}")
            
            # Show all available stats
            print("\nAll stats:")
            for key, value in sorted(team_data.items()):
                if value is not None:
                    print(f"  {key}: {value}")
        else:
            print(f"\nError: {data.get('error')}")
    else:
        print(f"HTTP Error: {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"Error: {e}")
