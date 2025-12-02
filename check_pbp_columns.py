"""Check what columns are available in nflverse play-by-play data"""
import nfl_data_py as nfl

print("Downloading 2025 play-by-play data...")
pbp = nfl.import_pbp_data([2025])
print(f"Total plays: {len(pbp)}")
print(f"\nTotal columns: {len(pbp.columns)}")
print("\nColumns containing 'epa', 'wpa', 'cpoe', 'air', 'yac', 'success', 'stuff', 'explosive':")
for col in sorted(pbp.columns):
    if any(term in col.lower() for term in ['epa', 'wpa', 'cpoe', 'air', 'yac', 'success', 'stuff', 'explosive']):
        print(f"  - {col}")
