"""
Verify nflverse data is flowing: Database -> API -> Frontend
Check all 64 team_game_stats columns
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=os.getenv('DB_PORT', '5432')
)

cur = conn.cursor()

# Step 1: Check what columns exist in team_game_stats
print("\n" + "="*80)
print("STEP 1: Database Schema Check")
print("="*80)
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_schema = 'hcl' 
    AND table_name = 'team_game_stats'
    ORDER BY ordinal_position
""")
db_columns = [row[0] for row in cur.fetchall()]
print(f"Total columns in hcl.team_game_stats: {len(db_columns)}")
print(f"Columns: {', '.join(db_columns)}")

# Step 2: Check if Week 13 has actual data in those columns
print("\n" + "="*80)
print("STEP 2: Week 13 Data Check (Sample: KC)")
print("="*80)
cur.execute("""
    SELECT *
    FROM hcl.team_game_stats
    WHERE season = 2025 AND week = 13 AND team = 'KC'
    LIMIT 1
""")
row = cur.fetchone()
if row:
    print(f"Found KC Week 13 data")
    # Check which fields have values vs NULL
    non_null = 0
    null_fields = []
    for i, col in enumerate(db_columns):
        if row[i] is not None:
            non_null += 1
        else:
            null_fields.append(col)
    
    print(f"Fields with data: {non_null}/{len(db_columns)}")
    if null_fields:
        print(f"NULL fields: {', '.join(null_fields)}")
else:
    print("❌ NO Week 13 data found for KC")

# Step 3: Check what the API query returns
print("\n" + "="*80)
print("STEP 3: API Query Check - What /api/hcl/teams/KC returns")
print("="*80)
print("Reading from api_routes_hcl.py to see what columns are queried...")

# Read the API file to see what it's selecting
with open('api_routes_hcl.py', 'r') as f:
    content = f.read()
    
# Find the team details query
if 'def get_team_details' in content:
    print("✅ Found get_team_details endpoint")
    # Extract the SELECT portion
    start = content.find('def get_team_details')
    end = content.find('FROM hcl.team_game_stats', start)
    query_section = content[start:end]
    
    # Count how many AVG() statements (each is a stat being returned)
    avg_count = query_section.count('AVG(')
    sum_count = query_section.count('SUM(')
    round_count = query_section.count('ROUND(')
    
    print(f"Stats being calculated: {avg_count} AVG(), {sum_count} SUM(), {round_count} ROUND()")
    
    # Check for EPA stats
    if 'epa_per_play' in query_section:
        print("✅ EPA stats ARE included in API query")
    else:
        print("❌ EPA stats NOT included in API query")
else:
    print("❌ Could not find get_team_details endpoint")

conn.close()

print("\n" + "="*80)
print("VERIFICATION COMPLETE")
print("="*80)
