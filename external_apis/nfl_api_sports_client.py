#!/usr/bin/env python3
"""
API-SPORTS NFL API Integration
Connect to external API to fetch team stats and betting odds
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

class APIConfiguration:
    """Configuration class for API-SPORTS NFL API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "YOUR_API_KEY_HERE"  # Replace with actual API key
        self.base_url = "https://v1.american-football.api-sports.io"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "v1.american-football.api-sports.io"
        }
        self.timeout = 30
        self.rate_limit_delay = 1  # Seconds between requests

class NFLAPIClient:
    """Client for API-SPORTS NFL API"""
    
    def __init__(self, api_key: str = None):
        self.config = APIConfiguration(api_key)
        self.session = requests.Session()
        self.session.headers.update(self.config.headers)
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.config.rate_limit_delay:
            time.sleep(self.config.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request with error handling"""
        self._rate_limit()
        
        url = f"{self.config.base_url}/{endpoint}"
        
        try:
            response = self.session.get(
                url, 
                params=params, 
                timeout=self.config.timeout
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Check API-specific errors
            if not data.get("response"):
                print(f"Warning: No data returned from {endpoint}")
                return {"response": [], "errors": data.get("errors", [])}
            
            return data
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                print("Rate limit exceeded. Waiting...")
                time.sleep(60)  # Wait 1 minute for rate limit reset
                return self._make_request(endpoint, params)  # Retry
            else:
                raise Exception(f"HTTP Error {response.status_code}: {e}")
        
        except requests.exceptions.Timeout:
            raise Exception("Request timeout - API may be slow")
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
        
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response from API")

def get_team_stats(season: int, team_id: int, api_key: str = None) -> Dict[str, Any]:
    """
    Fetch team statistics for a given season
    
    Args:
        season (int): NFL season year (e.g., 2024)
        team_id (int): Team ID from API-SPORTS
        api_key (str): API key for authentication
    
    Returns:
        Dict containing team statistics
    """
    client = NFLAPIClient(api_key)
    
    try:
        # Get team statistics
        stats_data = client._make_request("teams/statistics", {
            "season": season,
            "team": team_id
        })
        
        if not stats_data["response"]:
            return {"error": f"No statistics found for team {team_id} in season {season}"}
        
        # Parse team statistics
        team_stats = stats_data["response"][0]
        
        # Clean and structure the data
        parsed_stats = {
            "team_info": {
                "team_id": team_stats.get("team", {}).get("id"),
                "team_name": team_stats.get("team", {}).get("name"),
                "season": season,
                "last_updated": datetime.now().isoformat()
            },
            "offensive_stats": {
                "total_yards_per_game": team_stats.get("games", {}).get("played", {}).get("total", 0),
                "passing_yards_per_game": team_stats.get("points", {}).get("for", {}).get("average", {}).get("total", 0),
                "rushing_yards_per_game": team_stats.get("points", {}).get("against", {}).get("average", {}).get("total", 0),
                "points_per_game": team_stats.get("points", {}).get("for", {}).get("average", {}).get("total", 0),
                "touchdowns": team_stats.get("points", {}).get("for", {}).get("total", {}).get("total", 0)
            },
            "defensive_stats": {
                "points_allowed_per_game": team_stats.get("points", {}).get("against", {}).get("average", {}).get("total", 0),
                "yards_allowed_per_game": 0,  # Would need to calculate from detailed stats
                "turnovers_forced": 0,
                "sacks": 0
            },
            "record": {
                "wins": team_stats.get("games", {}).get("wins", {}).get("total", 0),
                "losses": team_stats.get("games", {}).get("loses", {}).get("total", 0),
                "ties": team_stats.get("games", {}).get("draws", {}).get("total", 0),
                "games_played": team_stats.get("games", {}).get("played", {}).get("total", 0)
            }
        }
        
        return parsed_stats
        
    except Exception as e:
        return {"error": f"Failed to fetch team stats: {str(e)}"}

def get_game_odds(game_id: int, api_key: str = None) -> Dict[str, Any]:
    """
    Fetch betting odds for a specific game
    
    Args:
        game_id (int): Game ID from API-SPORTS
        api_key (str): API key for authentication
    
    Returns:
        Dict containing betting odds information
    """
    client = NFLAPIClient(api_key)
    
    try:
        # Get game odds
        odds_data = client._make_request("odds", {
            "game": game_id
        })
        
        if not odds_data["response"]:
            return {"error": f"No odds found for game {game_id}"}
        
        # Parse odds data
        game_odds = odds_data["response"][0]
        
        # Extract bookmaker odds (usually multiple bookmakers available)
        bookmakers = game_odds.get("bookmakers", [])
        
        if not bookmakers:
            return {"error": "No bookmaker odds available"}
        
        # Use first bookmaker's odds (or could aggregate multiple)
        primary_odds = bookmakers[0]
        
        # Parse different bet types
        bets = primary_odds.get("bets", [])
        
        parsed_odds = {
            "game_info": {
                "game_id": game_id,
                "home_team": game_odds.get("game", {}).get("teams", {}).get("home", {}).get("name"),
                "away_team": game_odds.get("game", {}).get("teams", {}).get("away", {}).get("name"),
                "game_date": game_odds.get("game", {}).get("date"),
                "status": game_odds.get("game", {}).get("status", {}).get("long"),
                "last_updated": datetime.now().isoformat()
            },
            "bookmaker": {
                "name": primary_odds.get("name"),
                "id": primary_odds.get("id")
            },
            "betting_lines": {}
        }
        
        # Parse different types of bets
        for bet in bets:
            bet_name = bet.get("name", "").lower()
            
            if "spread" in bet_name or "handicap" in bet_name:
                # Point spread
                values = bet.get("values", [])
                if len(values) >= 2:
                    parsed_odds["betting_lines"]["spread"] = {
                        "home_spread": values[0].get("handicap"),
                        "home_odds": values[0].get("odd"),
                        "away_spread": values[1].get("handicap"),
                        "away_odds": values[1].get("odd")
                    }
            
            elif "totals" in bet_name or "over/under" in bet_name:
                # Over/Under totals
                values = bet.get("values", [])
                if len(values) >= 2:
                    parsed_odds["betting_lines"]["total"] = {
                        "total_points": values[0].get("handicap"),
                        "over_odds": values[0].get("odd"),
                        "under_odds": values[1].get("odd")
                    }
            
            elif "moneyline" in bet_name or "match winner" in bet_name:
                # Moneyline odds
                values = bet.get("values", [])
                if len(values) >= 2:
                    parsed_odds["betting_lines"]["moneyline"] = {
                        "home_odds": values[0].get("odd"),
                        "away_odds": values[1].get("odd")
                    }
        
        return parsed_odds
        
    except Exception as e:
        return {"error": f"Failed to fetch game odds: {str(e)}"}

def get_available_teams(season: int, api_key: str = None) -> List[Dict]:
    """Get list of available teams for testing"""
    client = NFLAPIClient(api_key)
    
    try:
        teams_data = client._make_request("teams", {"season": season})
        
        teams = []
        for team in teams_data["response"]:
            teams.append({
                "id": team.get("id"),
                "name": team.get("name"),
                "code": team.get("code"),
                "city": team.get("city")
            })
        
        return teams
        
    except Exception as e:
        print(f"Failed to fetch teams: {e}")
        return []

def get_recent_games(season: int, api_key: str = None) -> List[Dict]:
    """Get recent games for testing odds"""
    client = NFLAPIClient(api_key)
    
    try:
        games_data = client._make_request("games", {
            "season": season,
            "type": "regular"  # regular season games
        })
        
        games = []
        for game in games_data["response"][:5]:  # Get first 5 games
            games.append({
                "id": game.get("id"),
                "home_team": game.get("teams", {}).get("home", {}).get("name"),
                "away_team": game.get("teams", {}).get("away", {}).get("name"),
                "date": game.get("date"),
                "status": game.get("status", {}).get("long")
            })
        
        return games
        
    except Exception as e:
        print(f"Failed to fetch games: {e}")
        return []

def demo_api_integration(api_key: str = None):
    """Demonstrate API integration with example data"""
    
    print("🏈 API-SPORTS NFL API Integration Demo")
    print("=" * 50)
    
    # Note about API key
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("⚠️  NOTE: Using demo mode - replace 'YOUR_API_KEY_HERE' with actual API key")
        print("   Get your free API key at: https://rapidapi.com/api-sports/api/american-football/")
        print()
        
        # Demo with mock data since we don't have real API key
        print("📋 Demo Team Stats (Mock Data):")
        demo_team_stats = {
            "team_info": {
                "team_id": 1,
                "team_name": "Kansas City Chiefs",
                "season": 2024,
                "last_updated": datetime.now().isoformat()
            },
            "offensive_stats": {
                "total_yards_per_game": 385.2,
                "passing_yards_per_game": 267.8,
                "rushing_yards_per_game": 117.4,
                "points_per_game": 28.5,
                "touchdowns": 45
            },
            "defensive_stats": {
                "points_allowed_per_game": 19.2,
                "yards_allowed_per_game": 312.6,
                "turnovers_forced": 23,
                "sacks": 41
            },
            "record": {
                "wins": 11,
                "losses": 6,
                "ties": 0,
                "games_played": 17
            }
        }
        
        print(json.dumps(demo_team_stats, indent=2))
        
        print("\n🎰 Demo Game Odds (Mock Data):")
        demo_game_odds = {
            "game_info": {
                "game_id": 12345,
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "game_date": "2024-09-07T20:20:00",
                "status": "Not Started",
                "last_updated": datetime.now().isoformat()
            },
            "bookmaker": {
                "name": "DraftKings",
                "id": 8
            },
            "betting_lines": {
                "spread": {
                    "home_spread": -2.5,
                    "home_odds": "-110",
                    "away_spread": 2.5,
                    "away_odds": "-110"
                },
                "total": {
                    "total_points": 54.5,
                    "over_odds": "-110",
                    "under_odds": "-110"
                },
                "moneyline": {
                    "home_odds": "-140",
                    "away_odds": "+120"
                }
            }
        }
        
        print(json.dumps(demo_game_odds, indent=2))
        
        return
    
    # Real API integration (when API key is provided)
    season = 2024
    
    try:
        print("🔍 Fetching available teams...")
        teams = get_available_teams(season, api_key)
        if teams:
            print(f"Found {len(teams)} teams")
            test_team = teams[0]  # Use first team for testing
            
            print(f"\n📊 Fetching stats for {test_team['name']}...")
            team_stats = get_team_stats(season, test_team['id'], api_key)
            print(json.dumps(team_stats, indent=2))
        
        print("\n🎮 Fetching recent games...")
        games = get_recent_games(season, api_key)
        if games:
            test_game = games[0]  # Use first game for testing
            
            print(f"\n🎰 Fetching odds for {test_game['away_team']} @ {test_game['home_team']}...")
            game_odds = get_game_odds(test_game['id'], api_key)
            print(json.dumps(game_odds, indent=2))
        
    except Exception as e:
        print(f"❌ API Integration Error: {e}")

if __name__ == "__main__":
    # You can set your API key here or pass it as an environment variable
    api_key = "YOUR_API_KEY_HERE"  # Replace with actual API key
    
    demo_api_integration(api_key)