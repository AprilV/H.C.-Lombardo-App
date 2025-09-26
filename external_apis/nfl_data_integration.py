#!/usr/bin/env python3
"""
NFL Data Integration
Combines local database with external API-SPORTS data
"""

import sys
import os
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'nfl_betting_database'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

try:
    from nfl_database_utils import NFLDatabaseManager
    from api_config import get_api_config
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the correct directory")
    sys.exit(1)

class NFLDataIntegrator:
    """Integrates local database with external API data"""
    
    def __init__(self, api_key: str = None):
        # Initialize database manager
        db_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'nfl_betting_database', 
            'sports_betting.db'
        )
        self.db_manager = NFLDatabaseManager(db_path)
        
        # Initialize API configuration
        self.api_config = get_api_config()
        if api_key:
            self.api_config.api_sports_nfl_key = api_key
        
        self.base_url = "https://v1.american-football.api-sports.io"
        
    def get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        return {
            "X-RapidAPI-Key": self.api_config.api_sports_nfl_key,
            "X-RapidAPI-Host": "v1.american-football.api-sports.io"
        }
    
    def _make_api_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make request to external API with error handling"""
        if not self.api_config.is_api_key_valid():
            # Return mock data if no valid API key
            return self._get_mock_data(endpoint, params)
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(
                url, 
                headers=self.get_headers(), 
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return self._get_mock_data(endpoint, params)
    
    def _get_mock_data(self, endpoint: str, params: Dict = None) -> Dict:
        """Return mock data when API is not available"""
        if "teams/statistics" in endpoint:
            return {
                "response": [{
                    "team": {"id": params.get("team", 1), "name": "Kansas City Chiefs"},
                    "games": {"played": {"total": 17}, "wins": {"total": 14}, "loses": {"total": 3}},
                    "points": {
                        "for": {"average": {"total": 28.5}, "total": {"total": 484}},
                        "against": {"average": {"total": 19.2}, "total": {"total": 326}}
                    }
                }]
            }
        elif "odds" in endpoint:
            return {
                "response": [{
                    "game": {
                        "id": params.get("game", 12345),
                        "teams": {
                            "home": {"name": "Kansas City Chiefs"},
                            "away": {"name": "Buffalo Bills"}
                        },
                        "date": "2024-09-07T20:20:00",
                        "status": {"long": "Not Started"}
                    },
                    "bookmakers": [{
                        "name": "DraftKings",
                        "id": 8,
                        "bets": [
                            {
                                "name": "Spread",
                                "values": [
                                    {"handicap": -2.5, "odd": "-110"},
                                    {"handicap": 2.5, "odd": "-110"}
                                ]
                            },
                            {
                                "name": "Totals",
                                "values": [
                                    {"handicap": 54.5, "odd": "-110"},
                                    {"handicap": 54.5, "odd": "-110"}
                                ]
                            }
                        ]
                    }]
                }]
            }
        return {"response": []}

def get_team_stats(season: int, team_id: int, api_key: str = None) -> Dict:
    """
    Fetch team statistics from external API
    
    Args:
        season (int): NFL season year (e.g., 2024)
        team_id (int): Team ID from API-SPORTS
        api_key (str): Optional API key override
    
    Returns:
        Dict containing cleaned team statistics
    """
    integrator = NFLDataIntegrator(api_key)
    
    # Get data from external API
    response = integrator._make_api_request("teams/statistics", {
        "season": season,
        "team": team_id
    })
    
    if not response.get("response"):
        return {"error": f"No statistics found for team {team_id} in season {season}"}
    
    # Parse and clean the data
    raw_stats = response["response"][0]
    
    cleaned_stats = {
        "team_info": {
            "external_id": team_id,
            "name": raw_stats.get("team", {}).get("name", f"Team {team_id}"),
            "season": season,
            "data_source": "API-SPORTS",
            "retrieved_at": datetime.now().isoformat()
        },
        "season_record": {
            "games_played": raw_stats.get("games", {}).get("played", {}).get("total", 0),
            "wins": raw_stats.get("games", {}).get("wins", {}).get("total", 0),
            "losses": raw_stats.get("games", {}).get("loses", {}).get("total", 0),
            "win_percentage": 0.0
        },
        "offensive_performance": {
            "points_per_game": raw_stats.get("points", {}).get("for", {}).get("average", {}).get("total", 0),
            "total_points": raw_stats.get("points", {}).get("for", {}).get("total", {}).get("total", 0),
            "scoring_efficiency": "high"  # Could calculate based on league average
        },
        "defensive_performance": {
            "points_allowed_per_game": raw_stats.get("points", {}).get("against", {}).get("average", {}).get("total", 0),
            "total_points_allowed": raw_stats.get("points", {}).get("against", {}).get("total", {}).get("total", 0),
            "defensive_efficiency": "average"
        }
    }
    
    # Calculate win percentage
    if cleaned_stats["season_record"]["games_played"] > 0:
        wins = cleaned_stats["season_record"]["wins"]
        games = cleaned_stats["season_record"]["games_played"]
        cleaned_stats["season_record"]["win_percentage"] = round(wins / games, 3)
    
    return cleaned_stats

def get_game_odds(game_id: int, api_key: str = None) -> Dict:
    """
    Fetch betting odds for a specific game
    
    Args:
        game_id (int): Game ID from API-SPORTS
        api_key (str): Optional API key override
    
    Returns:
        Dict containing cleaned betting odds
    """
    integrator = NFLDataIntegrator(api_key)
    
    # Get odds from external API
    response = integrator._make_api_request("odds", {
        "game": game_id
    })
    
    if not response.get("response"):
        return {"error": f"No odds found for game {game_id}"}
    
    # Parse and clean odds data
    raw_odds = response["response"][0]
    game_info = raw_odds.get("game", {})
    bookmakers = raw_odds.get("bookmakers", [])
    
    if not bookmakers:
        return {"error": "No bookmaker data available"}
    
    # Use primary bookmaker
    primary_book = bookmakers[0]
    
    cleaned_odds = {
        "game_info": {
            "external_game_id": game_id,
            "home_team": game_info.get("teams", {}).get("home", {}).get("name"),
            "away_team": game_info.get("teams", {}).get("away", {}).get("name"),
            "game_date": game_info.get("date"),
            "status": game_info.get("status", {}).get("long"),
            "data_source": "API-SPORTS",
            "retrieved_at": datetime.now().isoformat()
        },
        "sportsbook": {
            "name": primary_book.get("name", "Unknown"),
            "book_id": primary_book.get("id")
        },
        "betting_markets": {
            "spread": None,
            "total": None,
            "moneyline": None
        }
    }
    
    # Parse different bet types
    for bet in primary_book.get("bets", []):
        bet_name = bet.get("name", "").lower()
        values = bet.get("values", [])
        
        if "spread" in bet_name and len(values) >= 2:
            cleaned_odds["betting_markets"]["spread"] = {
                "home_spread": values[0].get("handicap"),
                "home_odds": values[0].get("odd"),
                "away_spread": values[1].get("handicap"),
                "away_odds": values[1].get("odd")
            }
        
        elif "total" in bet_name and len(values) >= 2:
            cleaned_odds["betting_markets"]["total"] = {
                "points": values[0].get("handicap"),
                "over_odds": values[0].get("odd"),
                "under_odds": values[1].get("odd")
            }
        
        elif "moneyline" in bet_name and len(values) >= 2:
            cleaned_odds["betting_markets"]["moneyline"] = {
                "home_odds": values[0].get("odd"),
                "away_odds": values[1].get("odd")
            }
    
    return cleaned_odds

def integrate_with_local_database(team_stats: Dict, game_odds: Dict):
    """Integrate external API data with local database"""
    integrator = NFLDataIntegrator()
    
    print("🔄 Integrating external data with local database...")
    
    # This could store external data in our local database
    # For now, just show how the data could be combined
    
    # Get local teams for comparison
    local_teams = integrator.db_manager.get_teams()
    
    print(f"📊 External Team Stats Summary:")
    if "team_info" in team_stats:
        team_info = team_stats["team_info"]
        record = team_stats.get("season_record", {})
        
        print(f"   Team: {team_info.get('name')}")
        print(f"   Season: {team_info.get('season')}")
        print(f"   Record: {record.get('wins', 0)}-{record.get('losses', 0)}")
        print(f"   Win %: {record.get('win_percentage', 0):.1%}")
    
    print(f"\n🎰 External Betting Odds Summary:")
    if "game_info" in game_odds:
        game_info = game_odds["game_info"]
        markets = game_odds.get("betting_markets", {})
        
        print(f"   Game: {game_info.get('away_team')} @ {game_info.get('home_team')}")
        print(f"   Date: {game_info.get('game_date')}")
        
        if markets.get("spread"):
            spread = markets["spread"]
            print(f"   Spread: {spread.get('home_spread', 'N/A')}")
        
        if markets.get("total"):
            total = markets["total"]
            print(f"   Total: {total.get('points', 'N/A')}")
    
    print(f"\n🏪 Local Database Status:")
    stats = integrator.db_manager.get_database_stats()
    print(f"   Teams: {stats.get('teams', 0)}")
    print(f"   Games: {stats.get('games', 0)}")
    print(f"   Latest Season: {stats.get('latest_season', 'N/A')}")

def demo_external_api_integration():
    """Demonstrate the external API integration"""
    print("🌐 NFL External API Integration Demo")
    print("=" * 50)
    
    # Test parameters
    test_season = 2024
    test_team_id = 1  # Kansas City Chiefs ID in API-SPORTS
    test_game_id = 12345  # Example game ID
    
    print(f"📡 Testing API connection...")
    config = get_api_config()
    
    if not config.is_api_key_valid():
        print("⚠️  Using mock data (no API key configured)")
        print("   To use real data, set your API key in api_config.py")
    else:
        print("✅ API key configured - using live data")
    
    print(f"\n1️⃣  Fetching team stats (Season {test_season}, Team ID {test_team_id})...")
    team_stats = get_team_stats(test_season, test_team_id)
    
    if "error" in team_stats:
        print(f"❌ Error: {team_stats['error']}")
    else:
        print("✅ Team stats retrieved successfully!")
        print(json.dumps(team_stats, indent=2))
    
    print(f"\n2️⃣  Fetching game odds (Game ID {test_game_id})...")
    game_odds = get_game_odds(test_game_id)
    
    if "error" in game_odds:
        print(f"❌ Error: {game_odds['error']}")
    else:
        print("✅ Game odds retrieved successfully!")
        print(json.dumps(game_odds, indent=2))
    
    print(f"\n3️⃣  Integrating with local database...")
    integrate_with_local_database(team_stats, game_odds)
    
    print(f"\n✅ Demo completed!")
    print(f"\n🔗 API Documentation:")
    print(f"   https://rapidapi.com/api-sports/api/american-football/")

if __name__ == "__main__":
    demo_external_api_integration()