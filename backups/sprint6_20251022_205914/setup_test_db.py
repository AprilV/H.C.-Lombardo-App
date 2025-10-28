"""
HC Lombardo - Test Database Setup Script
Sprint 5-6: Create nfl_analytics_test database and hcl schema

Purpose:
- Create test database for safe development
- Run hcl_schema.sql to create tables/views/indexes
- Validate schema with sanity checks

Usage:
    python testbed/setup_test_db.py

Requirements:
    - PostgreSQL running on localhost:5432
    - DB credentials in .env (DB_USER, DB_PASSWORD)
    - Superuser privileges to CREATE DATABASE
"""

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

TEST_DB_NAME = 'nfl_analytics_test'
SCHEMA_FILE = Path(__file__).parent / 'schema' / 'hcl_schema.sql'


def create_test_database():
    """Create test database (drop if exists)"""
    print(f"\n{'='*70}")
    print(f"STEP 1: Creating Test Database")
    print(f"{'='*70}\n")
    
    # Connect to default postgres database
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database='postgres',
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    try:
        # Drop existing test database if exists
        print(f"[1/3] Checking for existing '{TEST_DB_NAME}' database...")
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'")
        if cursor.fetchone():
            print(f"      Found existing database. Dropping...")
            cursor.execute(sql.SQL("DROP DATABASE {}").format(
                sql.Identifier(TEST_DB_NAME)
            ))
            print(f"      ✓ Dropped existing database")
        else:
            print(f"      No existing database found")
        
        # Create new test database
        print(f"\n[2/3] Creating new '{TEST_DB_NAME}' database...")
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(TEST_DB_NAME)
        ))
        print(f"      ✓ Database created successfully")
        
        # Verify creation
        print(f"\n[3/3] Verifying database creation...")
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{TEST_DB_NAME}'")
        if cursor.fetchone():
            print(f"      ✓ Database verified")
        else:
            raise Exception("Database creation failed verification")
        
        print(f"\n✅ Test database '{TEST_DB_NAME}' ready")
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to create database: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def run_schema_file():
    """Execute hcl_schema.sql to create tables/views/indexes"""
    print(f"\n{'='*70}")
    print(f"STEP 2: Running Schema File")
    print(f"{'='*70}\n")
    
    # Read schema file
    print(f"[1/3] Reading schema file: {SCHEMA_FILE}")
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_FILE}")
    
    with open(SCHEMA_FILE, 'r') as f:
        schema_sql = f.read()
    
    print(f"      ✓ Schema file loaded ({len(schema_sql)} characters)")
    
    # Connect to test database
    print(f"\n[2/3] Connecting to '{TEST_DB_NAME}'...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=TEST_DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    try:
        # Execute schema
        print(f"\n[3/3] Executing schema SQL...")
        cursor.execute(schema_sql)
        conn.commit()
        print(f"      ✓ Schema executed successfully")
        
        print(f"\n✅ Schema created in '{TEST_DB_NAME}'")
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to execute schema: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def validate_schema():
    """Run validation queries to verify schema is correct"""
    print(f"\n{'='*70}")
    print(f"STEP 3: Validating Schema")
    print(f"{'='*70}\n")
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=TEST_DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    try:
        # Check schema exists
        print(f"[1/6] Checking 'hcl' schema exists...")
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = 'hcl'
        """)
        if cursor.fetchone():
            print(f"      ✓ Schema 'hcl' exists")
        else:
            raise Exception("Schema 'hcl' not found")
        
        # Check tables exist
        print(f"\n[2/6] Checking tables exist...")
        expected_tables = ['games', 'team_game_stats']
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'hcl'
            AND table_type = 'BASE TABLE'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in expected_tables:
            if table in tables:
                print(f"      ✓ Table 'hcl.{table}' exists")
            else:
                raise Exception(f"Table 'hcl.{table}' not found")
        
        # Check views exist
        print(f"\n[3/6] Checking views exist...")
        expected_views = [
            'v_team_season_stats',
            'v_game_matchup_display',
            'v_game_matchup_with_proj'
        ]
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'hcl'
        """)
        views = [row[0] for row in cursor.fetchall()]
        
        for view in expected_views:
            if view in views:
                print(f"      ✓ View 'hcl.{view}' exists")
            else:
                raise Exception(f"View 'hcl.{view}' not found")
        
        # Check indexes exist
        print(f"\n[4/6] Checking indexes exist...")
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE schemaname = 'hcl'
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        print(f"      ✓ Found {len(indexes)} indexes")
        for idx in indexes:
            print(f"        - {idx}")
        
        # Check table columns
        print(f"\n[5/6] Checking table structures...")
        
        # games table
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'hcl' AND table_name = 'games'
        """)
        games_columns = [row[0] for row in cursor.fetchall()]
        print(f"      ✓ Table 'games' has {len(games_columns)} columns")
        
        # team_game_stats table
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'hcl' AND table_name = 'team_game_stats'
        """)
        stats_columns = [row[0] for row in cursor.fetchall()]
        print(f"      ✓ Table 'team_game_stats' has {len(stats_columns)} columns")
        
        # Check views return data structure (no data yet, just schema)
        print(f"\n[6/6] Checking view structures...")
        cursor.execute("SELECT * FROM hcl.v_team_season_stats LIMIT 0")
        view_cols = len(cursor.description)
        print(f"      ✓ View 'v_team_season_stats' has {view_cols} columns")
        
        cursor.execute("SELECT * FROM hcl.v_game_matchup_display LIMIT 0")
        view_cols = len(cursor.description)
        print(f"      ✓ View 'v_game_matchup_display' has {view_cols} columns")
        
        cursor.execute("SELECT * FROM hcl.v_game_matchup_with_proj LIMIT 0")
        view_cols = len(cursor.description)
        print(f"      ✓ View 'v_game_matchup_with_proj' has {view_cols} columns")
        
        print(f"\n✅ All validation checks passed")
        
    except Exception as e:
        print(f"\n❌ VALIDATION ERROR: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def print_next_steps():
    """Print next steps for user"""
    print(f"\n{'='*70}")
    print(f"SETUP COMPLETE")
    print(f"{'='*70}\n")
    
    print(f"✅ Test database '{TEST_DB_NAME}' created")
    print(f"✅ Schema 'hcl' with 2 tables, 3 views, 5+ indexes")
    print(f"✅ Validation passed\n")
    
    print(f"NEXT STEPS:\n")
    print(f"1. Enhance nflverse_data_loader.py to write to database")
    print(f"   - Add --output database flag")
    print(f"   - UPSERT to hcl.games and hcl.team_game_stats\n")
    
    print(f"2. Load Week 7 test data:")
    print(f"   python nflverse_data_loader.py --seasons 2024 --weeks 7 --output database\n")
    
    print(f"3. Verify data loaded:")
    print(f"   psql -d {TEST_DB_NAME} -c \"SELECT COUNT(*) FROM hcl.games;\"\n")
    
    print(f"4. Test views:")
    print(f"   psql -d {TEST_DB_NAME} -c \"SELECT * FROM hcl.v_game_matchup_display LIMIT 5;\"\n")
    
    print(f"CONNECTION INFO:")
    print(f"   Database: {TEST_DB_NAME}")
    print(f"   Host:     {DB_HOST}")
    print(f"   Port:     {DB_PORT}")
    print(f"   Schema:   hcl")
    print(f"\n{'='*70}\n")


def main():
    """Main execution"""
    try:
        print(f"\n{'='*70}")
        print(f"HC LOMBARDO - TEST DATABASE SETUP")
        print(f"Sprint 5-6: Historical Data Storage")
        print(f"{'='*70}\n")
        
        print(f"Target Database: {TEST_DB_NAME}")
        print(f"Schema File: {SCHEMA_FILE}")
        print(f"Host: {DB_HOST}:{DB_PORT}\n")
        
        # Step 1: Create database
        create_test_database()
        
        # Step 2: Run schema
        run_schema_file()
        
        # Step 3: Validate
        validate_schema()
        
        # Print next steps
        print_next_steps()
        
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ SETUP FAILED")
        print(f"{'='*70}\n")
        print(f"Error: {e}\n")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
