#!/usr/bin/env python3
"""Create and populate hcl.team_info table on Render"""

import psycopg2

RENDER_URL = "postgresql://nfl_user:rzkKyzQq9pTas14pXDJU3fm8cCZObAh5@dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com/nfl_analytics"

# 32 NFL teams with metadata
NFL_TEAMS = [
    ('ARI', 'Arizona Cardinals', 'Cardinals', 'NFC', 'West'),
    ('ATL', 'Atlanta Falcons', 'Falcons', 'NFC', 'South'),
    ('BAL', 'Baltimore Ravens', 'Ravens', 'AFC', 'North'),
    ('BUF', 'Buffalo Bills', 'Bills', 'AFC', 'East'),
    ('CAR', 'Carolina Panthers', 'Panthers', 'NFC', 'South'),
    ('CHI', 'Chicago Bears', 'Bears', 'NFC', 'North'),
    ('CIN', 'Cincinnati Bengals', 'Bengals', 'AFC', 'North'),
    ('CLE', 'Cleveland Browns', 'Browns', 'AFC', 'North'),
    ('DAL', 'Dallas Cowboys', 'Cowboys', 'NFC', 'East'),
    ('DEN', 'Denver Broncos', 'Broncos', 'AFC', 'West'),
    ('DET', 'Detroit Lions', 'Lions', 'NFC', 'North'),
    ('GB', 'Green Bay Packers', 'Packers', 'NFC', 'North'),
    ('HOU', 'Houston Texans', 'Texans', 'AFC', 'South'),
    ('IND', 'Indianapolis Colts', 'Colts', 'AFC', 'South'),
    ('JAX', 'Jacksonville Jaguars', 'Jaguars', 'AFC', 'South'),
    ('KC', 'Kansas City Chiefs', 'Chiefs', 'AFC', 'West'),
    ('LA', 'Los Angeles Rams', 'Rams', 'NFC', 'West'),
    ('LAC', 'Los Angeles Chargers', 'Chargers', 'AFC', 'West'),
    ('LV', 'Las Vegas Raiders', 'Raiders', 'AFC', 'West'),
    ('MIA', 'Miami Dolphins', 'Dolphins', 'AFC', 'East'),
    ('MIN', 'Minnesota Vikings', 'Vikings', 'NFC', 'North'),
    ('NE', 'New England Patriots', 'Patriots', 'AFC', 'East'),
    ('NO', 'New Orleans Saints', 'Saints', 'NFC', 'South'),
    ('NYG', 'New York Giants', 'Giants', 'NFC', 'East'),
    ('NYJ', 'New York Jets', 'Jets', 'AFC', 'East'),
    ('PHI', 'Philadelphia Eagles', 'Eagles', 'NFC', 'East'),
    ('PIT', 'Pittsburgh Steelers', 'Steelers', 'AFC', 'North'),
    ('SF', 'San Francisco 49ers', '49ers', 'NFC', 'West'),
    ('SEA', 'Seattle Seahawks', 'Seahawks', 'NFC', 'West'),
    ('TB', 'Tampa Bay Buccaneers', 'Buccaneers', 'NFC', 'South'),
    ('TEN', 'Tennessee Titans', 'Titans', 'AFC', 'South'),
    ('WAS', 'Washington Commanders', 'Commanders', 'NFC', 'East'),
]

print("\n" + "="*80)
print("🏈 CREATING HCL.TEAM_INFO TABLE")
print("="*80)

conn = psycopg2.connect(RENDER_URL)
cur = conn.cursor()

# Create table
print("\n1️⃣ Creating table...")
cur.execute("""
    CREATE TABLE IF NOT EXISTS hcl.team_info (
        team VARCHAR(10) PRIMARY KEY,
        full_name VARCHAR(100),
        nickname VARCHAR(50),
        conference VARCHAR(10),
        division VARCHAR(10),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    )
""")
conn.commit()
print("   ✅ Table created")

# Insert teams
print("\n2️⃣ Inserting 32 NFL teams...")
cur.executemany("""
    INSERT INTO hcl.team_info (team, full_name, nickname, conference, division)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (team) DO UPDATE SET
        full_name = EXCLUDED.full_name,
        nickname = EXCLUDED.nickname,
        conference = EXCLUDED.conference,
        division = EXCLUDED.division,
        updated_at = NOW()
""", NFL_TEAMS)
conn.commit()
print(f"   ✅ Inserted {len(NFL_TEAMS)} teams")

# Verify
cur.execute("SELECT COUNT(*) FROM hcl.team_info")
count = cur.fetchone()[0]
print(f"\n3️⃣ Verification:")
print(f"   • Total teams: {count}")

cur.execute("SELECT team, full_name FROM hcl.team_info ORDER BY team LIMIT 5")
print(f"\n   Sample teams:")
for team, name in cur.fetchall():
    print(f"   • {team}: {name}")

conn.close()
print("\n✅ TEAM_INFO TABLE READY!")
print("="*80 + "\n")
