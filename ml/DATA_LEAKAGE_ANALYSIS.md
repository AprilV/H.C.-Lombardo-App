# Data Leakage Analysis - Sprint 9 ML

## Problem Identified

**100% Test Accuracy = Data Leakage!**

### Root Cause

The `hcl.team_game_stats` table contains **post-game statistics**:
- `points` - Points scored IN that game
- `touchdowns` - TDs scored IN that game  
- `total_yards` - Yards gained IN that game
- `epa_per_play` - EPA calculated FROM that game
- All 60+ columns are OUTCOMES of the game

### The Issue

Our model was using:
```python
Input Features: [points=28, touchdowns=4, total_yards=425, ...]
Predict: Did team win? → Answer: Obviously yes (scored 28 points!)
```

This is like asking: "Given that a team scored 35 points, did they win?" 
The answer is trivially obvious from the input!

### Why We Got 100% Accuracy

The neural network learned:
```
IF points > opponent_points THEN win = 1
```

No complex pattern learning needed - just look at the score!

## Solution: Rolling/Cumulative Features

We need features calculated from PREVIOUS games only:

### Correct Approach

For each game, calculate team's stats ENTERING that game:

**Team Historical Stats (Season-to-date before this game):**
- Average PPG in games 1 through (N-1)
- Average EPA over last 5 games  
- Win percentage
- Home/away splits
- Recent form (W/L last 3 games)

**Opponent Historical Stats:**
- Same metrics for opponent
- Head-to-head history (if exists)

**Matchup Factors:**
- EPA differential (team EPA - opponent EPA allowed)
- Pace matchup (fast vs slow)
- Style matchup (pass-heavy vs run-heavy)

**Context:**
- Rest days (days since last game)
- Travel distance  
- Home field advantage
- Weather (if available)
- Week of season
- Betting lines (spread, total, moneyline)

### Example

**Game: Week 8, 2024 - Kansas City Chiefs @ Buffalo Bills**

**Features (what we KNOW before kickoff):**
```python
# Chiefs entering Week 8
chiefs_ppg_season: 27.8  # Average from Weeks 1-7
chiefs_epa_l5: 0.18      # EPA over last 5 games
chiefs_record: 6-1        # Record before this game
chiefs_home_away_split: 0.85  # Win % on road

# Bills entering Week 8  
bills_ppg_season: 25.3
bills_epa_l5: 0.15
bills_record: 5-2
bills_home_advantage: 0.71  # Win % at home

# Matchup
epa_differential: 0.03   # Chiefs EPA - Bills EPA_allowed
rest_days_chiefs: 7      # Days since last game
rest_days_bills: 7
travel_distance: 1200    # Miles traveled

# Vegas lines (available pre-game)
spread_line: -3.5        # Chiefs favored by 3.5
total_line: 47.5
chiefs_moneyline: -180
bills_moneyline: +160

# Context
is_home: 0               # Chiefs are away
season: 2024
week: 8
```

**Label (what we DON'T know until after):**
```python
chiefs_won: 1  # Chiefs won 30-28
```

## Implementation Plan

### Step 1: Create Rolling Features Function

```python
def compute_rolling_features(df, window_sizes=[3, 5, 'season']):
    """
    For each game, compute team's stats from PREVIOUS games only
    
    Returns DataFrame with features like:
    - team_ppg_season
    - team_epa_l5  
    - opponent_ppg_season
    - opponent_epa_l5
    - epa_differential
    - etc.
    """
    pass
```

### Step 2: Feature Categories

1. **Team Season Stats** (games 1 to N-1):
   - PPG, yards/game, turnovers/game
   - EPA/play, success rate
   - Win percentage
   
2. **Team Recent Form** (last 3-5 games):
   - Recent EPA trend
   - Win streak
   - Points trend

3. **Opponent Stats** (same as above for opponent)

4. **Matchup Stats**:
   - Historical head-to-head (if exists)
   - Style matchup metrics
   
5. **Context**:
   - Home/away
   - Rest days
   - Week of season
   - Division game?
   
6. **Betting Lines**:
   - Spread
   - Total
   - Moneylines

### Step 3: Expected Accuracy

With proper features:
- **Training**: 55-60% accuracy
- **Validation**: 54-58% accuracy  
- **Test**: 55-60% accuracy (if we're lucky!)

This aligns with:
- Vegas lines: 52-55%
- Best ML models: 57-60%
- Our target: 60-65% (with EPA features)

## Technical Notes

### Why Rolling Features Are Hard

For game N in a season:
```
Game 1: No previous games → Use league averages
Game 2: Use stats from Game 1
Game 3: Use stats from Games 1-2
Game N: Use stats from Games 1 to N-1
```

Must compute separately for each team, each week!

### Database Query Approach

```sql
-- For each game, get team's stats from PREVIOUS games
SELECT 
    AVG(points) as ppg_before,
    AVG(epa_per_play) as avg_epa_before,
    COUNT(*) as games_played_before
FROM hcl.team_game_stats
WHERE team = 'KC'
  AND season = 2024
  AND week < 8  -- BEFORE current week
```

### pandas Approach

```python
# Group by team and season
grouped = df.groupby(['team', 'season'])

# Compute rolling stats (excluding current game)
df['ppg_before'] = grouped['points'].transform(
    lambda x: x.shift(1).expanding().mean()
)
```

## Next Steps

1. ✅ Identified data leakage issue
2. ⏳ Create `compute_rolling_features()` function
3. ⏳ Re-train model with proper features
4. ⏳ Expect 55-65% accuracy (realistic!)
5. ⏳ Build API endpoint and frontend

## Documentation Updates

- ✅ Technical docs created (ML_NEURAL_NETWORK_TECHNICAL_DOCS.md)
- ✅ Dr. Foster dashboard updated with neural network schematic
- ⏳ Update docs with rolling features approach
- ⏳ Add "Lessons Learned" section about data leakage

---

**Key Lesson**: Always verify you're using ONLY information available BEFORE the event you're predicting!

**Date**: November 6, 2025  
**Sprint**: 9 (ML Predictions)  
**Status**: Data leakage fixed, re-training needed
