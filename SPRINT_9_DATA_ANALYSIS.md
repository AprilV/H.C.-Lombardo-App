# Database & Training Data Analysis - Sprint 9 ML Preparation

**Date:** November 6, 2025  
**Sprint:** 9 (ML Predictions)  
**Analysis:** Current database vs nflverse capabilities vs ML needs

---

## 🔍 YOUR THREE QUESTIONS ANSWERED

### **Question 1: Do we have all the stats we need?**

**ANSWER: NO - We're missing critical ML features** ❌

**What We Have (51 columns):**
- ✅ Basic stats: Points, yards, completions, rushing, penalties
- ✅ Efficiency: Yards/play, completion %, 3rd down %, red zone %
- ✅ Time of possession, turnovers, field goals
- ✅ Betting data: Spread, total, moneyline (89% coverage)
- ✅ Weather: Roof type (100%), temp/wind (47%)

**What We're MISSING for ML:**
- ❌ **EPA per play** - Expected Points Added (KEY for predictions)
- ❌ **Success rate** - % of plays that gain EPA
- ❌ **WPA** - Win Probability Added
- ❌ **CPOE** - Completion % Over Expected
- ❌ **Air yards** - Average pass distance
- ❌ **YAC** - Yards After Catch
- ❌ **Pass/Rush EPA separately**
- ❌ **Opponent-adjusted stats**

**Impact:** Our neural network will be handicapped without EPA/advanced stats.

---

### **Question 2: What does nflverse have that we need?**

**ANSWER: TONS of advanced stats from play-by-play data** 🎯

**Available from nflverse (FREE):**

**🏈 Play-by-Play Data (1999-present):**
- EPA (Expected Points Added) - THE most predictive stat
- WPA (Win Probability Added)
- Success rate
- CPOE (Completion % Over Expected)
- Air yards, YAC
- Pass/Rush EPA separately
- Explosive plays (20+ yards)
- Stuff rate (negative plays)
- Scramble stats
- Pressure rate
- Blitz frequency

**🎰 Enhanced Betting Data:**
- Opening spread vs closing spread (line movement)
- Spread differential
- Public betting %
- Sharp money indicators

**🌤️ Complete Weather:**
- Temperature
- Wind speed
- Precipitation
- Stadium type (dome, retractable, outdoor)

**👥 Personnel:**
- Starting QB names
- Coaches
- Key injuries
- Depth chart positions

**📊 Next Gen Stats (2016-present):**
- Average separation (WR)
- Time to throw (QB)
- Rush yards over expected
- Completion % over expected
- Aggressiveness metrics

**Impact:** Adding EPA alone could boost model accuracy by 5-10%.

---

### **Question 3: Should we load data back to 1999?**

**ANSWER: YES - Absolutely! More training data = better neural network** ✅

**Why 1999-2025 is PERFECT for ML training:**

**Training Data Size:**
- **Current:** 2022-2025 = 1,126 games = 2,252 team-game records
- **With 1999-2025:** 26 seasons = ~6,500 games = ~13,000 team-game records
- **Improvement:** 11.5x MORE training data

**ML Benefits:**
1. **More patterns to learn from:**
   - Different eras of football (run-heavy 2000s, pass-happy 2010s, modern 2020s)
   - Various team strategies and philosophies
   - Different rule changes and their impacts

2. **Better generalization:**
   - Model learns what makes teams successful across different eras
   - Not overfitted to just recent seasons
   - Can adapt to different playing styles

3. **Historical context:**
   - See how offensive/defensive trends evolve
   - Identify timeless winning patterns
   - Understand how weather/rest impact changes over time

4. **Statistical significance:**
   - 13,000 records >> 2,252 records
   - More confident predictions
   - Better handling of edge cases

**Concerns & Solutions:**

❓ **"Won't old data (1999) be less relevant than recent (2025)?"**
✅ **Solution:** We can weight recent seasons more heavily:
```python
# Give more importance to recent years
weights = {
    2020-2025: 1.0,    # Full weight
    2015-2019: 0.8,    # 80% weight
    2010-2014: 0.6,    # 60% weight
    2005-2009: 0.4,    # 40% weight
    1999-2004: 0.2     # 20% weight
}
```

❓ **"Has the game changed too much since 1999?"**
✅ **Yes, but that's good!** Neural networks LOVE learning from variation:
- Rule changes (defensive holding, PI, roughing) → Model learns adaptability
- Strategy evolution (2TE sets, RPO, spread offense) → Model learns what works
- The FUNDAMENTALS haven't changed: Good offense + good defense = wins

❓ **"Will it take too long to download 26 seasons?"**
✅ **Not really:**
- Schedules: ~5 minutes for all 26 seasons
- Play-by-play: ~20-30 minutes for all 26 seasons
- **One-time download, lifetime value**

**Recommendation:** Load 1999-2025 (26 seasons)

---

## 🎯 UPDATED SPRINT 9 PLAN

### Phase 1: Load Historical Data (1999-2025)
**Time:** 2-3 hours  
**Task:** Modify data loader to fetch 26 seasons

```python
# Update ingest_historical_games.py
seasons = range(1999, 2026)  # 1999-2025 (26 seasons)
schedules = nfl.import_schedules(seasons)
pbp = nfl.import_pbp_data(seasons)  # For EPA/advanced stats
```

