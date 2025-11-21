# 🎯 AI Prediction Tracking System

## Overview
Complete system to track and analyze AI model predictions vs actual game results for the 2025 NFL season and beyond.

---

## 📊 Database Structure

### Table: `hcl.ml_predictions`

**Purpose:** Store predictions when generated and update with actual results after games complete.

```sql
CREATE TABLE hcl.ml_predictions (
    -- Primary Key
    prediction_id SERIAL PRIMARY KEY,
    game_id TEXT UNIQUE NOT NULL,
    
    -- Game Information
    season INTEGER NOT NULL,
    week INTEGER NOT NULL,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    game_date TIMESTAMP,
    
    -- Win/Loss Model Predictions
    predicted_winner TEXT,
    win_confidence DOUBLE PRECISION,
    home_win_prob DOUBLE PRECISION,
    away_win_prob DOUBLE PRECISION,
    
    -- Score & Spread Predictions
    predicted_home_score DOUBLE PRECISION,
    predicted_away_score DOUBLE PRECISION,
    predicted_margin DOUBLE PRECISION,
    ai_spread DOUBLE PRECISION,
    vegas_spread DOUBLE PRECISION,
    vegas_total DOUBLE PRECISION,
    
    -- Actual Results (filled post-game)
    actual_winner TEXT,
    actual_home_score INTEGER,
    actual_away_score INTEGER,
    actual_margin INTEGER,
    
    -- Performance Metrics
    win_prediction_correct BOOLEAN,
    score_prediction_error_home DOUBLE PRECISION,
    score_prediction_error_away DOUBLE PRECISION,
    margin_prediction_error DOUBLE PRECISION,
    
    -- Timestamps
    predicted_at TIMESTAMP DEFAULT NOW(),
    result_recorded_at TIMESTAMP
);

CREATE INDEX idx_ml_predictions_season_week ON hcl.ml_predictions(season, week);
CREATE INDEX idx_ml_predictions_game_date ON hcl.ml_predictions(game_date);
```

---

## 🔄 Workflow

### Phase 1: Prediction Generation
**When:** User visits ML Predictions page or Homepage (ticker)  
**Endpoint:** `GET /api/ml/predict-upcoming`

**What Happens:**
1. Generate predictions for upcoming week using both models:
   - **Classification Model:** Win/Loss + confidence %
   - **Regression Model:** Predicted scores + spread
2. **Automatically save** predictions to `hcl.ml_predictions` table
3. Return predictions to frontend for display

**Code:**
```python
# api_routes_ml.py - predict_upcoming()
predictions = pred.predict_upcoming()

# Auto-save to tracking table
for p in predictions:
    INSERT INTO hcl.ml_predictions (
        game_id, season, week, home_team, away_team,
        predicted_winner, win_confidence, home_win_prob, away_win_prob,
        predicted_home_score, predicted_away_score, predicted_margin,
        ai_spread, vegas_spread, vegas_total
    ) VALUES (...)
    ON CONFLICT (game_id) DO UPDATE SET ...
```

### Phase 2: Game Completion & Result Update
**When:** Games finish and data is reloaded  
**Endpoint:** `POST /api/ml/update-results`

**What Happens:**
1. Query all predictions that have corresponding completed games
2. Update `actual_winner`, `actual_home_score`, `actual_away_score`
3. Calculate performance metrics:
   - `win_prediction_correct` - Boolean (did we pick the right winner?)
   - `margin_prediction_error` - Absolute error in point margin
   - `score_prediction_error_home/away` - Score accuracy
4. Set `result_recorded_at` timestamp

**Code:**
```python
# api_routes_ml.py - update_results()
UPDATE hcl.ml_predictions mp
SET 
    actual_winner = CASE 
        WHEN g.home_score > g.away_score THEN g.home_team
        ELSE g.away_team
    END,
    actual_home_score = g.home_score,
    actual_away_score = g.away_score,
    win_prediction_correct = (predicted_winner = actual_winner),
    margin_prediction_error = ABS(predicted_margin - actual_margin),
    result_recorded_at = NOW()
FROM hcl.games g
WHERE mp.game_id = g.game_id
  AND g.home_score IS NOT NULL  -- Game is complete
  AND mp.result_recorded_at IS NULL  -- Not already updated
```

