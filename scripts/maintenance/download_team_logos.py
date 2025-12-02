"""
Download all 32 NFL team logos locally
Run this once to cache all team logos in the frontend
"""
import requests
import os
from pathlib import Path

# All 32 NFL team abbreviations
NFL_TEAMS = [
    # AFC East
    'BUF', 'MIA', 'NE', 'NYJ',
    # AFC North
    'BAL', 'CIN', 'CLE', 'PIT',
    # AFC South
    'HOU', 'IND', 'JAX', 'TEN',
    # AFC West
    'DEN', 'KC', 'LV', 'LAC',
    # NFC East
    'DAL', 'NYG', 'PHI', 'WAS',
    # NFC North
    'CHI', 'DET', 'GB', 'MIN',
    # NFC South
    'ATL', 'CAR', 'NO', 'TB',
    # NFC West
    'ARI', 'LAR', 'SF', 'SEA'
]

# Create images directory if it doesn't exist
IMAGES_DIR = Path(__file__).parent / 'frontend' / 'public' / 'images' / 'teams'
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("NFL TEAM LOGOS DOWNLOADER")
print("=" * 60)
print(f"Downloading logos to: {IMAGES_DIR}")
print()

successful = 0
failed = []

for team in NFL_TEAMS:
    # ESPN logo URL
    url = f"https://a.espncdn.com/i/teamlogos/nfl/500/{team}.png"
    output_path = IMAGES_DIR / f"{team.lower()}.png"
    
    try:
        print(f"Downloading {team}...", end=" ")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Save the image
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ ({len(response.content)} bytes)")
        successful += 1
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        failed.append(team)

print()
print("=" * 60)
print(f"DOWNLOAD COMPLETE")
print("=" * 60)
print(f"✓ Successful: {successful}/{len(NFL_TEAMS)}")
if failed:
    print(f"✗ Failed: {len(failed)} - {', '.join(failed)}")
else:
    print("✓ All logos downloaded successfully!")
print()
print(f"Logos saved to: {IMAGES_DIR}")
print("=" * 60)
