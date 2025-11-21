-- =============================================================================
-- ML PREDICTIONS TRACKING TABLE
-- =============================================================================
-- Purpose: Track AI predictions vs actual results for performance monitoring
-- Created: November 20, 2025
-- =============================================================================

CREATE TABLE IF NOT EXISTS hcl.ml_predictions (
  prediction_id SERIAL PRIMARY KEY,
  game_id TEXT NOT NULL REFERENCES hcl.games(game_id),
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

-- Index for quick lookups
CREATE INDEX IF NOT EXISTS idx_ml_predictions_season_week ON hcl.ml_predictions(season, week);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_game_date ON hcl.ml_predictions(game_date);

-- Comments
COMMENT ON TABLE hcl.ml_predictions IS 'Tracks ML model predictions vs actual results for performance monitoring (2025+)';
COMMENT ON COLUMN hcl.ml_predictions.win_prediction_correct IS 'TRUE if predicted_winner matches actual_winner';
COMMENT ON COLUMN hcl.ml_predictions.margin_prediction_error IS 'ABS(predicted_margin - actual_margin) - lower is better';
