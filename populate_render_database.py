"""
One-time script to populate Render PostgreSQL database from local machine
Run this once to set up the production database
"""
import os

# Set Render database credentials
os.environ['DB_HOST'] = 'dpg-d4j30ah5pdvs739561m0-a.oregon-postgres.render.com'
os.environ['DB_NAME'] = 'hcl_nfl_database'
os.environ['DB_USER'] = 'hcl_nfl_database_user'
os.environ['DB_PASSWORD'] = input("Enter Render DB password: ")
os.environ['DB_PORT'] = '5432'

print("🚀 Starting Render database population...")
print(f"📍 Host: {os.environ['DB_HOST']}")
print(f"📊 Database: {os.environ['DB_NAME']}")

# Run setup
import setup_render_db
setup_render_db.setup_database()
