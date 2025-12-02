import psycopg2

conn = psycopg2.connect('dbname=nfl_analytics user=postgres password=aprilv120 host=localhost')
cur = conn.cursor()

# Check Dallas results
cur.execute("""
    SELECT result, COUNT(*) 
    FROM hcl.team_game_stats 
    WHERE team='DAL' AND season=2025 
    GROUP BY result
""")
print("Dallas 2025 Results:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Check if ties exist anywhere in 2025
cur.execute("""
    SELECT team, COUNT(*) as tie_count
    FROM hcl.team_game_stats 
    WHERE season=2025 AND result='T'
    GROUP BY team
    ORDER BY tie_count DESC
""")
print("\nAll teams with ties in 2025:")
ties = cur.fetchall()
if ties:
    for row in ties:
        print(f"  {row[0]}: {row[1]} ties")
else:
    print("  No ties found")

cur.close()
conn.close()
