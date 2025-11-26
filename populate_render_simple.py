"""
Simpler approach - use the External Database URL directly
"""
import psycopg2
import os

# Use the External Database URL from Render (you'll paste this)
DATABASE_URL = input("Paste External Database URL: ")

print("🚀 Connecting to Render database...")

try:
    # Connect using the full URL
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("✅ Connected! Creating teams table...")
    
    # Create simple teams table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            abbreviation TEXT,
            wins INTEGER,
            losses INTEGER
        )
    """)
    
    # Insert one test team
    cursor.execute("""
        INSERT INTO teams (name, abbreviation, wins, losses)
        VALUES ('Kansas City Chiefs', 'KC', 10, 1)
    """)
    
    conn.commit()
    print("✅ Success! Database populated.")
    
    # Verify
    cursor.execute("SELECT * FROM teams")
    print(f"✅ Found {cursor.rowcount} teams in database")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
