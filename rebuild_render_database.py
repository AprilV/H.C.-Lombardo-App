#!/usr/bin/env python3
"""
COMPLETE RENDER DATABASE REBUILD
=================================
1. Drop and recreate HCL schema with correct columns (including EPA)
2. Copy all historical data from local database (1999-2024)
3. Load 2025 season with EPA calculations from nflverse

This will make Render database match your working local database.
"""

import psycopg2
from psycopg2.extras import execute_values
import sys

RENDER_URL = "postgresql://nfl_user:rzkKyzQq9pTas14pXDJU3fm8cCZObAh5@dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com/nfl_analytics"

LOCAL_CONN = {
    'dbname': 'nfl_analytics',
    'user': 'postgres',
    'password': 'aprilv120',
    'host': 'localhost',
    'port': '5432'
}

def main():
    print("\n" + "="*80)
    print("🔧 COMPLETE RENDER DATABASE REBUILD")
    print("="*80)
    
    # Connect to both databases
    print("\n📡 Connecting to databases...")
    try:
        local_conn = psycopg2.connect(**LOCAL_CONN)
        local_cur = local_conn.cursor()
        render_conn = psycopg2.connect(RENDER_URL)
        render_cur = render_conn.cursor()
        print("   ✅ Connected to LOCAL and RENDER")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    # STEP 1: Get schema from local database
    print("\n1️⃣ Extracting schema from LOCAL database...")
    try:
        # Get games table structure
        local_cur.execute("""
            SELECT column_name, data_type, character_maximum_length, 
                   numeric_precision, numeric_scale, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'hcl' AND table_name = 'games'
            ORDER BY ordinal_position
        """)
        games_columns = local_cur.fetchall()
        
        # Get team_game_stats table structure
        local_cur.execute("""
            SELECT column_name, data_type, character_maximum_length,
                   numeric_precision, numeric_scale, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'hcl' AND table_name = 'team_game_stats'
            ORDER BY ordinal_position
        """)
        stats_columns = local_cur.fetchall()
        
        print(f"   ✅ Extracted schema: {len(games_columns)} columns in games, {len(stats_columns)} in team_game_stats")
    except Exception as e:
        print(f"   ❌ Failed to extract schema: {e}")
        return False
    
    # STEP 2: Drop and recreate schema on Render
    print("\n2️⃣ Recreating HCL schema on RENDER...")
    try:
        render_cur.execute("DROP SCHEMA IF EXISTS hcl CASCADE")
        render_cur.execute("CREATE SCHEMA hcl")
        render_conn.commit()
        print("   ✅ Old schema dropped, new schema created")
    except Exception as e:
        print(f"   ❌ Failed to recreate schema: {e}")
        return False
    
    # STEP 3: Create games table with correct structure
    print("\n3️⃣ Creating tables on RENDER...")
    try:
        # Build CREATE TABLE statement for games
        cols = []
        for col_name, data_type, char_len, num_prec, num_scale, nullable, default in games_columns:
            col_def = f"{col_name} "
            
            if data_type == 'character varying':
                col_def += f"VARCHAR({char_len})" if char_len else "TEXT"
            elif data_type == 'numeric':
                col_def += f"NUMERIC({num_prec},{num_scale})"
            elif data_type == 'timestamp with time zone':
                col_def += "TIMESTAMPTZ"
            elif data_type == 'timestamp without time zone':
                col_def += "TIMESTAMP"
            elif data_type == 'double precision':
                col_def += "DOUBLE PRECISION"
            else:
                col_def += data_type.upper()
            
            if nullable == 'NO':
                col_def += " NOT NULL"
            
            if default and 'nextval' not in default:
                col_def += f" DEFAULT {default}"
            
            cols.append(col_def)
        
        games_sql = f"CREATE TABLE hcl.games ({', '.join(cols)})"
        render_cur.execute(games_sql)
        
        # Build CREATE TABLE for team_game_stats
        cols = []
        for col_name, data_type, char_len, num_prec, num_scale, nullable, default in stats_columns:
            col_def = f"{col_name} "
            
            if data_type == 'character varying':
                col_def += f"VARCHAR({char_len})" if char_len else "TEXT"
            elif data_type == 'numeric':
                col_def += f"NUMERIC({num_prec},{num_scale})"
            elif data_type == 'timestamp with time zone':
                col_def += "TIMESTAMPTZ"
            elif data_type == 'timestamp without time zone':
                col_def += "TIMESTAMP"
            elif data_type == 'double precision':
                col_def += "DOUBLE PRECISION"
            elif data_type == 'integer':
                col_def += "INTEGER"
            elif data_type == 'boolean':
                col_def += "BOOLEAN"
            else:
                col_def += data_type.upper()
            
            if nullable == 'NO' and 'serial' not in data_type:
                col_def += " NOT NULL"
            
            if default and 'nextval' not in default:
                col_def += f" DEFAULT {default}"
            
            cols.append(col_def)
        
        stats_sql = f"CREATE TABLE hcl.team_game_stats ({', '.join(cols)})"
        render_cur.execute(stats_sql)
        
        # Add primary keys
        render_cur.execute("ALTER TABLE hcl.games ADD PRIMARY KEY (game_id)")
        render_cur.execute("ALTER TABLE hcl.team_game_stats ADD PRIMARY KEY (game_id, team)")
        
        # Add indexes
        render_cur.execute("CREATE INDEX idx_games_season_week ON hcl.games(season, week)")
        render_cur.execute("CREATE INDEX idx_team_stats_team ON hcl.team_game_stats(team)")
        render_cur.execute("CREATE INDEX idx_team_stats_season ON hcl.team_game_stats(season)")
        
        render_conn.commit()
        print("   ✅ Tables created with correct schema")
    except Exception as e:
        print(f"   ❌ Failed to create tables: {e}")
        render_conn.rollback()
        return False
    
    # STEP 4: Copy historical data (1999-2024) from local
    print("\n4️⃣ Copying historical data (1999-2024) from LOCAL to RENDER...")
    try:
        # Get column names dynamically
        games_cols = [c[0] for c in games_columns]
        stats_cols = [c[0] for c in stats_columns]
        
        # Copy games (excluding 2025)
        local_cur.execute(f"""
            SELECT {', '.join(games_cols)}
            FROM hcl.games
            WHERE season < 2025
            ORDER BY season, week
        """)
        games_data = local_cur.fetchall()
        
        if games_data:
            execute_values(
                render_cur,
                f"INSERT INTO hcl.games ({', '.join(games_cols)}) VALUES %s",
                games_data
            )
            render_conn.commit()
            print(f"   ✅ Copied {len(games_data):,} games (1999-2024)")
        
        # Copy team_game_stats (excluding 2025)
        local_cur.execute(f"""
            SELECT {', '.join(stats_cols)}
            FROM hcl.team_game_stats
            WHERE season < 2025
            ORDER BY season, week
        """)
        stats_data = local_cur.fetchall()
        
        if stats_data:
            execute_values(
                render_cur,
                f"INSERT INTO hcl.team_game_stats ({', '.join(stats_cols)}) VALUES %s",
                stats_data
            )
            render_conn.commit()
            print(f"   ✅ Copied {len(stats_data):,} team game stats (1999-2024)")
        
    except Exception as e:
        print(f"   ❌ Failed to copy data: {e}")
        render_conn.rollback()
        return False
    
    # STEP 5: Verify
    print("\n5️⃣ Verifying RENDER database...")
    render_cur.execute("SELECT COUNT(*), MIN(season), MAX(season) FROM hcl.games WHERE season < 2025")
    games_count, min_s, max_s = render_cur.fetchone()
    render_cur.execute("SELECT COUNT(*) FROM hcl.team_game_stats WHERE season < 2025")
    stats_count = render_cur.fetchone()[0]
    
    print(f"   • Historical games: {games_count:,} ({min_s}-{max_s})")
    print(f"   • Historical stats: {stats_count:,}")
    
    # Check if EPA columns exist
    render_cur.execute("""
        SELECT column_name 
        FROM information_schema.columns
        WHERE table_schema = 'hcl' 
        AND table_name = 'team_game_stats'
        AND column_name LIKE '%epa%'
    """)
    epa_cols = [r[0] for r in render_cur.fetchall()]
    print(f"   • EPA columns: {', '.join(epa_cols) if epa_cols else 'NONE FOUND!'}")
    
    print("\n" + "="*80)
    print("✅ HISTORICAL DATA LOAD COMPLETE!")
    print("="*80)
    print("\n📝 Next step: Run ingest_historical_games.py for 2025 season")
    print("   Command: python ingest_historical_games.py --production --seasons 2025")
    
    local_conn.close()
    render_conn.close()
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
