"""
Create HCL Feature Engineering Views
Executes hcl_feature_views.sql to create analytical views
"""

import psycopg2
from db_config import get_connection_string

def create_views():
    """Create all feature engineering views"""
    
    print("="*80)
    print("CREATING HCL FEATURE ENGINEERING VIEWS")
    print("="*80)
    
    # Read SQL file
    with open('hcl_feature_views.sql', 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Connect to database
    try:
        conn = psycopg2.connect(get_connection_string())
        conn.autocommit = True  # Enable autocommit for DDL statements
        cur = conn.cursor()
        
        print("\n✓ Connected to database")
        
        # Extract only the CREATE VIEW statements
        view_statements = []
        current_statement = []
        in_view_creation = False
        
        for line in sql_content.split('\n'):
            line_upper = line.strip().upper()
            
            # Start of a view
            if line_upper.startswith('CREATE OR REPLACE VIEW'):
                in_view_creation = True
                current_statement = [line]
            elif in_view_creation:
                current_statement.append(line)
                # End of view (semicolon at end of line)
                if line.strip().endswith(';'):
                    view_statements.append('\n'.join(current_statement))
                    current_statement = []
                    in_view_creation = False
        
        print(f"\nFound {len(view_statements)} view definitions")
        
        # Create each view
        for i, statement in enumerate(view_statements, 1):
            try:
                # Extract view name
                view_name = statement.split('hcl.')[1].split(' ')[0].split('\n')[0]
                print(f"\nCreating view {i}/{len(view_statements)}: {view_name}")
                
                cur.execute(statement)
                print(f"✓ Created view: {view_name}")
                
            except Exception as e:
                print(f"❌ Error creating view: {str(e)[:200]}")
        
        print(f"\n✓ Created {len(view_statements)} views")
        
        # Verify views were created
        print("\n" + "="*80)
        print("VERIFYING VIEWS")
        print("="*80)
        
        cur.execute("""
            SELECT viewname 
            FROM pg_views 
            WHERE schemaname = 'hcl' 
              AND viewname LIKE 'v_%'
            ORDER BY viewname
        """)
        
        views = cur.fetchall()
        print(f"\nFound {len(views)} views in hcl schema:")
        for view in views:
            print(f"  - {view[0]}")
        
        # Get row counts
        print("\n" + "="*80)
        print("ROW COUNTS")
        print("="*80)
        
        view_names = [
            'v_team_betting_performance',
            'v_weather_impact_analysis',
            'v_rest_advantage',
            'v_referee_tendencies'
        ]
        
        for view_name in view_names:
            try:
                cur.execute(f"SELECT COUNT(*) FROM hcl.{view_name}")
                count = cur.fetchone()[0]
                print(f"  {view_name}: {count} rows")
            except Exception as e:
                print(f"  {view_name}: Error - {str(e)[:50]}")
        
        # Sample queries
        print("\n" + "="*80)
        print("SAMPLE DATA")
        print("="*80)
        
        # Best ATS teams in 2025
        print("\n1. Top 5 Teams Against The Spread (2025):")
        cur.execute("""
            SELECT team, total_games, ats_wins, ats_losses, ats_win_pct
            FROM hcl.v_team_betting_performance
            WHERE season = 2025
            ORDER BY ats_win_pct DESC
            LIMIT 5
        """)
        
        for row in cur.fetchall():
            print(f"   {row[0]}: {row[1]} games, {row[2]}-{row[3]} ATS ({row[4]}%)")
        
        # Weather impact
        print("\n2. Scoring by Stadium Type:")
        cur.execute("""
            SELECT roof, 
                   COUNT(*) as game_count,
                   ROUND(AVG(avg_total_points)::numeric, 1) as avg_ppg
            FROM hcl.v_weather_impact_analysis
            GROUP BY roof
            ORDER BY avg_ppg DESC
        """)
        
        for row in cur.fetchall():
            print(f"   {row[0]}: {row[2]} PPG ({row[1]} games)")
        
        # Rest advantage
        print("\n3. Win Percentage by Rest Days:")
        cur.execute("""
            SELECT rest_category, 
                   SUM(total_games) as games,
                   ROUND(AVG(win_pct)::numeric, 1) as avg_win_pct
            FROM hcl.v_rest_advantage
            WHERE season = 2025
            GROUP BY rest_category
            ORDER BY MIN(rest_days)
        """)
        
        for row in cur.fetchall():
            print(f"   {row[0]}: {row[2]}% ({row[1]} games)")
        
        # Referee stats
        print("\n4. Referees with Most Games (2025):")
        cur.execute("""
            SELECT referee, total_games, home_win_pct, avg_total_points
            FROM hcl.v_referee_tendencies
            WHERE season = 2025
            ORDER BY total_games DESC
            LIMIT 5
        """)
        
        for row in cur.fetchall():
            print(f"   {row[0]}: {row[1]} games, {row[2]}% home wins, {row[3]} PPG")
        
        cur.close()
        conn.close()
        
        print("\n" + "="*80)
        print("✅ ALL VIEWS CREATED SUCCESSFULLY!")
        print("="*80)
        print("\nViews are ready to use:")
        print("  - hcl.v_team_betting_performance")
        print("  - hcl.v_weather_impact_analysis")
        print("  - hcl.v_rest_advantage")
        print("  - hcl.v_referee_tendencies")
        print("\nExample query:")
        print("  SELECT * FROM hcl.v_team_betting_performance WHERE team = 'BAL';")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    create_views()