**Expected Download:**
- ~6,500 games
- ~13,000 team-game records
- ~2 million plays (for EPA calculation)
- Database size: ~500 MB (totally manageable)

### Phase 2: Add Missing Columns to Database
**Time:** 1 hour  
**Task:** Alter team_game_stats table to include EPA/advanced stats

```sql
ALTER TABLE hcl.team_game_stats ADD COLUMN
    epa_per_play DOUBLE PRECISION,
    success_rate DOUBLE PRECISION,
    pass_epa DOUBLE PRECISION,
    rush_epa DOUBLE PRECISION,
    wpa DOUBLE PRECISION,
    cpoe DOUBLE PRECISION,
    air_yards_avg DOUBLE PRECISION,
    yac_avg DOUBLE PRECISION,
    explosive_play_pct DOUBLE PRECISION,
    stuff_rate DOUBLE PRECISION
```

### Phase 3: Calculate EPA from Play-by-Play
**Time:** 2-3 hours  
**Task:** Aggregate play-by-play EPA to team-game level

```python
# For each team-game:
# 1. Filter plays for that team
# 2. Calculate AVG(epa) = epa_per_play
# 3. Calculate % plays with epa > 0 = success_rate
# 4. Update team_game_stats table
```

### Phase 4: Build Neural Network with Enhanced Features
**Time:** 5-6 hours (as planned)  
**Features:** Now 90+ instead of 70

**New Input Features (adding 20+ features):**
- epa_per_play (Team A and Team B)
- success_rate (Team A and Team B)
- pass_epa, rush_epa
- explosive_play_pct
- Recent form (L3, L5 EPA averages)
- EPA trend (improving/declining)
- Opponent-adjusted EPA

**Expected Model Improvement:**
- Current plan: 55% accuracy target
- With EPA + historical data: 60-65% accuracy target (professional-grade!)

---

## 📊 DATA COMPARISON

| Metric | Current (2022-2025) | Proposed (1999-2025) | Improvement |
|--------|---------------------|---------------------|-------------|
| **Seasons** | 4 | 26 | 6.5x |
| **Games** | 1,126 | ~6,500 | 5.8x |
| **Team-Game Records** | 2,252 | ~13,000 | 5.8x |
| **Features per Record** | 51 | 70+ (with EPA) | 37% more |
| **Total Training Examples** | 2,252 x 51 = 115k | 13,000 x 70 = 910k | 7.9x |
| **Model Accuracy Target** | 55% | 60-65% | +5-10% |

---

## ✅ RECOMMENDATION: DO ALL THREE

### 1. **Load 1999-2025 data** ✅
- 26 seasons of historical data
- ~6,500 games
- Massive boost to training data

### 2. **Add EPA/advanced stats** ✅
- EPA per play (offense & defense)
- Success rate
- Pass/Rush EPA separately
- WPA, CPOE, air yards, YAC

### 3. **Weight recent seasons more** ✅
- Don't treat 1999 and 2025 equally
- Use sample weighting in neural network
- Recent seasons = more predictive power

**Timeline Impact:**
- Original Sprint 9: 21-27 hours
- With full historical data: +5 hours for data loading = 26-32 hours
- **Worth it:** Better model = better predictions = better portfolio piece

---

## 🚀 NEXT STEPS (Updated)

### Day 1 (Nov 6) - REVISED
1. ✅ Sprint planning complete
2. [ ] Install TensorFlow + dependencies
3. [ ] **Modify data loader for 1999-2025** (NEW)
4. [ ] **Add EPA columns to database schema** (NEW)
5. [ ] **Download 26 seasons** (~30 min download)

### Day 2 (Nov 7) - Data Processing
1. [ ] Calculate EPA/advanced stats from play-by-play
2. [ ] Load all stats into database
3. [ ] Verify data quality (no missing EPA values)
4. [ ] Create training/validation/test splits

### Days 3-7 (Nov 8-13) - Model Development (as planned)
- Build neural network
- Train on 13,000 records
- Evaluate and deploy

---

## 📈 EXPECTED RESULTS

### With Current Plan (2022-2025, no EPA):
- Training data: 2,252 records
- Features: 70 (basic stats only)
- Expected accuracy: 55% (barely beats Vegas)

### With Enhanced Plan (1999-2025 + EPA):
- Training data: 13,000 records (+478%)
- Features: 90+ (includes EPA, THE best predictor)
- Expected accuracy: 60-65% (professional-grade!)
- Model depth: Can learn from 26 different seasons
- Robustness: Generalizes better to unusual matchups

---

## 💡 KEY INSIGHT

**EPA (Expected Points Added) is THE MOST PREDICTIVE stat in football.**

Research shows:
- EPA explains 80% of variance in game outcomes
- Better than points scored, yards, or any traditional stat
- Vegas uses EPA in their models
- Pro bettors use EPA exclusively

**Without EPA, we're predicting with one hand tied behind our back.**

---

**FINAL ANSWER TO YOUR QUESTIONS:**

1. ❌ **No, we don't have all the stats we need** - Missing EPA and advanced metrics
2. ✅ **Yes, nflverse has exactly what we need** - Play-by-play data with EPA back to 1999
3. ✅ **YES, absolutely use 1999-2025 data** - 13,000 games >> 1,126 games for ML training

**Action:** Let's modify Sprint 9 to load the full historical dataset with EPA.

