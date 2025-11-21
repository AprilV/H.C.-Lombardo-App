"""
Setup ML Predictions Tracking Table
Creates table to track AI predictions vs actual results for performance monitoring
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def setup_predictions_tracking():
    """Create ml_predictions table for tracking model performance"""
    
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'nfl_analytics'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '')
    )
    
    cur = conn.cursor()
    
    sql = """
    -- ML Predictions Tracking Table
    CREATE TABLE IF NOT EXISTS hcl.ml_predictions (
      prediction_id SERIAL PRIMARY KEY,
      game_id TEXT NOT NULL,
      season INT NOT NULL,
      week INT NOT NULL,
      
      -- Game Info
      home_team TEXT NOT NULL,
      away_team TEXT NOT NULL,
      game_date DATE,
      
      -- Win/Loss Model Predictions (Classification)
      predicted_winner TEXT,
      win_confidence DOUBLE PRECISION,
      home_win_prob DOUBLE PRECISION,
      away_win_prob DOUBLE PRECISION,
      
      -- Point Spread Model Predictions (Regression)
      predicted_home_score DOUBLE PRECISION,
      predicted_away_score DOUBLE PRECISION,
      predicted_margin DOUBLE PRECISION,
      ai_spread DOUBLE PRECISION,
      
      -- Vegas Lines (for comparison)
      vegas_spread DOUBLE PRECISION,
      vegas_total DOUBLE PRECISION,
      
      -- Actual Results (filled in after game)
      actual_winner TEXT,
      actual_home_score INT,
      actual_away_score INT,
      actual_margin INT,
      
      -- Performance Metrics (calculated after game)
      win_prediction_correct BOOLEAN,
      score_prediction_error_home DOUBLE PRECISION,
      score_prediction_error_away DOUBLE PRECISION,
      margin_prediction_error DOUBLE PRECISION,
      
      -- Timestamps
      predicted_at TIMESTAMP DEFAULT NOW(),
      result_recorded_at TIMESTAMP,
      
      -- Ensure one prediction per game
      UNIQUE(game_id)
    );
    
    -- Indexes
    CREATE INDEX IF NOT EXISTS idx_ml_predictions_season_week ON hcl.ml_predictions(season, week);
    CREATE INDEX IF NOT EXISTS idx_ml_predictions_game_date ON hcl.ml_predictions(game_date);
    """
    
    cur.execute(sql)
    conn.commit()
    
    print("✅ Created hcl.ml_predictions table")
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    setup_predictions_tracking()
