import requests
import nfl_data_py as nfl

# Get API predictions
response = requests.get('http://127.0.0.1:5000/api/ml/predict-week/2025/12')
api_data = response.json()
predictions = api_data['predictions']

# Get actual scores from NFLverse
schedules = nfl.import_schedules([2025])
week12 = schedules[(schedules['week'] == 12) & (schedules['season'] == 2025)]

print("Week 12 DETAILED Coverage Comparison")
print("=" * 120)

vegas_covered_games = []
ai_covered_games = []
vegas_total = 0
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
    
    vegas_spread = pred['vegas_spread']
    ai_spread = pred['ai_spread']
    
    # Check Vegas coverage
    vegas_is_push = False
    vegas_covered_game = None
    vegas_favorite = None
    
    if vegas_spread < 0:
        vegas_favorite = pred['home_team']
        if actual_margin == -vegas_spread:
            vegas_is_push = True
        else:
            vegas_covered_game = actual_margin > abs(vegas_spread)
    else:
        vegas_favorite = pred['away_team']
        if actual_margin == -vegas_spread:
            vegas_is_push = True
        else:
            vegas_covered_game = actual_margin < -abs(vegas_spread)
    
    # Check AI coverage
    ai_is_push = False
    ai_covered_game = None
    ai_favorite = None
    
    if ai_spread < 0:
        ai_favorite = pred['home_team']
        if actual_margin == -ai_spread:
            ai_is_push = True
        else:
            ai_covered_game = actual_margin > abs(ai_spread)
    else:
        ai_favorite = pred['away_team']
        if actual_margin == -ai_spread:
            ai_is_push = True
        else:
            ai_covered_game = actual_margin < -abs(ai_spread)
    
    # Count totals
    if not vegas_is_push:
        vegas_total += 1
        if vegas_covered_game:
            vegas_covered_games.append(f"{pred['away_team']} @ {pred['home_team']}")
    
    if not ai_is_push:
        ai_total += 1
        if ai_covered_game:
            ai_covered_games.append(f"{pred['away_team']} @ {pred['home_team']}")
    
    # Print game details
    vegas_status = "PUSH" if vegas_is_push else ("✓ COVERED" if vegas_covered_game else "✗ NO COVER")
    ai_status = "PUSH" if ai_is_push else ("✓ COVERED" if ai_covered_game else "✗ NO COVER")
    
    print(f"{pred['away_team']} @ {pred['home_team']}: {away_score}-{home_score} (margin: {actual_margin:+d})")
    print(f"  Vegas: {vegas_spread:+.1f} ({vegas_favorite} fav by {abs(vegas_spread):.1f}) → {vegas_status}")
    print(f"  AI:    {ai_spread:+.1f} ({ai_favorite} fav by {abs(ai_spread):.1f}) → {ai_status}")
    print()

print("=" * 120)
print(f"\nVEGAS COVERED ({len(vegas_covered_games)}/{vegas_total}):")
for game in vegas_covered_games:
    print(f"  ✓ {game}")

print(f"\nAI COVERED ({len(ai_covered_games)}/{ai_total}):")
for game in ai_covered_games:
    print(f"  ✓ {game}")

print(f"\nVEGAS SPREAD COVERAGE: {len(vegas_covered_games)} / {vegas_total} = {100*len(vegas_covered_games)/vegas_total:.1f}%")
print(f"AI SPREAD COVERAGE:    {len(ai_covered_games)} / {ai_total} = {100*len(ai_covered_games)/ai_total:.1f}%")
