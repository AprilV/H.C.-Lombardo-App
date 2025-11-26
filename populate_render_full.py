"""
Complete database setup for Render PostgreSQL
This runs the full schema creation and data loading
"""
import psycopg2
import os
import sys

# Get the External Database URL
DATABASE_URL = input("Paste External Database URL: ")

print("🚀 Connecting to Render database...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("✅ Connected! Setting up complete schema...")
    
    # Drop existing tables if they exist (fresh start)
    print("🗑️ Dropping old tables...")
    cursor.execute("DROP TABLE IF EXISTS games CASCADE")
    cursor.execute("DROP TABLE IF EXISTS teams CASCADE")
    conn.commit()
    
    # Create teams table with ALL required columns
    print("📊 Creating teams table...")
    cursor.execute("""
        CREATE TABLE teams (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            abbreviation TEXT UNIQUE NOT NULL,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            ties INTEGER DEFAULT 0,
            ppg DECIMAL(5,2) DEFAULT 0,
            pa DECIMAL(5,2) DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    # Insert all 32 NFL teams
    print("🏈 Inserting NFL teams...")
    teams_data = [
        ('Arizona Cardinals', 'ARI'), ('Atlanta Falcons', 'ATL'),
        ('Baltimore Ravens', 'BAL'), ('Buffalo Bills', 'BUF'),
        ('Carolina Panthers', 'CAR'), ('Chicago Bears', 'CHI'),
        ('Cincinnati Bengals', 'CIN'), ('Cleveland Browns', 'CLE'),
        ('Dallas Cowboys', 'DAL'), ('Denver Broncos', 'DEN'),
        ('Detroit Lions', 'DET'), ('Green Bay Packers', 'GB'),
        ('Houston Texans', 'HOU'), ('Indianapolis Colts', 'IND'),
        ('Jacksonville Jaguars', 'JAX'), ('Kansas City Chiefs', 'KC'),
        ('Las Vegas Raiders', 'LV'), ('Los Angeles Chargers', 'LAC'),
        ('Los Angeles Rams', 'LAR'), ('Miami Dolphins', 'MIA'),
        ('Minnesota Vikings', 'MIN'), ('New England Patriots', 'NE'),
        ('New Orleans Saints', 'NO'), ('New York Giants', 'NYG'),
        ('New York Jets', 'NYJ'), ('Philadelphia Eagles', 'PHI'),
        ('Pittsburgh Steelers', 'PIT'), ('San Francisco 49ers', 'SF'),
        ('Seattle Seahawks', 'SEA'), ('Tampa Bay Buccaneers', 'TB'),
        ('Tennessee Titans', 'TEN'), ('Washington Commanders', 'WAS')
    ]
    
    for name, abbr in teams_data:
        cursor.execute(
            "INSERT INTO teams (name, abbreviation) VALUES (%s, %s)",
            (name, abbr)
        )
    conn.commit()
    
    # Create games table
    print("📅 Creating games table...")
    cursor.execute("""
        CREATE TABLE games (
            id SERIAL PRIMARY KEY,
            season INTEGER NOT NULL,
            week INTEGER NOT NULL,
            game_date TIMESTAMP,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            home_score INTEGER,
            away_score INTEGER,
            vegas_line DECIMAL(5,2),
            vegas_favorite TEXT,
            ai_predicted_winner TEXT,
            ai_confidence DECIMAL(5,2),
            ai_spread DECIMAL(5,2),
            status TEXT DEFAULT 'scheduled',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    print("✅ Schema created successfully!")
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM teams")
    team_count = cursor.fetchone()[0]
    print(f"✅ Found {team_count} teams in database")
    
    cursor.close()
    conn.close()
    
    print("🎉 Database setup complete! Your Render app should now work.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
