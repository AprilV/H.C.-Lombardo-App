# Dashboard Fix Plan — April 20, 2026

## GOAL
Restore the dashboard to a fully working state:
- Nav bar functional (all tabs clickable)
- Sprint 13 showing correctly (auto-detected from date)
- All April 19th changes intact (Sprint 13 tasks, RAG banner, weekly report, charts)

---

## PLANNING

**Target commit:** `c51ee33e` — "AI Project Log v2"
- Last known good state before logbook broke the script block
- Contains ALL April 19th changes (verified via grep):
  - getCurrentSprint() auto-detection
  - CURRENT_DASH_SPRINT wired to getCurrentSprint()
  - Sprint 13 task data (TA-057, 058, 059, 063, 068, 069, 070)
  - RAG banner with id="rag-banner"
  - Dashboard dates updated to Apr 19
  - Weekly report rebuilt with Sprint 13 data
  - WEEK_META with Sprint 13 weeks
  - Sprint selector automation
- Nav bar was working at this commit
- Sprint 13 auto-detection was working at this commit

**Root cause of current break:**
embed_devlog.py injected logbook content into Dashboard/index.html and disrupted
the main script block structure. The browser throws a SyntaxError that crashes
ALL JavaScript — not just the nav bar. Sprint 13 never loads because the script
never runs. Every April 19th change is in the file but none of it executes.

---

## CHANGES

**Step 1:** Run restore command:
```
git checkout c51ee33e -- Dashboard/index.html
```
**Step 2:** Nothing else touched. No other files modified.

---

## VERIFICATION

After restore, April hard-reloads at `http://localhost:5500/Dashboard/index.html` (`Ctrl+Shift+R`)

**Check list:**
- [ ] Nav tabs are clickable (Dashboard, Sprint Backlog, Product Backlog, etc.)
- [ ] Sprint 13 shows as current sprint (not Sprint 12)
- [ ] RAG banner shows green / Sprint 13 message
- [ ] Task tracker shows TA-057, 058, 059, 063, 068, 069
- [ ] Weekly report tab works
- [ ] Charts load correctly
- [ ] No console errors

Claude verifies all 6 batches of April 19th changes are present and functioning.

---

## BACKOUT PLAN

If restore makes things worse or breaks additional things:
```
git checkout 95c69b1c -- Dashboard/index.html
```
This returns the file exactly to where it is right now (current broken state).
Nothing is permanently lost — current state is preserved in git at 95c69b1c.

---

## IF VERIFICATION FAILS

**If nav is still broken after restore:**
- c51ee33e had a broken nav before the logbook was added
- Extract script block, run through Chrome DevTools (not Node) to find exact error
- Fix only that specific line
- Re-verify

**If Sprint 13 still shows Sprint 12:**
- Read getCurrentSprint() date logic in restored file
- Fix date comparison
- Re-verify

**If both fail:**
- Do not push anything
- Report full findings to April
- Reassess with fresh approach

---

## PRODUCTION

- This is LOCAL DEV only
- Do NOT push to GitHub until April explicitly says "push"
- Once all verification checks pass, commit the working file
- After dashboard is stable, move to Sprint 13 ML tasks:
  - TA-068 CRITICAL: Create ml/elo_ratings.py
  - TA-069 HIGH: Fix early return bug in predict_week.py
  - TA-057 CRITICAL: Fix train_xgb_winner.py schema
  - TA-058 CRITICAL: Fix broken SQL in train_xgb_spread.py
  - TA-059 HIGH: Remove hardcoded season=2025
  - TA-063 CRITICAL: EC2 disk cleanup

---

## RULES
- Claude reports after EVERY action before moving to next step
- Nothing happens without April's go-ahead
- No restores beyond c51ee33e
- No pushes to GitHub
- No touching START-DEV.bat or STOP.bat
