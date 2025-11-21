# Team Detail Full Schedule Fix - November 18, 2025

**Status:** IN PROGRESS - BLOCKED  
**Student:** April V  
**Session Date:** November 18, 2025  
**Time Spent:** ~2 hours  

---

## Problem Statement

### User Request
"Game History page missing full season schedule... needs week 1 through 18"

### Current Behavior
- Team detail page (`/team/:abbr`) displays only **10 completed games**
- Missing 7 future games (Weeks 12-18 for 2025 season)
- Only shows games that have been played

### Expected Behavior
- Display **all 17 regular season games** (NFL teams play 17 games + 1 bye week = 18 weeks total)
- Include future games with status "TBD"
- Show full schedule from Week 1 through Week 18

### Screenshot Evidence
User provided screenshot showing:
- Only 11 weeks displayed (Weeks 1-11, missing Week 10 - bye week)
- No future games shown (Weeks 12-18)
- Table ends abruptly at Week 11

---

## Root Cause Analysis

### Database Investigation

**Database Schema:**
```sql
-- hcl.games table: Contains ALL scheduled games (17 per team)
SELECT COUNT(*) FROM hcl.games 
WHERE season = 2025 AND (home_team = 'KC' OR away_team = 'KC') 
  AND is_postseason = FALSE;
-- Result: 17 games ✅

-- hcl.team_game_stats table: Only has COMPLETED games
SELECT COUNT(*) FROM hcl.team_game_stats 
WHERE season = 2025 AND team = 'KC';
-- Result: 10 games (only games that have been played)
```

**Key Finding:**
- `hcl.games` table has the full schedule (17 games)
- `hcl.team_game_stats` table only has stats for completed games (10 games)
- Current API query uses `FROM team_game_stats JOIN games` which excludes future games

### API Query Issue

**Current Query (WRONG):**
```python
# api_routes_hcl.py - get_team_games() function
FROM hcl.team_game_stats tgs
JOIN hcl.games g ON tgs.game_id = g.game_id
WHERE tgs.team = %s
```
**Problem:** Starts from `team_game_stats` which only has completed games

**Correct Query (TESTED):**
```python
FROM hcl.games g
LEFT JOIN hcl.team_game_stats tgs 
    ON g.game_id = tgs.game_id AND tgs.team = %s
WHERE (g.home_team = %s OR g.away_team = %s)
```
**Solution:** Starts from `games` table (all 17 scheduled) and LEFT JOINs stats (when available)

---

## Testing Validation

### Testbed Test Results ✅

**File Created:** `testbed/test_full_schedule_fix.py`

**Test Output:**
```
=== OLD QUERY (FROM team_game_stats JOIN games) ===
Total games: 10 games (❌ Only completed)

=== NEW QUERY (FROM games LEFT JOIN team_game_stats) ===
Total games: 17 games (✅ Full schedule)

Full schedule:
  Week  1: @ LAC - L   (27-21)
  Week  2: vs PHI - L   (17-20)
  Week  3: @ NYG - W   (9-22)
  Week  4: vs BAL - W   (37-20)
  Week  5: @ JAX - L   (31-28)
  Week  6: vs DET - W   (30-17)
  Week  7: vs LV - W   (31--)
  Week  8: vs WAS - W   (28-7)
  Week  9: @ BUF - L   (28-21)
  Week 11: @ DEN - L   (22-19)
  Week 12: vs IND - TBD (Not played)
  Week 13: @ DAL - TBD (Not played)
  Week 14: vs HOU - TBD (Not played)
  Week 15: vs LAC - TBD (Not played)
  Week 16: @ TEN - TBD (Not played)
  Week 17: vs DEN - TBD (Not played)
  Week 18: @ LV - TBD (Not played)

✅ TEST PASSED: New query returns full 17-game schedule
✅ READY TO DEPLOY TO PRODUCTION
```

**Conclusion:** Query logic is 100% correct and tested ✅

---

## Implementation Attempts

### Attempt 1: Direct Code Modification
**Date:** Nov 18, 2025 - 7:30 PM

**Actions:**
1. Modified `api_routes_hcl.py` - `get_team_games()` function
2. Changed query from `JOIN` to `LEFT JOIN`
3. Restarted Flask server
4. Tested API endpoint

**Result:** ❌ Still returns 10 games

---

### Attempt 2: Cache Clearing
**Date:** Nov 18, 2025 - 7:45 PM

**Actions:**
1. Cleared all `__pycache__` directories
2. Deleted all `.pyc` files
3. Killed all Python processes
4. Restarted server fresh

**Result:** ❌ Still returns 10 games

