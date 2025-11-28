#!/usr/bin/env python3
"""
Load 2025 season to RENDER database with EPA calculations
Uses nflverse to download play-by-play data and calculate EPA stats
"""

import os
import sys

# Set environment variables to point to RENDER database
os.environ['DB_HOST'] = 'dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com'
os.environ['DB_NAME'] = 'nfl_analytics'
os.environ['DB_USER'] = 'nfl_user'
os.environ['DB_PASSWORD'] = 'rzkKyzQq9pTas14pXDJU3fm8cCZObAh5'
os.environ['DB_PORT'] = '5432'

print("\n" + "="*80)
print("📥 LOADING 2025 SEASON TO RENDER (with EPA calculations)")
print("="*80)
print(f"\n🌐 Target: {os.environ['DB_HOST']}")
print(f"📊 Database: {os.environ['DB_NAME']}")
print("\n⏳ This will take 5-10 minutes (downloading play-by-play data)...\n")

# Now run the ingest script
import subprocess
result = subprocess.run(
    [sys.executable, 'ingest_historical_games.py', '--production', '--seasons', '2025'],
    capture_output=False,
    text=True
)

sys.exit(result.returncode)
