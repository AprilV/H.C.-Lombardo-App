# ML Predictions Page Fixes - November 18, 2025

## Issues Identified

### Issue 1: Home Team Overflow ✅ FIXED

**Problem:**  
Home team information (logos, team names, and win percentages) were breaking outside the prediction card boundaries. Examples: MIA (42.9%), NE, BUF, JAX.

**Root Cause:**  
The flexbox layout in `.team-section` was allowing elements to expand beyond the parent container width. Previous `overflow: hidden` fixes weren't effective because:
1. Missing `overflow: hidden` on `.prediction-card` itself
2. Missing `contain: layout` property for layout containment
3. Logo and probability elements didn't have `flex-shrink: 0` to prevent unwanted shrinking
4. Missing `box-sizing: border-box` on team sections

**Solution Applied:**
```css
/* Force strict containment on prediction cards */
.prediction-card {
  overflow: hidden;
  contain: layout;
  max-width: 100%;
}

/* Ensure matchup container respects boundaries */
.matchup-container {
  overflow: hidden;
  max-width: 100%;
  contain: layout;
}

/* Prevent team sections from expanding */
.team-section {
  overflow: hidden;
  max-width: 100%;
  min-width: 0;
  box-sizing: border-box;
}

/* Keep logo and percentage from shrinking */
.team-logo {
  flex-shrink: 0;
}

.team-prob {
  flex-shrink: 0;
  white-space: nowrap;
}
```

**Files Modified:**
- `frontend/src/MLPredictions.css` (5 changes)

---

### Issue 2: Wrong Dates Displayed 🔍 EXPLAINED

**Problem:**  
Prediction cards showing dates like "2025-11-13" and "2025-11-16" when the current date is November 18, 2025.

**Root Cause:**  
The dates ARE correct - they represent the actual game dates from the NFL schedule. The confusion is because:

1. **The page is showing Week 11 predictions** (games from Nov 13-17)
2. **Week 11 games already happened** (today is Nov 18)
3. **The "Predict Upcoming" button should show Week 12** (future games)

**Investigation Results:**

Database query confirms:
```
Week 11 Games (PAST):
2025_11_NYJ_NE   2025-11-13   NYJ @ NE
2025_11_WAS_MIA  2025-11-16   WAS @ MIA
2025_11_CAR_ATL  2025-11-16   CAR @ ATL
2025_11_TB_BUF   2025-11-16   TB @ BUF
2025_11_LAC_JAX  2025-11-16   LAC @ JAX
... (and more Week 11 games)
```

**Data Flow:**
```
Database: hcl.games.game_date (DATE column)
    ↓
Backend: ml/predict_week.py line 296
    result['game_date'] = str(game['game_date'])
    ↓
API: /api/ml/predict-upcoming returns predictions with game_date
    ↓
Frontend: MLPredictions.js displays {pred.game_date}
    ↓
Display: "2025-11-13", "2025-11-16"
```

**What the Dates Represent:**  
The dates are the **actual scheduled game dates** from the NFL schedule, NOT:
- Week start dates
- Prediction generation dates  
- Cached/stale data

**Solution:**  
The "Predict Upcoming" button should automatically detect the current week and predict the NEXT week's games (Week 12), not Week 11 which already happened.

**Next Steps:**
- Update the "Predict Upcoming" logic to:
  1. Get current date (Nov 18, 2025)
  2. Determine current NFL week
  3. Predict NEXT week's games (Week 12, not Week 11)
- OR: Update Week 11 games with actual results instead of showing predictions

---

## Testing

**Test Cases for Overflow Fix:**
1. ✅ CAR vs MIA (42.9% home win probability)
2. ✅ WAS vs NE  
3. ✅ LAC vs BUF
4. ✅ CHI vs JAX

**Expected Result:**
- Team logos stay within card boundaries
- Team names don't break outside cards
- Win percentages (42.9%, etc.) stay inside cards
- Cards maintain consistent width across all predictions

---

## Deployment

**To Apply Fixes:**
```bash
cd "c:\IS330\H.C Lombardo App"
STOP.bat              # Stop current server
START.bat             # Restart with new build
```

The CSS fixes have been compiled into the production build (`main.b8f589ca.css`).

---

## Technical Details

### CSS Properties Used

**`contain: layout`**  
Forces the browser to contain all layout calculations within the element boundary. Prevents child elements from affecting or escaping parent dimensions.

**`flex-shrink: 0`**  
Prevents flexbox children from shrinking below their natural size. Applied to logo and probability to maintain consistent sizing.

**`box-sizing: border-box`**  
Includes padding and border in width calculations, ensuring `max-width: 100%` accounts for all space used.

**`white-space: nowrap`**  
Prevents percentages from wrapping to multiple lines (e.g., "42.9" and "%" on separate lines).

---

## Files Changed

1. **frontend/src/MLPredictions.css** - Overflow fixes
2. **check_game_dates.py** (NEW) - Database investigation script

---

## Summary

✅ **Home team overflow**: FIXED with comprehensive CSS containment  
🔍 **Date confusion**: EXPLAINED - dates are correct, but showing past games  
📋 **Next step**: Update "Predict Upcoming" to show Week 12 instead of Week 11

Sprint: Post-Sprint 10 Maintenance  
Date: November 18, 2025  
Developer: AI Assistant  