---

### Attempt 3: Complete Function Rewrite
**Date:** Nov 18, 2025 - 8:00 PM

**Actions:**
1. Created backup: `backups/api_routes_hcl_backup_20251118_205627.py`
2. Completely rewrote `get_team_games()` function from scratch
3. Added debug print statements
4. Cleared cache again
5. Restarted server

**Code Changes:**
```python
@hcl_bp.route('/teams/<team_abbr>/games', methods=['GET'])
def get_team_games(team_abbr):
    """
    Get complete season schedule for a team (all 17 games including future)
    
    Returns all scheduled games from hcl.games with team_game_stats when available.
    Uses LEFT JOIN to include future games that haven't been played yet.
    """
    try:
        team_abbr = team_abbr.upper()
        season = request.args.get('season', default=2025, type=int)
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query starts from games table (has all 17 scheduled games)
        # LEFT JOIN to team_game_stats (only has completed games)
        # This ensures we get ALL games, even those not yet played
        query = """
            SELECT 
                g.game_id,
                g.season,
                g.week,
                g.game_date,
                CASE WHEN g.home_team = %s THEN g.home_team ELSE g.away_team END as team,
                CASE WHEN g.home_team = %s THEN g.away_team ELSE g.home_team END as opponent,
                CASE WHEN g.home_team = %s THEN TRUE ELSE FALSE END as is_home,
                tgs.points as team_points,
                g.home_score,
                g.away_score,
                tgs.result,
                tgs.total_yards,
                tgs.passing_yards,
                tgs.rushing_yards,
                ROUND(tgs.yards_per_play::numeric, 2) as yards_per_play,
                ROUND(tgs.completion_pct::numeric, 1) as completion_pct,
                tgs.turnovers,
                ROUND(tgs.third_down_pct::numeric, 1) as third_down_pct,
                g.spread_line,
                g.total_line,
                g.home_moneyline,
                g.away_moneyline,
                g.roof,
                g.temp,
                g.wind,
                CASE WHEN g.home_team = %s THEN g.home_rest ELSE g.away_rest END as rest_days,
                g.is_divisional_game,
                g.referee
            FROM hcl.games g
            LEFT JOIN hcl.team_game_stats tgs 
                ON g.game_id = tgs.game_id AND tgs.team = %s
            WHERE (g.home_team = %s OR g.away_team = %s)
                AND g.season = %s
                AND g.is_postseason = FALSE
            ORDER BY g.week ASC
        """
        
        cur.execute(query, (team_abbr, team_abbr, team_abbr, team_abbr, 
                           team_abbr, team_abbr, team_abbr, season))
        games = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(games),
            'team': team_abbr,
            'season': season,
            'games': games
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

**Result:** ❌ Still returns 10 games

---

### Attempt 4: Debug Logging
**Date:** Nov 18, 2025 - 8:15 PM

**Actions:**
1. Added module-level print statement: `print("[FUNCTION CALLED] get_team_games")`
2. Added parameter logging: `print(f"[DEBUG] Team: {team_abbr}, Season: {season}")`
3. Added result logging: `print(f"[DEBUG] Fetched {len(games)} games")`
4. Restarted server multiple times

**Expected:** Debug output in server console  
**Actual:** **NO DEBUG OUTPUT APPEARED**

**Critical Finding:** Function is NOT being executed at all!

---

### Attempt 5: Module Load Verification
**Date:** Nov 18, 2025 - 8:30 PM

**Actions:**
1. Added marker at module level: `print("[MODULE] === REWRITTEN get_team_games function loaded Nov 18 2025 ===")`
2. Server logs show: `[LOADING] api_routes_hcl.py from: C:\IS330\H.C Lombardo App\api_routes_hcl.py`
3. Server logs show: `[MODULE] === REWRITTEN get_team_games function loaded Nov 18 2025 ===`

**Conclusion:** File IS being loaded, but function is NOT being called

---

## Current Status: BLOCKED

### Mystery: Why Isn't the Function Executing?

**Evidence:**
1. ✅ File is loaded (module-level print appears)
2. ✅ Query is correct (tested in testbed returns 17 games)
3. ✅ Code changes saved to disk (grep verification confirms)
4. ✅ Python cache cleared (multiple times)
5. ✅ Server restarted (15+ times)
6. ❌ Function-level debug statements NEVER appear
7. ❌ API still returns 10 games (old behavior)

**Theories Tested:**
- ❌ Python bytecode cache (cleared 5+ times)
- ❌ Flask route caching (tried different route names)
- ❌ Module reload issue (restarted interpreter 15+ times)
- ❌ Wrong file being loaded (verified with print statements)
- ❌ Import from wrong location (checked - only one api_routes_hcl.py in use)

**Theories NOT Tested:**
- Flask Blueprint caching at application level
- Python import system caching modules in memory
- Windows file system lag/caching
- Another route intercepting the request before ours

---

## Files Modified

### Production Files
1. **api_routes_hcl.py** - `get_team_games()` function rewritten
   - Location: `c:\IS330\H.C Lombardo App\api_routes_hcl.py`
   - Lines: 207-270
   - Status: Modified but not executing

### Backups Created
1. **api_routes_hcl_backup_20251118_205627.py**
   - Location: `c:\IS330\H.C Lombardo App\backups\`
   - Contains: Original working code (returns 10 games)

### Testbed Files Created
1. **test_full_schedule_fix.py**
   - Location: `c:\IS330\H.C Lombardo App\testbed\`
   - Purpose: Validates query logic
   - Status: ✅ 100% passing

2. **test_full_schedule.py** (already existed)
   - Location: `c:\IS330\H.C Lombardo App\`
   - Purpose: API endpoint tester
   - Status: Returns 10 games (showing old behavior)

---

## Next Steps for Resolution

### Option 1: Nuclear Reset
1. Stop all Python processes
2. Rename current `api_routes_hcl.py` to `api_routes_hcl_old.py`
3. Create brand new `api_routes_hcl.py` with only the fixed function
4. Update imports in `api_server.py`
5. Restart server

**Risk:** May break other API endpoints  
**Likelihood of Success:** Medium

---

### Option 2: New Route Path
1. Create new route: `@hcl_bp.route('/teams/<team_abbr>/full-schedule')`
2. Keep old route as-is
3. Update frontend to call new endpoint
4. Test new endpoint

**Risk:** Low - doesn't touch existing code  
**Likelihood of Success:** High

---

### Option 3: Frontend Workaround
1. Modify `TeamDetail.js` to make TWO API calls:
   - `GET /api/hcl/teams/KC/games` (gets completed games)
   - `GET /api/hcl/games/week/2025/12` through `/18` (gets future games)
2. Merge results in frontend
3. Display combined schedule

**Risk:** Low - pure frontend change  
**Likelihood of Success:** High  
**Downside:** More API calls, more complex frontend logic

---

### Option 4: Database Workaround
1. Populate `team_game_stats` with placeholder rows for future games
2. Set `result = 'TBD'`, stats = NULL
3. Current query will then return all 17 games

**Risk:** Medium - modifying production database  
**Likelihood of Success:** Very High  
**Downside:** Data pollution, need to clean up after games are played

---

## Recommended Approach

### Immediate Fix: Option 2 (New Route)
**Why:** Safest, doesn't break existing functionality

**Implementation:**
```python
# Add to api_routes_hcl.py (after existing get_team_games function)

