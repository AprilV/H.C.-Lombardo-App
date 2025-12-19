-- Create table for Elo-based predictions
-- Sprint 10: Elo System Implementation
-- Date: December 19, 2025

CREATE TABLE IF NOT EXISTS hcl.ml_predictions_elo (
    prediction_id SERIAL PRIMARY KEY,
    game_id VARCHAR(50) UNIQUE NOT NULL,
    season INTEGER NOT NULL,
    week INTEGER NOT NULL,
    game_date TIMESTAMP,
    
    -- Teams
    home_team VARCHAR(10) NOT NULL,
    away_team VARCHAR(10) NOT NULL,
    
    -- Elo Ratings
    home_elo DECIMAL(6,1) NOT NULL,
    away_elo DECIMAL(6,1) NOT NULL,
    elo_diff DECIMAL(6,1) NOT NULL,
    
    -- Win Probabilities
    home_win_prob DECIMAL(5,3) NOT NULL,
    away_win_prob DECIMAL(5,3) NOT NULL,
    
    -- Prediction
    predicted_winner VARCHAR(10) NOT NULL,
    confidence DECIMAL(5,3) NOT NULL,
    
    -- Spread Prediction
    elo_spread DECIMAL(5,1) NOT NULL,
    vegas_spread DECIMAL(5,1),
    spread_diff DECIMAL(5,1),
    
    -- Analysis
    split_prediction BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    prediction_date TIMESTAMP DEFAULT NOW(),
    
    -- Actual Results (populated after game)
    actual_winner VARCHAR(10),
    actual_spread DECIMAL(5,1),
    prediction_correct BOOLEAN,
    spread_error DECIMAL(5,1),
    
    -- Indexes
    CONSTRAINT fk_game FOREIGN KEY (game_id) REFERENCES hcl.games(game_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_elo_pred_season_week ON hcl.ml_predictions_elo(season, week);
CREATE INDEX IF NOT EXISTS idx_elo_pred_game_date ON hcl.ml_predictions_elo(game_date);
CREATE INDEX IF NOT EXISTS idx_elo_pred_teams ON hcl.ml_predictions_elo(home_team, away_team);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON hcl.ml_predictions_elo TO postgres;
GRANT USAGE, SELECT ON SEQUENCE hcl.ml_predictions_elo_prediction_id_seq TO postgres;

COMMENT ON TABLE hcl.ml_predictions_elo IS 'NFL game predictions using Elo rating system';
COMMENT ON COLUMN hcl.ml_predictions_elo.elo_diff IS 'Home Elo minus Away Elo (positive = home favored)';
COMMENT ON COLUMN hcl.ml_predictions_elo.elo_spread IS 'Predicted point spread from Elo difference';
COMMENT ON COLUMN hcl.ml_predictions_elo.split_prediction IS 'True when Elo disagrees significantly with Vegas';
