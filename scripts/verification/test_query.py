from db_config import DATABASE_CONFIG
import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(**DATABASE_CONFIG)
cur = conn.cursor(cursor_factory=RealDictCursor)

team_abbr = 'KC'
season = 2025

query = """
    SELECT 
        g.game_id,
        g.week,
        CASE 
            WHEN g.home_team = %s THEN g.away_team
            ELSE g.home_team
        END as opponent,
        CASE 
            WHEN g.home_team = %s THEN TRUE
            ELSE FALSE
        END as is_home,
        tgs.result,
        g.home_score,
        g.away_score
    FROM hcl.games g
    LEFT JOIN hcl.team_game_stats tgs ON g.game_id = tgs.game_id 
        AND tgs.team = %s
    WHERE (g.home_team = %s OR g.away_team = %s)
        AND g.season = %s
        AND g.is_postseason = FALSE
    ORDER BY g.week ASC
"""

cur.execute(query, (team_abbr, team_abbr, team_abbr, team_abbr, team_abbr, season))
games = cur.fetchall()

print(f"Total games: {len(games)}\n")
for game in games:
    result = game['result'] or 'TBD'
    loc = 'vs' if game['is_home'] else '@'
    print(f"Week {game['week']:2d}: {loc} {game['opponent']} - {result}")

cur.close()
conn.close()
