"""Test multiple teams"""
import requests

teams = ['KC', 'SF', 'BAL', 'PHI', 'DET', 'GB']
print("\n" + "="*60)
print("Testing Multiple Team Endpoints")
print("="*60)

for team_abbr in teams:
    r = requests.get(f'http://localhost:5000/api/hcl/teams/{team_abbr}')
    if r.ok:
        data = r.json()
        if data.get('success'):
            team = data['team']
            print(f"{team_abbr}: {team['wins']}-{team['losses']} ({team['ppg']} PPG, {team['epa_per_play']} EPA)")
        else:
            print(f"{team_abbr}: ERROR - {data.get('error')}")
    else:
        print(f"{team_abbr}: HTTP {r.status_code}")

print("="*60 + "\n")
