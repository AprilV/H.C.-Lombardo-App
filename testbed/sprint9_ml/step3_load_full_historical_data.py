"""
SPRINT 9: Full Historical Data Loader (1999-2025 with EPA)
Phase 1c: Load 26 seasons of NFL data with advanced stats

Features:
- Loads 1999-2025 seasons (~6,500 games)
- Calculates EPA from play-by-play data
- Includes all 13 advanced metrics
- Sample weighting strategy (recent years = more weight)
- Progress tracking and ETA

Estimated time: 30-45 minutes total
- Schedules: ~5 minutes
- Play-by-play: ~20-30 minutes (26 seasons)
- EPA calculations: ~10 minutes
"""
import nfl_data_py as nfl
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os
from datetime import datetime
import numpy as np

load_dotenv()

conn = psycopg2.connect(
    dbname='nfl_analytics',
    user='postgres',
    password=os.getenv('DB_PASSWORD'),
    host='localhost',
    port='5432'
)

print("=" * 80)
print("SPRINT 9: HISTORICAL DATA LOADER (1999-2025 WITH EPA)")
print("=" * 80)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Configuration
SEASONS = list(range(1999, 2026))  # 1999-2025 (26 seasons)
BATCH_SIZE = 5  # Process 5 seasons at a time to manage memory

print(f"\n📅 Loading {len(SEASONS)} seasons: {SEASONS[0]}-{SEASONS[-1]}")
print(f"   Expected games: ~6,500")
print(f"   Expected team-game records: ~13,000")

# Step 1: Load all schedules
print("\n" + "=" * 80)
print("STEP 1: DOWNLOAD SCHEDULES (1999-2025)")
print("=" * 80)

start_time = datetime.now()
print(f"⏳ Downloading schedules for {len(SEASONS)} seasons...")

schedules = nfl.import_schedules(SEASONS)
elapsed = (datetime.now() - start_time).total_seconds()

print(f"✅ Downloaded {len(schedules):,} games in {elapsed:.1f} seconds")
print(f"   Seasons: {schedules['season'].min()}-{schedules['season'].max()}")
print(f"   Games per season (avg): {len(schedules) / len(SEASONS):.0f}")

# Step 2: Insert games into database
print("\n" + "=" * 80)
print("STEP 2: INSERT GAMES INTO DATABASE")
print("=" * 80)

cur = conn.cursor()

# First, check if we need to delete existing data
cur.execute("SELECT COUNT(*) FROM hcl.games WHERE season BETWEEN 1999 AND 2025")
existing_count = cur.fetchone()[0]

if existing_count > 0:
    response = input(f"\n⚠️  Found {existing_count} existing games (1999-2025). Delete and reload? (yes/no): ")
    if response.lower() == 'yes':
        print("🗑️  Deleting existing games...")
        cur.execute("DELETE FROM hcl.team_game_stats WHERE season BETWEEN 1999 AND 2025")
        cur.execute("DELETE FROM hcl.games WHERE season BETWEEN 1999 AND 2025")
        conn.commit()
        print(f"✅ Deleted {existing_count} games")
    else:
        print("❌ Aborted. Exiting.")
        cur.close()
        conn.close()
        exit()

print("\n⏳ Inserting games into database...")

games_data = []
for _, row in schedules.iterrows():
    games_data.append((
        row['game_id'],
        int(row['season']),
        int(row['week']),
        row.get('gameday'),
        None,  # kickoff_time_utc
        row['home_team'],
        row['away_team'],
        row.get('stadium'),
        None,  # city
        None,  # state
        None,  # timezone
        row['game_type'] != 'REG' if 'game_type' in row else False,
        int(row['home_score']) if pd.notna(row.get('home_score')) else None,
        int(row['away_score']) if pd.notna(row.get('away_score')) else None,
        float(row['spread_line']) if pd.notna(row.get('spread_line')) else None,
        float(row['total_line']) if pd.notna(row.get('total_line')) else None,
        float(row['home_moneyline']) if pd.notna(row.get('home_moneyline')) else None,
        float(row['away_moneyline']) if pd.notna(row.get('away_moneyline')) else None,
        None,  # home_spread_odds
        None,  # away_spread_odds
        None,  # over_odds
        None,  # under_odds
        row.get('roof'),
        row.get('surface'),
        float(row['temp']) if pd.notna(row.get('temp')) else None,
        float(row['wind']) if pd.notna(row.get('wind')) else None,
        int(row['away_rest']) if pd.notna(row.get('away_rest')) else None,
        int(row['home_rest']) if pd.notna(row.get('home_rest')) else None,
        row.get('div_game') == 1 if 'div_game' in row else None,
        int(row['overtime']) if pd.notna(row.get('overtime')) else None,
        row.get('referee'),
        row.get('away_coach'),
        row.get('home_coach'),
        row.get('away_qb_name'),
        row.get('home_qb_name')
    ))

