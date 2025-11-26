"""
Populate Render Production Database with HCL Schema Data
Connects to RENDER database and loads historical NFL data
"""
import psycopg2
from psycopg2.extras import execute_values
import sys

# Render database connection
RENDER_DB_URL = "postgresql://nfl_user:rzkKyzQq9pTas14pXDJU3fm8cCZObAh5@dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com/nfl_analytics"

print("=" * 80)
print("POPULATE RENDER DATABASE - HCL SCHEMA")
print("=" * 80)

try:
    conn = psycopg2.connect(RENDER_DB_URL)
    cursor = conn.cursor()
    
    print("\n✅ Connected to Render database")
    
    # Step 1: Create team_info table if it doesn't exist
    print("\n📋 Step 1: Creating hcl.team_info table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hcl.team_info (
            team_abbr VARCHAR(3) PRIMARY KEY,
            team_name VARCHAR(100) NOT NULL,
            conference VARCHAR(3),
            division VARCHAR(10)
        )
    """)
    conn.commit()
    print("✅ Table created")
    
    # Step 2: Insert all 32 NFL teams into team_info
    print("\n👥 Step 2: Inserting 32 NFL teams...")
    
    teams = [
        ('ARI', 'Arizona Cardinals', 'NFC', 'West'),
        ('ATL', 'Atlanta Falcons', 'NFC', 'South'),
        ('BAL', 'Baltimore Ravens', 'AFC', 'North'),
        ('BUF', 'Buffalo Bills', 'AFC', 'East'),
        ('CAR', 'Carolina Panthers', 'NFC', 'South'),
        ('CHI', 'Chicago Bears', 'NFC', 'North'),
        ('CIN', 'Cincinnati Bengals', 'AFC', 'North'),
        ('CLE', 'Cleveland Browns', 'AFC', 'North'),
        ('DAL', 'Dallas Cowboys', 'NFC', 'East'),
        ('DEN', 'Denver Broncos', 'AFC', 'West'),
        ('DET', 'Detroit Lions', 'NFC', 'North'),
        ('GB', 'Green Bay Packers', 'NFC', 'North'),
        ('HOU', 'Houston Texans', 'AFC', 'South'),
        ('IND', 'Indianapolis Colts', 'AFC', 'South'),
        ('JAX', 'Jacksonville Jaguars', 'AFC', 'South'),
        ('KC', 'Kansas City Chiefs', 'AFC', 'West'),
        ('LAC', 'Los Angeles Chargers', 'AFC', 'West'),
        ('LAR', 'Los Angeles Rams', 'NFC', 'West'),
        ('LV', 'Las Vegas Raiders', 'AFC', 'West'),
        ('MIA', 'Miami Dolphins', 'AFC', 'East'),
        ('MIN', 'Minnesota Vikings', 'NFC', 'North'),
        ('NE', 'New England Patriots', 'AFC', 'East'),
        ('NO', 'New Orleans Saints', 'NFC', 'South'),
        ('NYG', 'New York Giants', 'NFC', 'East'),
        ('NYJ', 'New York Jets', 'AFC', 'East'),
        ('PHI', 'Philadelphia Eagles', 'NFC', 'East'),
        ('PIT', 'Pittsburgh Steelers', 'AFC', 'North'),
        ('SEA', 'Seattle Seahawks', 'NFC', 'West'),
        ('SF', 'San Francisco 49ers', 'NFC', 'West'),
        ('TB', 'Tampa Bay Buccaneers', 'NFC', 'South'),
        ('TEN', 'Tennessee Titans', 'AFC', 'South'),
        ('WSH', 'Washington Commanders', 'NFC', 'East'),
    ]
    
    # Delete existing teams first
    cursor.execute("DELETE FROM hcl.team_info")
    
    # Insert teams
    execute_values(cursor, """
        INSERT INTO hcl.team_info (team_abbr, team_name, conference, division)
        VALUES %s
        ON CONFLICT (team_abbr) DO UPDATE SET
            team_name = EXCLUDED.team_name,
            conference = EXCLUDED.conference,
            division = EXCLUDED.division
    """, teams)
    
    conn.commit()
    print(f"✅ Inserted {len(teams)} teams")
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM hcl.team_info")
    count = cursor.fetchone()[0]
    print(f"\n✅ Verification: {count} teams in hcl.team_info")
    
    # Show sample
    cursor.execute("SELECT team_abbr, team_name FROM hcl.team_info ORDER BY team_abbr LIMIT 5")
    sample = cursor.fetchall()
    print("\nSample teams:")
    for abbr, name in sample:
        print(f"  {abbr}: {name}")
    
    print("\n" + "=" * 80)
    print("SUCCESS! Team dropdowns should now work")
    print("=" * 80)
    print("\nNext step: Load historical games data")
    print("(This will require running the historical data loader script)")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
