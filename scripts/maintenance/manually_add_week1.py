"""
Manually add Week 1 predictions by checking existing games
Since Week 1 was already played, we'll create retroactive predictions
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import DATABASE_CONFIG

def add_week1_from_games():
    print("=" * 70)
    print("Manually Adding Week 1 2025 Predictions from Completed Games")
    print("=" * 70)
    
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if Week 1 games exist
    cur.execute("""
        SELECT game_id, week, home_team, away_team, game_date,
               home_score, away_score, spread_line, total_line
        FROM hcl.games 
        WHERE season = 2025 AND week = 1
        ORDER BY game_date
    """)
    
    games = cur.fetchall()
    
    if not games:
        print("\n❌ No Week 1 games found in database!")
        cur.close()
        conn.close()
        return
    
    print(f"\n✅ Found {len(games)} Week 1 games")
    
    # Check if predictions already exist
    cur.execute("SELECT COUNT(*) as count FROM hcl.ml_predictions WHERE season = 2025 AND week = 1")
    existing = cur.fetchone()['count']
    
    if existing > 0:
        print(f"\n⚠️  Week 1 already has {existing} predictions.")
        print("   Deleting old predictions and recreating...")
        cur.execute("DELETE FROM hcl.ml_predictions WHERE season = 2025 AND week = 1")
        conn.commit()
    
    print("\n[1/2] Creating predictions for completed games...")
    saved = 0
    
    for game in games:
        # Create a "prediction" based on Vegas line or 50/50 split
        vegas_spread = game['spread_line'] if game['spread_line'] else 0
        
        # Predict based on Vegas line (favorite wins)
        if vegas_spread < 0:  # Home team favored
            predicted_winner = game['home_team']
            home_win_prob = 0.55
            predicted_margin = abs(vegas_spread)
        elif vegas_spread > 0:  # Away team favored  
            predicted_winner = game['away_team']
            home_win_prob = 0.45
            predicted_margin = abs(vegas_spread)
        else:  # Even matchup
            predicted_winner = game['home_team']
            home_win_prob = 0.50
            predicted_margin = 3
        
        # Estimate scores
        total_line = game['total_line'] if game['total_line'] else 45
        if predicted_winner == game['home_team']:
            predicted_home_score = (total_line + predicted_margin) / 2
            predicted_away_score = (total_line - predicted_margin) / 2
        else:
            predicted_home_score = (total_line - predicted_margin) / 2
            predicted_away_score = (total_line + predicted_margin) / 2
        
        insert_sql = """
            INSERT INTO hcl.ml_predictions (
                game_id, season, week, home_team, away_team, game_date,
                predicted_winner, win_confidence, home_win_prob, away_win_prob,
                predicted_home_score, predicted_away_score, predicted_margin, ai_spread,
                vegas_spread, vegas_total
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cur.execute(insert_sql, (
            game['game_id'],
            2025,
            1,
            game['home_team'],
            game['away_team'],
            game['game_date'],
            predicted_winner,
            abs(home_win_prob - 0.5) * 2,  # Confidence 0-1
            home_win_prob,
            1 - home_win_prob,
            predicted_home_score,
            predicted_away_score,
            predicted_margin,
            -vegas_spread if predicted_winner == game['home_team'] else vegas_spread,
            vegas_spread,
            total_line
        ))
        saved += 1
    
    conn.commit()
    print(f"    ✅ Created {saved} predictions")
    
    print("\n[2/2] Updating with actual results...")
    update_sql = """
        UPDATE hcl.ml_predictions p
        SET 
            actual_winner = CASE 
                WHEN g.home_score > g.away_score THEN g.home_team
                WHEN g.away_score > g.home_score THEN g.away_team
                ELSE 'TIE'
            END,
            actual_home_score = g.home_score,
            actual_away_score = g.away_score,
            actual_margin = ABS(g.home_score - g.away_score),
            win_prediction_correct = (
                (p.predicted_winner = g.home_team AND g.home_score > g.away_score) OR
                (p.predicted_winner = g.away_team AND g.away_score > g.home_score)
            ),
            margin_prediction_error = ABS(p.predicted_margin - ABS(g.home_score - g.away_score)),
            score_prediction_error_home = ABS(p.predicted_home_score - g.home_score),
            score_prediction_error_away = ABS(p.predicted_away_score - g.away_score),
            result_recorded_at = NOW()
        FROM hcl.games g
        WHERE p.game_id = g.game_id
            AND p.season = 2025
            AND p.week = 1
            AND g.home_score IS NOT NULL
            AND g.away_score IS NOT NULL
    """
    
    cur.execute(update_sql)
    updated = cur.rowcount
    conn.commit()
    print(f"    ✅ Updated {updated} predictions with actual results")
    
    # Show summary
    print("\n" + "=" * 70)
    print("WEEK 1 SUMMARY")
    print("=" * 70)
    
    cur.execute("""
        SELECT 
            COUNT(*) as total_games,
            SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as correct,
            CAST(AVG(CASE WHEN win_prediction_correct THEN 100.0 ELSE 0.0 END) AS NUMERIC(10,1)) as accuracy,
            CAST(AVG(margin_prediction_error) AS NUMERIC(10,1)) as avg_margin_error
        FROM hcl.ml_predictions
        WHERE season = 2025 AND week = 1 AND result_recorded_at IS NOT NULL
    """)
    
    stats = cur.fetchone()
    if stats and stats['total_games'] > 0:
        print(f"\nGames Tracked: {stats['total_games']}")
        print(f"Correct Picks: {stats['correct']}/{stats['total_games']}")
        print(f"Accuracy: {stats['accuracy']}%")
        print(f"Avg Margin Error: {stats['avg_margin_error']} pts")
        print(f"\n💡 Note: Week 1 uses Vegas-based predictions since it was")
        print(f"   played before ML tracking started.")
    
    cur.close()
    conn.close()
    print("\n✅ Week 1 successfully added to tracking!")

if __name__ == '__main__':
    add_week1_from_games()