execute_values(
    cur,
    """
    INSERT INTO hcl.games (
        game_id, season, week, game_date, kickoff_time_utc, home_team, away_team,
        stadium, city, state, timezone, is_postseason, home_score, away_score,
        spread_line, total_line, home_moneyline, away_moneyline,
        home_spread_odds, away_spread_odds, over_odds, under_odds,
        roof, surface, temp, wind, away_rest, home_rest,
        is_divisional_game, overtime, referee, away_coach, home_coach,
        away_qb_name, home_qb_name
    ) VALUES %s
    ON CONFLICT (game_id) DO NOTHING
    """,
    games_data
)

conn.commit()
print(f"✅ Inserted {len(games_data):,} games")

# Step 3: Load play-by-play data in batches and calculate EPA
print("\n" + "=" * 80)
print("STEP 3: LOAD PLAY-BY-PLAY DATA AND CALCULATE EPA")
print("=" * 80)
print(f"⏳ This will take 20-30 minutes for {len(SEASONS)} seasons...")
print(f"   Processing in batches of {BATCH_SIZE} seasons")

all_team_game_stats = []
total_seasons = len(SEASONS)

for batch_start in range(0, total_seasons, BATCH_SIZE):
    batch_end = min(batch_start + BATCH_SIZE, total_seasons)
    batch_seasons = SEASONS[batch_start:batch_end]
    
    print(f"\n📦 Batch {batch_start//BATCH_SIZE + 1}/{(total_seasons + BATCH_SIZE - 1)//BATCH_SIZE}: Seasons {batch_seasons[0]}-{batch_seasons[-1]}")
    
    batch_start_time = datetime.now()
    print(f"   ⏳ Downloading play-by-play data...")
    
    pbp = nfl.import_pbp_data(batch_seasons)
    
    elapsed = (datetime.now() - batch_start_time).total_seconds()
    print(f"   ✅ Downloaded {len(pbp):,} plays in {elapsed:.1f} seconds")
    
    print(f"   🧮 Calculating EPA for each team-game...")
    
    # Get unique games in this batch
    batch_games = pbp['game_id'].unique()
    
    for i, game_id in enumerate(batch_games):
        if (i + 1) % 50 == 0:
            print(f"      Progress: {i+1}/{len(batch_games)} games", end='\r')
        
        game_plays = pbp[pbp['game_id'] == game_id]
        teams = game_plays['posteam'].dropna().unique()
        
        for team in teams:
            team_plays = game_plays[game_plays['posteam'] == team]
            
            if len(team_plays) == 0:
                continue
            
            # Get opponent
            opponent = game_plays[game_plays['posteam'] != team]['posteam'].dropna().unique()
            opponent = opponent[0] if len(opponent) > 0 else None
            
            # Determine if home team
            is_home = game_plays[game_plays['posteam'] == team]['home_team'].iloc[0] == team if len(team_plays) > 0 else None
            
            # Get season and week
            season = int(game_plays['season'].iloc[0]) if 'season' in game_plays else None
            week = int(game_plays['week'].iloc[0]) if 'week' in game_plays else None
            
            # Calculate EPA stats
            stats = {
                'game_id': game_id,
                'team': team,
                'opponent': opponent,
                'is_home': is_home,
                'season': season,
                'week': week,
                
                'epa_per_play': team_plays['epa'].mean() if 'epa' in team_plays and team_plays['epa'].notna().any() else None,
                'total_epa': team_plays['epa'].sum() if 'epa' in team_plays and team_plays['epa'].notna().any() else None,
                'success_rate': (team_plays['epa'] > 0).mean() if 'epa' in team_plays and team_plays['epa'].notna().any() else None,
                
                'pass_epa': team_plays[team_plays['play_type'] == 'pass']['epa'].sum() if 'epa' in team_plays else None,
                'pass_success_rate': (team_plays[team_plays['play_type'] == 'pass']['epa'] > 0).mean() if 'epa' in team_plays else None,
                
                'rush_epa': team_plays[team_plays['play_type'] == 'run']['epa'].sum() if 'epa' in team_plays else None,
                'rush_success_rate': (team_plays[team_plays['play_type'] == 'run']['epa'] > 0).mean() if 'epa' in team_plays else None,
                
                'wpa': team_plays['wpa'].sum() if 'wpa' in team_plays and team_plays['wpa'].notna().any() else None,
                'cpoe': team_plays['cpoe'].mean() if 'cpoe' in team_plays and team_plays['cpoe'].notna().any() else None,
                
                'air_yards_per_att': team_plays[team_plays['play_type'] == 'pass']['air_yards'].mean() if 'air_yards' in team_plays else None,
                'yac_per_completion': team_plays[team_plays['complete_pass'] == 1]['yards_after_catch'].mean() if 'yards_after_catch' in team_plays else None,
                
                'explosive_play_pct': (team_plays['yards_gained'] >= 20).mean() if 'yards_gained' in team_plays else None,
                'stuff_rate': (team_plays[team_plays['play_type'] == 'run']['yards_gained'] <= 0).mean() if 'yards_gained' in team_plays else None,
            }
            
            all_team_game_stats.append(stats)
    
    print(f"   ✅ Calculated EPA for {len(batch_games)} games in batch")
    print(f"   ⏱️  Batch total time: {(datetime.now() - batch_start_time).total_seconds():.1f} seconds")

