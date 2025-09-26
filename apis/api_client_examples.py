#!/usr/bin/env python3
"""
API Client Examples
Examples showing how to use the Text Classification and NFL Betting APIs
"""

import requests
import json
from typing import Dict, List

class TextClassificationClient:
    """Client for Text Classification API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def classify_text(self, text: str, model_name: str = "distilbert") -> Dict:
        """Classify a single text"""
        response = requests.post(
            f"{self.base_url}/classify",
            json={"text": text, "model_name": model_name}
        )
        response.raise_for_status()
        return response.json()
    
    def classify_batch(self, texts: List[str], model_name: str = "distilbert") -> Dict:
        """Classify multiple texts"""
        response = requests.post(
            f"{self.base_url}/classify-batch",
            json={"texts": texts, "model_name": model_name}
        )
        response.raise_for_status()
        return response.json()
    
    def get_models(self) -> Dict:
        """Get available models"""
        response = requests.get(f"{self.base_url}/models")
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict:
        """Check API health"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

class NFLBettingClient:
    """Client for NFL Betting API"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
    
    def get_teams(self) -> List[Dict]:
        """Get all teams"""
        response = requests.get(f"{self.base_url}/teams")
        response.raise_for_status()
        return response.json()
    
    def get_games(self, season: int, week: int) -> List[Dict]:
        """Get games for a specific week"""
        response = requests.get(
            f"{self.base_url}/games",
            params={"season": season, "week": week}
        )
        response.raise_for_status()
        return response.json()
    
    def predict_game(self, home_team_id: int, away_team_id: int, season: int) -> Dict:
        """Predict game outcome"""
        response = requests.post(
            f"{self.base_url}/predict",
            json={
                "home_team_id": home_team_id,
                "away_team_id": away_team_id,
                "season": season
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_team_stats(self, team_id: int, season: int) -> Dict:
        """Get team statistics"""
        response = requests.get(
            f"{self.base_url}/stats/team/{team_id}",
            params={"season": season}
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict:
        """Check API health"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

def demo_text_classification_api():
    """Demonstrate Text Classification API usage"""
    print("🤖 Text Classification API Demo")
    print("=" * 40)
    
    client = TextClassificationClient()
    
    try:
        # Health check
        health = client.health_check()
        print(f"API Status: {health['status']}")
        
        # Get available models
        models = client.get_models()
        print(f"Available Models: {models['available_models']}")
        
        # Single text classification
        text = "This movie is absolutely fantastic!"
        result = client.classify_text(text)
        print(f"\nSingle Classification:")
        print(f"Text: '{result['text']}'")
        print(f"Prediction: {result['prediction']}")
        print(f"Confidence: {result['confidence']:.1%}")
        
        # Batch classification
        texts = [
            "I love this product!",
            "This is terrible.",
            "It's okay, nothing special."
        ]
        batch_result = client.classify_batch(texts)
        print(f"\nBatch Classification ({batch_result['total_processed']} texts):")
        for result in batch_result['results']:
            print(f"  '{result['text']}' -> {result['prediction']} ({result['confidence']:.1%})")
        
    except requests.RequestException as e:
        print(f"❌ API Error: {e}")
        print("Make sure the Text Classification API is running on port 8000")

def demo_nfl_betting_api():
    """Demonstrate NFL Betting API usage"""
    print("\n🏈 NFL Betting API Demo")
    print("=" * 40)
    
    client = NFLBettingClient()
    
    try:
        # Health check
        health = client.health_check()
        print(f"API Status: {health['status']}")
        print(f"Database Stats: {health['database_stats']}")
        
        # Get teams
        teams = client.get_teams()
        print(f"\nAvailable Teams ({len(teams)}):")
        for team in teams[:3]:  # Show first 3
            print(f"  {team['name']} ({team['abbreviation']}) - {team['conference']} {team['division']}")
        
        # Get games
        games = client.get_games(2024, 1)
        print(f"\nWeek 1, 2024 Games ({len(games)}):")
        for game in games:
            print(f"  {game['away_team']} @ {game['home_team']} - {game['game_date']}")
        
        # Make prediction (if we have teams)
        if len(teams) >= 2:
            prediction = client.predict_game(
                home_team_id=teams[0]['team_id'],
                away_team_id=teams[1]['team_id'],
                season=2024
            )
            print(f"\nPrediction: {prediction['away_team']} @ {prediction['home_team']}")
            print(f"  Spread: {prediction['predicted_spread']:+.1f}")
            print(f"  Total: {prediction['predicted_total']:.1f}")
            print(f"  Confidence: {prediction['confidence']:.1%}")
        
    except requests.RequestException as e:
        print(f"❌ API Error: {e}")
        print("Make sure the NFL Betting API is running on port 8001")

def main():
    """Run API demos"""
    print("🚀 API Client Demo")
    print("=" * 50)
    print("This demo shows how to use both APIs programmatically.")
    print("Make sure both API servers are running before testing.")
    print()
    
    # Demo both APIs
    demo_text_classification_api()
    demo_nfl_betting_api()
    
    print("\n✅ Demo Complete!")
    print("\nTo start the APIs:")
    print("  Text Classification: python text_classification_api.py")
    print("  NFL Betting: python nfl_betting_api.py")
    print("\nAPI Documentation:")
    print("  http://localhost:8000/docs (Text Classification)")
    print("  http://localhost:8001/docs (NFL Betting)")

if __name__ == "__main__":
    main()