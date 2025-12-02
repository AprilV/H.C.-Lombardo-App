import json
import nfl_data_py as nfl

# Load predictions
with open('ml/predictions_week_12.json') as f:
    preds = json.load(f)

# Load NFLverse data
schedules = nfl.import_schedules([2025])
week12 = schedules[(schedules['week'] == 12) & (schedules['season'] == 2025)]

print("Checking Vegas Spread Coverage for Week 12")
print("=" * 80)

covered_count = 0
total_finished = 0

for pred in preds:
    game_id = pred['game_id']
    nfl_game = week12[week12['game_id'] == game_id]
    
    if len(nfl_game) > 0:
        nfl_game = nfl_game.iloc[0]
        
        # Skip unfinished games
        if nfl_game['home_score'] != nfl_game['home_score']:  # NaN check
            continue
            
        home_score = int(nfl_game['home_score'])
        away_score = int(nfl_game['away_score'])
        actual_margin = home_score - away_score
        vegas_spread = pred['vegas_spread']
        
        total_finished += 1
        
        # Check coverage
        covered = None
        if vegas_spread < 0:
            # Home team favored
            if actual_margin > abs(vegas_spread):
                covered = True
            elif actual_margin == -vegas_spread:
                covered = None  # Push
            else:
                covered = False
        else:
            # Away team favored
            if actual_margin < -abs(vegas_spread):
                covered = True
            elif actual_margin == -vegas_spread:
                covered = None  # Push
            else:
                covered = False
        
        if covered:
            covered_count += 1
        
        status = "COVERED ✓" if covered else ("PUSH" if covered is None else "DID NOT COVER ✗")
        
        print(f"{pred['away_team']} @ {pred['home_team']}: {away_score}-{home_score}")
        print(f"  Vegas Spread: {vegas_spread} ({'Home' if vegas_spread < 0 else 'Away'} favored by {abs(vegas_spread)})")
        print(f"  Actual Margin: {actual_margin} (Home won by {actual_margin})" if actual_margin > 0 else f"  Actual Margin: {actual_margin} (Away won by {abs(actual_margin)})")
        print(f"  Result: {status}")
        print()

print("=" * 80)
print(f"Vegas Coverage: {covered_count} / {total_finished} ({100*covered_count/total_finished:.1f}%)")
