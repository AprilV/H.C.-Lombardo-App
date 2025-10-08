import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'nfl_analytics'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD')
)
cursor = conn.cursor()

print("\nDATABASE TABLE STRUCTURE:")
print("="*60)
cursor.execute("""
    SELECT column_name, data_type, character_maximum_length 
    FROM information_schema.columns 
    WHERE table_name = 'teams'
    ORDER BY ordinal_position
""")
for row in cursor.fetchall():
    print(row)

print("\nTOP 5 TEAMS IN DATABASE:")
print("="*60)
cursor.execute("SELECT name, ppg, pa FROM teams ORDER BY ppg DESC LIMIT 5")
for row in cursor.fetchall():
    print(f"{row[0]:30} PPG: {row[1]:5.1f}  PA: {row[2]:5.1f}")

print("\nTOTAL ROWS:")
cursor.execute("SELECT COUNT(*) FROM teams")
print(f"Teams in database: {cursor.fetchone()[0]}")

conn.close()
