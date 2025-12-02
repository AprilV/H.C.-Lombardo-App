import requests
import json

print("Testing ML Predictions API...")
print("="*80)

try:
    response = requests.get('http://localhost:5000/api/ml/predict-upcoming')
    data = response.json()
    
    print(f"\nSeason: {data.get('season')}")
    print(f"Week: {data.get('week')}")
    print(f"Total Games: {data.get('total_games')}\n")
    
    if data.get('predictions'):
        for i, pred in enumerate(data['predictions'][:3], 1):  # First 3 games
            print(f"\nGame {i}:")
            print(f"  Game ID: {pred.get('game_id')}")
            print(f"  Date: {pred.get('game_date')}")
            print(f"  Kickoff: {pred.get('kickoff_time')}")
            print(f"  Matchup: {pred.get('away_team')} @ {pred.get('home_team')}")
            print(f"  Prediction: {pred.get('predicted_winner')} wins")
            print(f"  Confidence: {pred.get('confidence')*100:.1f}%")
    else:
        print("No predictions found!")
        print(json.dumps(data, indent=2))
        
except Exception as e:
    print(f"ERROR: {e}")
