"""
Create analytics views on Render database
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to Render database
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    sslmode='require'
)

cur = conn.cursor()

print("Creating analytics views on Render database...")

# Read and execute the feature views SQL
with open('hcl_feature_views.sql', 'r') as f:
    sql = f.read()
    
    # Execute the SQL (it has multiple statements)
    cur.execute(sql)
    conn.commit()

print("✅ Analytics views created successfully")

# Verify
cur.execute("""
    SELECT table_name 
    FROM information_schema.views 
    WHERE table_schema = 'hcl' 
    AND table_name LIKE 'v_%'
    ORDER BY table_name
""")

views = cur.fetchall()
print(f"\n✅ Created {len(views)} views:")
for (view_name,) in views:
    print(f"   - {view_name}")

cur.close()
conn.close()
