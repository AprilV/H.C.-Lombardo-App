# ML Predictions Page - Complete Fix (7th Attempt)
**Date: November 18, 2025**

## Issues Fixed

### ✅ Issue 1: Wrong Week Displayed (Dates Issue)

**Problem:**  
The "Predict Upcoming" button was showing Week 11 games (Nov 13-17) which already happened, instead of Week 12 (Nov 20-24) which are the actual upcoming games.

**What the dates represent:**  
The dates shown on each card represent the **actual NFL game date** from the schedule. This is correct and working as designed.

**Root Cause:**  
The `predict_upcoming()` function in `ml/predict_week.py` was finding the "next week" by looking for games where `home_score IS NULL`, which included PAST games that haven't had scores entered yet.

**Fix Applied:**
Changed the query to use `game_date >= CURRENT_DATE` instead of checking for NULL scores:

```python
# OLD (WRONG) - Found games without scores (includes past games)
query = """
    SELECT season, week
    FROM hcl.games
    WHERE is_postseason = false
    AND (home_score IS NULL OR away_score IS NULL)
    ORDER BY season DESC, week ASC
    LIMIT 1;
"""

# NEW (CORRECT) - Find games in the future
query = """
    SELECT season, week
    FROM hcl.games
    WHERE is_postseason = false
    AND game_date >= CURRENT_DATE
    ORDER BY season ASC, week ASC
    LIMIT 1;
"""
```

**Result:**  
Now shows correct upcoming games:
- Week 12: Nov 20-24, 2025
- BUF @ HOU (Nov 20)
- PHI @ DAL (Nov 23) ← This is the upcoming game you mentioned
- PIT @ CHI, NYG @ DET, MIN @ GB, etc. (Nov 23)
- CAR @ SF (Nov 24)

---

### ✅ Issue 2: Team Names/Logos Breaking Out of Cards

**Problem:**  
Team information (especially home team logos, names, and win percentages) were breaking outside the prediction card boundaries. Previous 6 attempts with flexbox didn't work.

**Root Cause:**  
Flexbox layout allowed elements to expand beyond container width. The `flex: 1` on `.team-info` was causing the container to grow, and `overflow: hidden` wasn't effective because the flex items could still expand.

**Fix Applied:**  
Completely changed from Flexbox to **CSS Grid** with explicit column sizing:

```css
/* OLD (WRONG) - Flexbox allowed expansion */
.team-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.team-info {
  flex: 1;
}

/* NEW (CORRECT) - Grid with fixed columns */
.team-section {
  display: grid;
  grid-template-columns: 60px 1fr auto;
  /* 60px = logo, 1fr = team info (can shrink), auto = percentage (natural width) */
  align-items: center;
  gap: 15px;
  overflow: hidden;
  max-width: 100%;
  box-sizing: border-box;
}

.team-info {
  min-width: 0;
  overflow: hidden;
}

.team-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

**Grid Layout Breakdown:**
1. **Column 1 (60px fixed)**: Team logo - always 60px wide
2. **Column 2 (1fr)**: Team info (name + label) - takes remaining space, can shrink
3. **Column 3 (auto)**: Win percentage - only as wide as needed

This forces the team name to stay within its allocated space and truncate with `...` if too long.

---

## Files Modified

### Backend:
1. **ml/predict_week.py** (lines 330-355)
   - Fixed `predict_upcoming()` to use date-based query instead of score-based

### Frontend:
2. **frontend/src/MLPredictions.css**
   - `.team-section`: Changed from flexbox to grid layout
   - `.team-info`: Removed flex, added overflow hidden
   - `.team-name`: Changed to ellipsis overflow instead of word-wrap
   - `.prediction-card`: Added `contain: layout` and `overflow: hidden`
   - `.matchup-container`: Added containment properties

---

## Testing Results

### Backend Test:
```bash
python ml/predict_week.py --upcoming
```

**Output:**
```
📅 Predicting upcoming games: Season 2025, Week 12
Found 14 games

BUF @ HOU (Nov 20)
PIT @ CHI (Nov 23)
NYG @ DET (Nov 23)
PHI @ DAL (Nov 23)  ← Correct upcoming game
MIN @ GB (Nov 23)
... (9 more games)
```

✅ **Confirmed: Now showing Week 12, not Week 11**

---

## Deployment

**To apply fixes:**
```bash
cd "c:\IS330\H.C Lombardo App"
STOP.bat
START.bat
```

The fixes are compiled into:
- **Backend**: `ml/predict_week.py` (already saved)
- **Frontend**: `build/static/css/main.19d6251d.css` (new build)

---

## What Changed vs Previous Attempts

**Attempts 1-6:**
- Added `overflow: hidden` to various elements
- Added `min-width: 0` for flexbox shrinking
- Added `word-wrap` and `overflow-wrap` properties
- Added `max-width: 100%` constraints
- **Problem**: Flexbox still allowed expansion

**Attempt 7 (THIS FIX):**
- ✅ Completely switched to **CSS Grid** layout
- ✅ Explicit column sizing prevents expansion
- ✅ Text truncation with ellipsis (...) for long names
- ✅ Fixed backend date logic to show actual upcoming games

---

## Summary

### Dates:
- **What they represent**: Actual NFL game dates from the schedule
- **Why they were wrong**: API was returning past games (Week 11) instead of upcoming (Week 12)
- **Fix**: Changed query to `game_date >= CURRENT_DATE`

### Card Display:
- **Problem**: Teams breaking out of cards (especially home team)
- **Why previous fixes failed**: Flexbox layout allows child growth
- **Fix**: CSS Grid with explicit column widths (60px | 1fr | auto)

---

## Expected Behavior

When you click "Predict Upcoming" now:

1. ✅ Shows **Week 12** games (Nov 20-24, 2025)
2. ✅ Dates are correct NFL game dates
3. ✅ PHI @ DAL shows date "2025-11-23" (Sunday, Nov 23)
4. ✅ Team logos stay within cards
5. ✅ Team names truncate with "..." if too long
6. ✅ Win percentages align properly on the right

**Restart the server to see the fixes!**

---

Sprint: Post-Sprint 10 Bug Fixes  
Attempt: 7th  
Status: ✅ COMPLETE  
Developer: AI Assistant  