**How to Trigger:**
```bash
# After running data update (ingest_historical_games.py)
curl -X POST http://localhost:5000/api/ml/update-results
```

### Phase 3: Performance Display
**Where:** Admin Panel > System Status tab  
**Endpoint:** `GET /api/ml/performance-stats?season=2025`

**What Shows:**
- **Overall Stats:**
  - Total games predicted
  - Correct picks count
  - Win/Loss accuracy %
  - Average margin error (MAE)
  
- **Week-by-Week Breakdown:**
  - Per-week accuracy
  - Games predicted each week
  - MAE per week

**SQL Query:**
```sql
SELECT 
    COUNT(*) as total_games,
    SUM(CASE WHEN win_prediction_correct THEN 1 ELSE 0 END) as correct_predictions,
    ROUND(AVG(CASE WHEN win_prediction_correct THEN 100.0 ELSE 0.0 END), 2) as win_accuracy,
    ROUND(AVG(margin_prediction_error), 2) as avg_margin_error
FROM hcl.ml_predictions
WHERE season = 2025
  AND result_recorded_at IS NOT NULL
```

---

## 🎨 Frontend Components

### Admin.js - Performance Display
```javascript
const [modelPerformance, setModelPerformance] = useState(null);

const fetchModelPerformance = async () => {
    const response = await fetch(`${API_URL}/api/ml/performance-stats?season=2025`);
    const data = await response.json();
    setModelPerformance(data);
};

// Display:
// - 4 stat boxes (games, correct, accuracy %, MAE)
// - Week-by-week table
// - Auto-refreshes with system status
```

### MLPredictions.js - Checkmarks (Future)
```javascript
// For completed games, show ✅ or ❌ based on win_prediction_correct
{prediction.result_recorded_at && (
    <div className="prediction-result">
        {prediction.win_prediction_correct ? '✅ Correct' : '❌ Incorrect'}
    </div>
)}
```

---

## 📡 API Endpoints

### 1. Save Predictions (Automatic)
**Endpoint:** `GET /api/ml/predict-upcoming`  
**Purpose:** Generate predictions AND save to tracking table  
**Response:**
```json
{
    "season": 2025,
    "week": 10,
    "total_games": 16,
    "predictions": [
        {
            "game_id": "2025_10_KC_BUF",
            "home_team": "KC",
            "away_team": "BUF",
            "predicted_winner": "KC",
            "confidence": 0.68,
            "predicted_home_score": 27.3,
            "predicted_away_score": 23.8,
            "ai_spread": -3.5,
            "vegas_spread": -4.0
        }
    ]
}
```

### 2. Update Results (Manual Trigger)
**Endpoint:** `POST /api/ml/update-results`  
**Purpose:** Update predictions with actual game results  
**Response:**
```json
{
    "success": true,
    "updated": 12,
    "message": "Updated 12 predictions with actual results"
}
```

### 3. Get Performance Stats
**Endpoint:** `GET /api/ml/performance-stats?season=2025&week=10`  
**Purpose:** Retrieve model performance metrics  
**Query Params:**
- `season` (required) - Season year
- `week` (optional) - Filter to specific week

**Response:**
```json
{
    "success": true,
    "season": 2025,
    "overall": {
        "total_games": 48,
        "correct_predictions": 32,
        "win_accuracy": 66.67,
        "avg_margin_error": 9.8
    },
    "by_week": [
        {
            "week": 10,
            "games": 16,
            "correct": 11,
            "accuracy": 68.8,
            "mae": 9.2
        }
    ]
}
```

---

## 🧪 Testing the System

### Step 1: Generate Predictions
1. Visit ML Predictions page: http://localhost:3000/mlpredictions
2. Predictions automatically saved to database
3. Check terminal: "✅ Auto-saved 16 predictions to tracking table"

### Step 2: Verify Saved Data
```sql
SELECT 
    game_id, 
    predicted_winner, 
    win_confidence, 
    predicted_at 
FROM hcl.ml_predictions 
WHERE season = 2025 
ORDER BY predicted_at DESC;
```

### Step 3: Simulate Game Results
```sql
-- Manually update a game result for testing
UPDATE hcl.games 
SET home_score = 28, away_score = 24 
WHERE game_id = '2025_10_KC_BUF';
```