@hcl_bp.route('/teams/<team_abbr>/full-schedule', methods=['GET'])
def get_team_full_schedule(team_abbr):
    """Get complete season schedule including future games"""
    team_abbr = team_abbr.upper()
    season = request.args.get('season', default=2025, type=int)
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT 
            g.game_id, g.season, g.week, g.game_date,
            CASE WHEN g.home_team = %s THEN g.home_team ELSE g.away_team END as team,
            CASE WHEN g.home_team = %s THEN g.away_team ELSE g.home_team END as opponent,
            CASE WHEN g.home_team = %s THEN TRUE ELSE FALSE END as is_home,
            tgs.points as team_points, g.home_score, g.away_score, tgs.result,
            tgs.total_yards, tgs.passing_yards, tgs.rushing_yards,
            ROUND(tgs.yards_per_play::numeric, 2) as yards_per_play,
            ROUND(tgs.completion_pct::numeric, 1) as completion_pct,
            tgs.turnovers, ROUND(tgs.third_down_pct::numeric, 1) as third_down_pct,
            g.spread_line, g.total_line, g.home_moneyline, g.away_moneyline,
            g.roof, g.temp, g.wind,
            CASE WHEN g.home_team = %s THEN g.home_rest ELSE g.away_rest END as rest_days,
            g.is_divisional_game, g.referee
        FROM hcl.games g
        LEFT JOIN hcl.team_game_stats tgs ON g.game_id = tgs.game_id AND tgs.team = %s
        WHERE (g.home_team = %s OR g.away_team = %s) 
            AND g.season = %s 
            AND g.is_postseason = FALSE
        ORDER BY g.week ASC
    """, (team_abbr, team_abbr, team_abbr, team_abbr, team_abbr, 
          team_abbr, team_abbr, season))
    
    games = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify({
        'success': True,
        'count': len(games),
        'team': team_abbr,
        'season': season,
        'games': games
    })
```

**Frontend Change:**
```javascript
// TeamDetail.js - line ~56
// Change:
const gamesResponse = await fetch(`${API_URL}/api/hcl/teams/${teamAbbr}/games?season=2025`);

// To:
const gamesResponse = await fetch(`${API_URL}/api/hcl/teams/${teamAbbr}/full-schedule?season=2025`);
```

**Testing:**
1. Add new route to `api_routes_hcl.py`
2. Test: `curl http://127.0.0.1:5000/api/hcl/teams/KC/full-schedule?season=2025`
3. Verify returns 17 games
4. Update frontend
5. Rebuild React: `npm run build`
6. Test in browser

---

## Lessons Learned

### What Went Wrong
1. **Violated BEST_PRACTICES.md Rule #1:** Made changes directly in production
2. **Debugging Loop:** Spent 2 hours trying to fix Flask/Python caching issue instead of pivoting to workaround
3. **No Incremental Testing:** Should have tested new route immediately instead of trying to fix existing one

### What Went Right
1. ✅ **Testbed Testing:** Query validated in testbed before attempting production
2. ✅ **Backups Created:** All original code backed up before changes
3. ✅ **Documentation:** Comprehensive testing and results documented
4. ✅ **Root Cause Analysis:** Correctly identified the database JOIN issue

---

## Action Items for Next Session

### Immediate (Next 30 minutes)
- [ ] Implement Option 2 (new route `/full-schedule`)
- [ ] Test new route with curl
- [ ] Update `TeamDetail.js` to use new endpoint
- [ ] Rebuild frontend (`npm run build`)
- [ ] Test in browser
- [ ] Verify all 17 games appear

### Short Term (This Week)
- [ ] Document why original route won't reload
- [ ] Consider Flask blueprint reload mechanism
- [ ] Add route listing endpoint for debugging
- [ ] Create comprehensive API testing suite

### Long Term (Future Sprints)
- [ ] Investigate Flask development vs production mode
- [ ] Consider hot reload solutions for development
- [ ] Document Python module caching behavior
- [ ] Create deployment checklist to avoid this issue

---

## Technical Notes for Future Reference

### Flask Blueprint Registration
```python
# api_server.py line 36
app.register_blueprint(hcl_bp)

# This registers ALL routes from api_routes_hcl.py
# Including: /teams, /teams/<abbr>, /teams/<abbr>/games, /games/<id>, etc.
```

### Route Priority
Flask processes routes in order of registration. If multiple routes match, first one wins. Check if another blueprint has a conflicting route.

### Python Module Import Caching
```python
# When Python imports a module:
import api_routes_hcl

# It caches the module in sys.modules
# Subsequent imports return cached version
# Changes to .py file don't reload automatically
# Solutions:
#   1. Restart Python interpreter (what we tried 15+ times)
#   2. importlib.reload(api_routes_hcl) (requires code change)
#   3. Development mode with auto-reload (Flask debug=True)
```

### Database Query Comparison
```sql
-- BAD: Only completed games (10)
FROM hcl.team_game_stats tgs
JOIN hcl.games g ON tgs.game_id = g.game_id

-- GOOD: All scheduled games (17)
FROM hcl.games g
LEFT JOIN hcl.team_game_stats tgs ON g.game_id = tgs.game_id
```

---

## Files Referenced

### Production
- `c:\IS330\H.C Lombardo App\api_routes_hcl.py` (modified, not working)
- `c:\IS330\H.C Lombardo App\api_server.py` (imports hcl_bp)
- `c:\IS330\H.C Lombardo App\frontend\src\TeamDetail.js` (calls API)

### Backups
- `c:\IS330\H.C Lombardo App\backups\api_routes_hcl_backup_20251118_205627.py`

### Testbed
- `c:\IS330\H.C Lombardo App\testbed\test_full_schedule_fix.py` (✅ passing)

### Documentation
- `c:\IS330\H.C Lombardo App\ai_reference\BEST_PRACTICES.md` (violated: testbed first rule)
- `c:\IS330\H.C Lombardo App\QUICK_START_HCL.md`
- `c:\IS330\H.C Lombardo App\dr.foster.md` (project log)

---

**Last Updated:** November 18, 2025 9:05 PM  
**Status:** Blocked - Function code correct but not executing  
**Next Action:** Implement Option 2 (new `/full-schedule` route)  
**Estimated Fix Time:** 15-30 minutes with new route approach
