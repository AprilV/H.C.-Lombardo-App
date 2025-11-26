# ML Predictions Results Tracking - Test Plan

## Feature Requirements
1. **Scorecard at top** showing AI vs Vegas performance for the selected week
2. **Result indicators** (✓/✗) on each prediction card
3. **Final scores** displayed prominently for finished games
4. **Works across all weeks and seasons**

## Data Fields Available (from API)
- `actual_home_score`, `actual_away_score` - Final scores (null if not finished)
- `actual_winner` - Team that won (null if not finished)
- `predicted_winner` - AI's prediction
- `correct` - Boolean if AI was correct
- `vegas_spread` - Vegas spread line
- `ai_spread` - AI's predicted spread

## Test Cases

### Test 1: Week with Finished Games (Week 12, 2025)
**Expected:**
- Scorecard shows "Week 12 Results"
- AI record shows correct count (e.g., "1/1 - 100%" for BUF@HOU game)
- Each finished game shows:
  - "FINAL" badge
  - Final score display
  - ✓ or ✗ on winner prediction
  - ✓ or ✗ on spread predictions

**Data Check:**
```
BUF @ HOU:
- actual_home_score: 23, actual_away_score: 19
- actual_winner: "HOU"
- predicted_winner: "HOU"
- correct: true
- Should show: ✓ for AI prediction
```

### Test 2: Week with All Scheduled Games
**Expected:**
- No scorecard shown (no finished games)
- No ✓/✗ indicators
- No final scores
- Predictions display normally

### Test 3: Mixed Week (Some finished, some not)
**Expected:**
- Scorecard shows only finished games count
- Finished games show results
- Scheduled games show predictions only

### Test 4: Spread Coverage Logic
**Vegas Spread Logic:**
- If vegas_spread = -5.5 (home favored by 5.5)
- Actual margin = home_score - away_score
- If actual margin > vegas_spread, home team "covered"
- Example: HOU -5.5, final 23-19 (margin = 4)
  - 4 > -5.5 is TRUE, so Vegas "covered"? NO - this logic is WRONG
  
**CORRECT Logic:**
- Home favored by 5.5 means home must win by MORE than 5.5
- Margin of 4 means home won by 4, which is LESS than 5.5
- Home did NOT cover
- Need to check: Math.abs(actual_margin) > Math.abs(vegas_spread) when signs match

**FIX:** Need to properly calculate spread coverage

### Test 5: Edge Cases
- Ties (if any)
- Missing data fields
- Games with null values

## Implementation Steps
1. Fix field names (`actual_home_score` not `home_score`)
2. Fix spread coverage calculation logic
3. Add CSS for all new elements
4. Test with real API data for Week 12
5. Test with different weeks
6. Verify calculations are correct

## Success Criteria
✅ Scorecard shows correct win/loss records
✅ Percentages calculate correctly
✅ Checkmarks appear on correct predictions
✅ X's appear on wrong predictions
✅ Final scores display for all finished games
✅ No errors in browser console
✅ Works for all weeks 1-18
✅ Works for multiple seasons
