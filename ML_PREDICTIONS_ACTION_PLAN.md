# ML Predictions - Critical Issues & Action Plan
**Date:** December 19, 2025

## Problems Identified

### 1. Model Confidence Severely Miscalibrated
**Symptoms:**
- 99.7% confidence predictions that lose (e.g., Cleveland Week 15)
- 70%+ of games show "Split Prediction" (AI disagrees with Vegas)
- Models predict with 90-99% confidence even when wrong

**Root Cause:**
- **Overfitting:** 46 features with only 1,506 training games (need ~10x more data)
- **Missing calibration:** XGBoost probabilities not calibrated (need Platt scaling or isotonic regression)
- **Vegas line dependence:** When spread_line=0 (missing), predictions are random with high confidence

**Impact:**
- Predictions are useless - worse than Vegas lines
- "Split Prediction" badge appears too frequently (should be <20%, currently 70%)
- User trust completely broken

### 2. UI/UX Issues
**Problems:**
- Win/loss model mixed with point spread model (confusing)
- Statistics not displayed properly
- Split Prediction logic too aggressive

**Needed Changes:**
- Separate sections for: Win Probability vs Point Spread Prediction
- Better stat placement and readability
- Fix Split Prediction to only show when |AI_spread - Vegas_spread| ≥ 7 points

### 3. Data Quality Issues
**Vegas Line Coverage:**
```
Weeks 1-14:  100% coverage (nflverse historical)
Week 15:     0% coverage
Week 16:     88% coverage (14/16 games)
Week 17-18:  0% coverage
```

**Problem:** Models trained on games WITH Vegas lines, but many games missing lines = garbage predictions

## Recommended Solutions

### Short-Term Fixes (This Week)

#### 1. Confidence Calibration
Add calibration layer to cap unrealistic confidence:
```python
# In predict_week.py
def calibrate_confidence(raw_prob):
    """Cap confidence to realistic levels"""
    if raw_prob > 0.75:
        return 0.55 + (raw_prob - 0.75) * 0.8  # Max 75% -> 65%
    return raw_prob
```

#### 2. Fix Split Prediction Logic
Change from "any disagreement" to "significant disagreement":
```python
def is_split_prediction(ai_spread, vegas_spread):
    """Only flag when difference is meaningful"""
    if vegas_spread is None:
        return False
    return abs(ai_spread - vegas_spread) >= 7.0  # 1+ touchdown difference
```

#### 3. Don't Show Predictions Without Vegas Lines
```python
if spread_line is None:
    return {"error": "No Vegas line available - cannot generate reliable prediction"}
```

#### 4. UI Redesign
**Proposed Layout:**
```
┌─────────────────────────────────────────────┐
│  GAME MATCHUP (Team Logos, Time, etc)      │
├─────────────────────────────────────────────┤
│  WIN PROBABILITY                            │
│  ├─ Home Team: 58%  █████████░░░            │
│  └─ Away Team: 42%  ███████░░░░░            │
├─────────────────────────────────────────────┤
│  POINT SPREAD ANALYSIS                      │
│  ├─ Vegas Line: KC -3.5                     │
│  ├─ AI Prediction: KC -5.2                  │
│  └─ Spread Difference: 1.7 pts              │
│  └─ [Split Prediction Badge] if ≥7 pts      │
├─────────────────────────────────────────────┤
│  PREDICTED SCORES                           │
│  Home: 24.5  |  Away: 19.3                  │
└─────────────────────────────────────────────┘
```

### Medium-Term Fixes (Next 1-2 Weeks)

#### 1. Retrain with Calibration
```python
from sklearn.calibration import CalibratedClassifierCV

# Wrap XGBoost with calibration
calibrated_model = CalibratedClassifierCV(
    xgb_model, 
    method='isotonic',  # Better for XGBoost
    cv=5
)
```

#### 2. Reduce Features to 12-15 Key Stats
**Keep Only:**
- Vegas spread_line (MUST HAVE)
- EPA per play (offense/defense) - 4 features
- Success rate (offense/defense) - 4 features  
- Recent form (last 3 games) - 4 features
- Turnover differential - 2 features

Drop 30+ other features causing overfitting.

#### 3. Implement Elo Rating System (Backup)
FiveThirtyEight's proven approach:
- K-factor: 20
- Home Field Advantage: 65 points
- MOV multiplier for blowouts
- 60-65% accuracy vs Vegas

### Long-Term Strategy (2-4 Weeks)

#### 1. Ensemble Model
Combine three approaches:
- XGBoost (calibrated, 12 features)
- Elo rating system
- Vegas line (weighted 40%)

Final prediction = 30% XGBoost + 30% Elo + 40% Vegas

#### 2. Weekly Validation
Track accuracy vs Vegas:
- Overall win %
- Against the spread %
- Split Prediction success rate
- Confidence calibration curve

#### 3. Adaptive Weighting
Adjust ensemble weights based on recent performance:
```python
if xgb_recent_accuracy < 0.50:
    increase_vegas_weight()
if elo_recent_accuracy > 0.60:
    increase_elo_weight()
```

## Immediate Action Items

**Priority 1 (Do Now):**
1. ✅ Scrape Vegas lines for weeks 15, 17, 18
2. ❌ Add confidence calibration to predict_week.py
3. ❌ Fix Split Prediction threshold (7+ points)
4. ❌ Regenerate all 2025 predictions
5. ❌ Deploy to EC2

**Priority 2 (Next Session):**
1. ❌ Redesign MLPredictions.js UI (separate sections)
2. ❌ Add "No Vegas line" handling
3. ❌ Update statistics display

**Priority 3 (This Week):**
1. ❌ Retrain models with calibration
2. ❌ Reduce to 12-15 features
3. ❌ Implement Elo system as backup

## Success Criteria

**Model Performance:**
- Win prediction: 55-60% accuracy (realistic)
- Against spread: 52-55% accuracy (beat random)
- Confidence: Max 70% displayed, calibrated to actual accuracy
- Split Predictions: <20% of games, >60% success rate

**User Experience:**
- Clear separation: Win Probability vs Spread Analysis
- Realistic confidence levels (no 99%)
- Meaningful split predictions only
- Comprehensive but readable stats

## Current Status
- ✅ Models trained (XGBoost 46 features)
- ✅ Vegas line scraper working
- ✅ EC2 server operational
- ❌ Predictions severely miscalibrated
- ❌ UI needs redesign
- ❌ Split Prediction logic broken

**Bottom Line:** The math is fundamentally flawed. The models are overconfident because they're overfitting. Need to either fix calibration immediately or switch to simpler, proven Elo system.