print(f"\n✅ Total team-game records with EPA: {len(all_team_game_stats):,}")

# Step 4: Insert/Update database with EPA stats
print("\n" + "=" * 80)
print("STEP 4: INSERT/UPDATE DATABASE WITH EPA STATS")
print("=" * 80)

print("⏳ Inserting team_game_stats with EPA calculations...")

# Convert numpy types to Python types for PostgreSQL
def convert_value(val):
    if pd.isna(val):
        return None
    return float(val)

insert_data = []
for stats in all_team_game_stats:
    insert_data.append((
        stats['game_id'],
        stats['team'],
        stats['opponent'],
        stats['is_home'],
        stats['season'],
        stats['week'],
        convert_value(stats['epa_per_play']),
        convert_value(stats['success_rate']),
        convert_value(stats['pass_epa']),
        convert_value(stats['rush_epa']),
        convert_value(stats['total_epa']),
        convert_value(stats['wpa']),
        convert_value(stats['cpoe']),
        convert_value(stats['air_yards_per_att']),
        convert_value(stats['yac_per_completion']),
        convert_value(stats['explosive_play_pct']),
        convert_value(stats['stuff_rate']),
        convert_value(stats['pass_success_rate']),
        convert_value(stats['rush_success_rate'])
    ))

execute_values(
    cur,
    """
    INSERT INTO hcl.team_game_stats (
        game_id, team, opponent, is_home, season, week,
        epa_per_play, success_rate, pass_epa, rush_epa, total_epa,
        wpa, cpoe, air_yards_per_att, yac_per_completion,
        explosive_play_pct, stuff_rate, pass_success_rate, rush_success_rate,
        created_at, updated_at
    ) VALUES %s
    ON CONFLICT (game_id, team) DO UPDATE SET
        opponent = EXCLUDED.opponent,
        is_home = EXCLUDED.is_home,
        season = EXCLUDED.season,
        week = EXCLUDED.week,
        epa_per_play = EXCLUDED.epa_per_play,
        success_rate = EXCLUDED.success_rate,
        pass_epa = EXCLUDED.pass_epa,
        rush_epa = EXCLUDED.rush_epa,
        total_epa = EXCLUDED.total_epa,
        wpa = EXCLUDED.wpa,
        cpoe = EXCLUDED.cpoe,
        air_yards_per_att = EXCLUDED.air_yards_per_att,
        yac_per_completion = EXCLUDED.yac_per_completion,
        explosive_play_pct = EXCLUDED.explosive_play_pct,
        stuff_rate = EXCLUDED.stuff_rate,
        pass_success_rate = EXCLUDED.pass_success_rate,
        rush_success_rate = EXCLUDED.rush_success_rate,
        updated_at = NOW()
    """,
    insert_data,
    template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())"
)

conn.commit()
print(f"✅ Inserted/Updated {len(insert_data):,} team-game records with EPA stats")

# Step 5: Verification
print("\n" + "=" * 80)
print("STEP 5: VERIFICATION")
print("=" * 80)

cur.execute("""
    SELECT 
        COUNT(*) as total_games,
        COUNT(DISTINCT season) as seasons,
        MIN(season) as first_season,
        MAX(season) as last_season,
        COUNT(*) FILTER (WHERE spread_line IS NOT NULL) as has_spread,
        COUNT(*) FILTER (WHERE total_line IS NOT NULL) as has_total
    FROM hcl.games
    WHERE season BETWEEN 1999 AND 2025
""")

result = cur.fetchone()
print(f"\n📊 Games Table:")
print(f"   Total games: {result[0]:,}")
print(f"   Seasons: {result[1]} ({result[2]}-{result[3]})")
print(f"   With spread: {result[4]:,} ({result[4]/result[0]*100:.1f}%)")
print(f"   With total: {result[5]:,} ({result[5]/result[0]*100:.1f}%)")

cur.execute("""
    SELECT 
        COUNT(*) as total_records,
        COUNT(*) FILTER (WHERE epa_per_play IS NOT NULL) as has_epa,
        AVG(epa_per_play) as avg_epa,
        AVG(success_rate) as avg_success_rate
    FROM hcl.team_game_stats
    WHERE season BETWEEN 1999 AND 2025
""")

result = cur.fetchone()
print(f"\n📈 Team Game Stats Table:")
print(f"   Total records: {result[0]:,}")
print(f"   With EPA: {result[1]:,} ({result[1]/result[0]*100:.1f}%)")
print(f"   Avg EPA/play: {result[2]:.4f}")
print(f"   Avg success rate: {result[3]:.1%}")

cur.close()
conn.close()

total_time = (datetime.now() - datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')).total_seconds()

print("\n" + "=" * 80)
print("✅ HISTORICAL DATA LOAD COMPLETE!")
print("=" * 80)
print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\n🎉 SUCCESS! Loaded 1999-2025 NFL data with EPA calculations")
print(f"   Ready for Sprint 9 neural network training!")
print("=" * 80)
