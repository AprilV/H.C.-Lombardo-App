import requests
import nfl_data_py as nfl

# Get API predictions
response = requests.get('http://127.0.0.1:5000/api/ml/predict-week/2025/12')
api_data = response.json()
predictions = api_data['predictions']

# Get actual scores from NFLverse
schedules = nfl.import_schedules([2025])
week12 = schedules[(schedules['week'] == 12) & (schedules['season'] == 2025)]

print("Week 12 AI Spread Coverage (from API data)")
print("=" * 100)

ai_covered = 0
ai_total = 0

for pred in predictions:
    game_id = pred['game_id']
    nfl_game = week12[week12['game_id'] == game_id]
    
    if len(nfl_game) == 0:
        continue
        
    nfl_game = nfl_game.iloc[0]
    
    # Skip unfinished games
    if nfl_game['home_score'] != nfl_game['home_score']:  # NaN check
        continue
        
    home_score = int(nfl_game['home_score'])
    away_score = int(nfl_game['away_score'])
    actual_margin = home_score - away_score
    
    ai_spread = pred['ai_spread']
    
    # Check AI coverage
    ai_is_push = False
    ai_covered_game = None
    
    if ai_spread < 0:
        # Home team favored
        if actual_margin == -ai_spread:
            ai_is_push = True
        else:
            ai_covered_game = actual_margin > abs(ai_spread)
    else:
        # Away team favored
        if actual_margin == -ai_spread:
            ai_is_push = True
        else:
            ai_covered_game = actual_margin < -abs(ai_spread)
    
    # Count totals (excluding pushes)
    if not ai_is_push:
        ai_total += 1
        if ai_covered_game:
            ai_covered += 1
    
    # Print game details
    ai_status = "PUSH" if ai_is_push else ("✓ COVERED" if ai_covered_game else "✗ NO COVER")
    
    print(f"{pred['away_team']} @ {pred['home_team']}: {away_score}-{home_score} (margin: {actual_margin:+d})")
    print(f"  AI: {ai_spread:+.1f} {'(Home fav)' if ai_spread < 0 else '(Away fav)':<11} → {ai_status}")
    print()

print("=" * 100)
print(f"AI SPREAD COVERAGE: {ai_covered} / {ai_total} = {100*ai_covered/ai_total:.1f}%")