### Step 4: Update Predictions with Results
```bash
curl -X POST http://localhost:5000/api/ml/update-results
```

### Step 5: Check Performance Stats
1. Visit Admin page: http://localhost:3000/admin
2. Click "System Status" tab
3. Scroll to "2025 Season Performance (Live Tracking)"
4. Verify stats appear:
   - Games Predicted: 16
   - Correct Picks: 11
   - Win/Loss Accuracy: 68.8%
   - Avg Margin Error: 9.2

---

## 🔍 Monitoring & Maintenance

### Daily Operations
1. **Predictions generated:** Automatic when users visit ML Predictions page
2. **Results updated:** Run after each data refresh (Sunday nights + Monday mornings)
3. **Performance tracking:** Real-time display on Admin page

### Manual Update Schedule
```bash
# After games complete (Sunday nights, Monday mornings, Thursday nights)
python ingest_historical_games.py  # Load latest results
curl -X POST http://localhost:5000/api/ml/update-results  # Update tracking

# Check performance
curl http://localhost:5000/api/ml/performance-stats?season=2025
```

### Data Integrity Checks
```sql
-- Verify all predictions have results for completed games
SELECT COUNT(*) 
FROM hcl.ml_predictions mp
JOIN hcl.games g ON mp.game_id = g.game_id
WHERE g.home_score IS NOT NULL  -- Game complete
  AND mp.result_recorded_at IS NULL;  -- Not yet updated
-- Should be 0 if tracking is current

-- Check overall accuracy
SELECT 
    ROUND(AVG(CASE WHEN win_prediction_correct THEN 100.0 ELSE 0.0 END), 2) as accuracy
FROM hcl.ml_predictions
WHERE season = 2025 AND result_recorded_at IS NOT NULL;
```

---

## 📈 Performance Benchmarks

### Expected Accuracy (Based on Test Set)
- **Win/Loss Model:** 65-67% accuracy
- **Point Spread MAE:** 9-11 points
- **Score Predictions:** ±7-9 points per team

### Interpretation
- **60%+ accuracy:** Beating coin flip, solid performance
- **65%+ accuracy:** Matching Vegas spread performance
- **70%+ accuracy:** Exceptional (likely small sample)
- **<60% accuracy:** Investigation needed

### Red Flags
- Accuracy drops below 55% for 3+ consecutive weeks
- MAE increases above 13 points
- Consistent bias toward home/away teams
- Model performs worse than Vegas spread >3 weeks

---

## 🚀 Future Enhancements

### Phase 1 (Current Sprint)
- ✅ Database table created
- ✅ Auto-save predictions when generated
- ✅ Update results endpoint
- ✅ Admin page performance display
- ⏳ Checkmarks on prediction cards

### Phase 2 (Next Sprint)
- ⏳ Weekly email report with performance summary
- ⏳ Model vs Vegas head-to-head comparison
- ⏳ Confidence calibration analysis
- ⏳ Best/worst predictions visualization

### Phase 3 (Future)
- ⏳ Historical backfill for earlier 2025 games
- ⏳ Bet simulation (if followed AI, profit/loss?)
- ⏳ Feature importance tracking (which stats matter most?)
- ⏳ A/B testing for model improvements

---

## 📝 Notes

### Why Track Going Forward Only?
- **Historical data not useful:** Past predictions not saved, can't backfill accurately
- **2025+ focus:** Track real-world performance on unseen data
- **Future decision making:** Data informs model retraining and improvements

### Data Lifecycle
1. **Pre-game:** Prediction saved with `predicted_at` timestamp
2. **Post-game:** Results updated with `result_recorded_at` timestamp
3. **Analysis:** Performance calculated from predictions with results
4. **End of season:** Data archived, model retrained with full season

### Academic Context
This tracking system demonstrates:
- **Model validation:** Testing on unseen real-world data
- **Performance monitoring:** Continuous evaluation post-deployment
- **Data engineering:** Complete ETL pipeline for predictions
- **Production ML:** Real-world model deployment patterns

---

**Created:** January 2025  
**Status:** ✅ Fully Implemented  
**Sprint:** Sprint 12 - Prediction Tracking  
**Next Review:** After Week 12 games complete
