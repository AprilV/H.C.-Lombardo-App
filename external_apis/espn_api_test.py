#!/usr/bin/env python3
"""
ESPN API Integration (Free, No Key Required)
Alternative to API-SPORTS for live NFL data
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

class ESPNNFLApi:
    """ESPN NFL API wrapper (free, no authentication required)"""
    
    def __init__(self):
        self.base_url = "https://site.web.api.espn.com/apis/site/v2/sports/football/nfl"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_teams(self) -> List[Dict]:
        """Get all NFL teams from ESPN"""
        try:
            url = f"{self.base_url}/teams"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            teams = []
            
            if 'sports' in data and len(data['sports']) > 0:
                leagues = data['sports'][0].get('leagues', [])
                if leagues:
                    for team_data in leagues[0].get('teams', []):
                        team = team_data.get('team', {})
                        teams.append({
                            'id': team.get('id'),
                            'name': team.get('displayName'),
                            'abbreviation': team.get('abbreviation'),
                            'logo': team.get('logos', [{}])[0].get('href', ''),
                            'color': team.get('color', ''),
                            'record': self._extract_record(team)
                        })
            
            return teams
            
        except Exception as e:
            print(f"ESPN API Error (teams): {e}")
            return []
    
    def get_team_stats(self, team_id: int) -> Dict:
        """Get team statistics (limited data from ESPN)"""
        try:
            # ESPN doesn't have detailed stats API, so we'll get basic info
            teams = self.get_teams()
            
            for team in teams:
                if team['id'] == str(team_id):
                    return {
                        "team_info": {
                            "external_id": team_id,
                            "name": team['name'],
                            "abbreviation": team['abbreviation'],
                            "data_source": "ESPN API (Free)",
                            "retrieved_at": datetime.now().isoformat()
                        },
                        "season_record": team.get('record', {}),
                        "note": "ESPN provides limited stats compared to premium APIs"
                    }
            
            return {"error": f"Team {team_id} not found"}
            
        except Exception as e:
            return {"error": f"ESPN API error: {e}"}
    
    def get_scoreboard(self) -> Dict:
        """Get current NFL scoreboard"""
        try:
            url = f"{self.base_url}/scoreboard"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            games = []
            
            for event in data.get('events', []):
                game_info = {
                    'id': event.get('id'),
                    'name': event.get('name'),
                    'date': event.get('date'),
                    'status': event.get('status', {}).get('type', {}).get('name'),
                    'competitors': []
                }
                
                for competitor in event.get('competitions', [{}])[0].get('competitors', []):
                    team = competitor.get('team', {})
                    game_info['competitors'].append({
                        'team': team.get('displayName'),
                        'abbreviation': team.get('abbreviation'),
                        'score': competitor.get('score'),
                        'home_away': competitor.get('homeAway')
                    })
                
                games.append(game_info)
            
            return {
                "scoreboard": games,
                "data_source": "ESPN API (Free)",
                "retrieved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"ESPN scoreboard error: {e}"}
    
    def _extract_record(self, team_data: Dict) -> Dict:
        """Extract team record from ESPN data"""
        try:
            # ESPN record format varies, try to extract wins/losses
            record = team_data.get('record', {})
            if 'items' in record:
                overall = next((item for item in record['items'] if item.get('type') == 'total'), {})
                stats = overall.get('stats', [])
                
                wins = next((stat['value'] for stat in stats if stat['name'] == 'wins'), 0)
                losses = next((stat['value'] for stat in stats if stat['name'] == 'losses'), 0)
                
                return {
                    'wins': wins,
                    'losses': losses,
                    'games_played': wins + losses,
                    'win_percentage': wins / (wins + losses) if (wins + losses) > 0 else 0
                }
        except:
            pass
        
        return {'wins': 0, 'losses': 0, 'games_played': 0, 'win_percentage': 0}

def test_espn_api():
    """Test ESPN API functionality"""
    print("🏈 Testing ESPN NFL API (Free)")
    print("=" * 40)
    
    api = ESPNNFLApi()
    
    # Test teams
    print("1️⃣ Getting NFL teams...")
    teams = api.get_teams()
    
    if teams:
        print(f"✅ Found {len(teams)} teams")
        for team in teams[:5]:  # Show first 5
            record = team.get('record', {})
            wins = record.get('wins', 0)
            losses = record.get('losses', 0)
            print(f"   {team['name']} ({team['abbreviation']}) - {wins}-{losses}")
    else:
        print("❌ No teams found")
    
    # Test scoreboard
    print("\n2️⃣ Getting current scoreboard...")
    scoreboard = api.get_scoreboard()
    
    if 'error' not in scoreboard:
        games = scoreboard.get('scoreboard', [])
        print(f"✅ Found {len(games)} games")
        for game in games[:3]:  # Show first 3
            print(f"   {game.get('name', 'Unknown matchup')} - {game.get('status', 'Unknown')}")
    else:
        print(f"❌ Scoreboard error: {scoreboard['error']}")
    
    # Test team stats for a known team (assuming team ID 1 exists)
    if teams:
        print("\n3️⃣ Getting team stats...")
        team_id = teams[0]['id']
        stats = api.get_team_stats(int(team_id))
        
        if 'error' not in stats:
            team_info = stats.get('team_info', {})
            print(f"✅ Stats for {team_info.get('name', 'Unknown team')}")
            print(f"   Source: {team_info.get('data_source', 'Unknown')}")
        else:
            print(f"❌ Stats error: {stats['error']}")
    
    print("\n🎯 ESPN API Summary:")
    print("✅ Free to use (no API key required)")
    print("✅ Basic team info and scores")
    print("❌ Limited statistics compared to premium APIs")
    print("❌ No betting odds/lines")
    print("💡 Good for basic NFL data without API costs")

def main():
    """Run ESPN API test"""
    test_espn_api()
    
    print("\n" + "=" * 50)
    print("🔄 Want to switch to ESPN API for live data?")
    print("💡 Pros: Free, no API key needed")
    print("💡 Cons: Limited data, no betting lines")
    print("🎯 Your current mock data might be more complete!")

if __name__ == "__main__":
    main()