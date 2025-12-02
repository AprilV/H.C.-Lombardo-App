"""
Update Week 12 2025 spreads with actual NFLverse closing lines
"""
import json
import nfl_data_py as nfl

# Get current NFLverse data for 2025 Week 12
schedules = nfl.import_schedules([2025])
week12 = schedules[(schedules['week'] == 12) & (schedules['season'] == 2025)]

# Load our predictions file
with open('ml/predictions_week_12.json', 'r') as f:
    predictions = json.load(f)

print("Updating Week 12 spreads with NFLverse closing lines...")
print("=" * 80)

updates = 0
for pred in predictions:
    game_id = pred['game_id']
    
    # Find matching game in NFLverse data
    nfl_game = week12[week12['game_id'] == game_id]
    
    if len(nfl_game) > 0:
        # NFLverse uses OPPOSITE sign convention: positive = home favored, negative = away favored
        # We need to flip the sign to match standard Vegas convention (negative = favorite)
        nfl_spread = -float(nfl_game.iloc[0]['spread_line'])
        old_spread = pred['vegas_spread']
        
        if nfl_spread != old_spread:
            pred['vegas_spread'] = nfl_spread
            pred['spread_difference'] = round(pred['ai_spread'] - nfl_spread, 1)
            updates += 1
            print(f"{pred['away_team']} @ {pred['home_team']}")
            print(f"  Old spread: {old_spread}")
            print(f"  New spread: {nfl_spread}")
            print()

print(f"\nUpdated {updates} games")

# Save updated predictions
with open('ml/predictions_week_12.json', 'w') as f:
    json.dump(predictions, f, indent=2)

print("\n✓ Updated predictions_week_12.json with correct Vegas spreads")
