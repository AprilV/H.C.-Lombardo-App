# ⚠️ STOP! READ THIS BEFORE DOING ANYTHING ⚠️

**THIS FILE EXISTS BECAUSE YOU KEEP MAKING THE SAME MISTAKES**

---

## 🚨 CRITICAL RULES - NO EXCEPTIONS

### 1. **CHECK YOUR CURRENT SPRINT STATUS FIRST**
- **DO NOT ASSUME** what sprint we're on
- **READ** `dr.foster/README.md` to see current sprint
- **READ** `dr.foster.md` for complete project history
- **CHECK** git log to see latest commits
- **As of Nov 20, 2025:** We are on **SPRINT 10 COMPLETE** (NOT Sprint 7!)

### 2. **NEVER TOUCH PRODUCTION FILES DIRECTLY**
- ❌ **DO NOT** modify files in `c:\IS330\H.C Lombardo App\` root
- ❌ **DO NOT** modify `api_routes_hcl.py` in production
- ❌ **DO NOT** modify `frontend/src/` files in production
- ❌ **DO NOT** run `npm run build` in production without testing first
- ✅ **ONLY** work in `testbed/prototypes/[feature_name]/`

### 3. **MANDATORY WORKFLOW - FOLLOW EXACTLY**
```
Step 1: Read dr.foster folder files to understand current state
Step 2: Create feature in testbed/prototypes/[feature_name]/
Step 3: Write comprehensive tests
Step 4: Run tests until 100% pass rate
Step 5: Create timestamped backup of production files
Step 6: Get user approval before touching production
Step 7: Deploy to production
Step 8: Verify deployment works
Step 9: If broken, immediate rollback
```

### 4. **FILES YOU MUST READ BEFORE STARTING ANY WORK**
1. `ai_reference/READ_THIS_FIRST.md` (THIS FILE!)
2. `ai_reference/BEST_PRACTICES.md` - Development rules
3. `ai_reference/STARTUP_GUIDE.md` - How to start/stop app
4. `ai_reference/STARTUP_MODES.md` - Dev vs Production modes
5. `dr.foster/README.md` - Current sprint status
6. `dr.foster.md` - Complete project history

---

## 📋 CURRENT PROJECT STATE

### **Application:** H.C. Lombardo NFL Analytics
- **Course:** IS330
- **Student:** April V. Sykes
- **Current Status:** Sprint 10 Complete
- **Last Commit:** feae9b5f - "Fix team detail page: restore all game stats, add team logos, fix navigation, update database loader"
- **Commit Date:** Recent (check git log for exact date)

### **Technology Stack:**
- **Database:** PostgreSQL `nfl_analytics` 
  - Schema: `hcl` (historical data 1999-2025)
  - Schema: `public` (live standings)
- **Backend:** Flask REST API (Python)
  - Main file: `api_server.py`
  - Routes: `api_routes_hcl.py`, `api_routes_ml.py`
  - Port: 5000
- **Frontend:** React 18.2.0
  - Source: `frontend/src/`
  - Build: `frontend/build/` (served by Flask)
  - Development Port: 3000 (dev mode only)
  - Production Port: 5000 (Flask serves React build)

### **Environments:**
1. **Production:** `c:\IS330\H.C Lombardo App\`
   - Files in root directory
   - NEVER modify directly
   - Always use git restore if broken
   
2. **Testbed:** `c:\IS330\H.C Lombardo App\testbed\`
   - ALL development happens here first
   - Create `testbed/prototypes/[feature_name]/` for new features
   - Test until 100% pass rate
   - Only then migrate to production

### **Startup Procedures:**
- **Production Mode:** `START.bat` (port 5000 only, optimized build)
- **Dev Mode:** `START-DEV.bat` (port 3000 + 5000, hot reload)
- **Stop:** `STOP.bat` (graceful shutdown)
- **Never:** Manually run `python api_server.py` without understanding context

---

## 🚫 MISTAKES YOU KEEP MAKING

### **Mistake #1: Assuming Sprint Number**
❌ You assumed Sprint 7 when we're on Sprint 10
✅ **FIX:** Read `dr.foster/README.md` FIRST to see current sprint

### **Mistake #2: Modifying Production Directly**
❌ You modified `api_routes_hcl.py` and `TeamDetail.js` in production
❌ You broke the entire team detail page
✅ **FIX:** Work in `testbed/prototypes/` ONLY

### **Mistake #3: Not Following BEST_PRACTICES.md**
❌ You skip testbed, skip tests, skip backups
❌ You make changes user never approved
✅ **FIX:** Follow the documented workflow exactly

### **Mistake #4: Overconfidence**
❌ You think you understand the project without reading docs
❌ You make wholesale changes without checking what data is being received
✅ **FIX:** Be humble, read docs, ask before changing anything

### **Mistake #5: Not Understanding Data Flow**
❌ You changed API endpoints without checking what fields the frontend expects
❌ You broke stats, charts, and display because field names didn't match
✅ **FIX:** Check API response structure, check frontend code that consumes it

---

## 📖 WHAT YOU NEED TO KNOW ABOUT THIS APP

### **Database Schema:**
- **hcl.games** - Individual game records (1999-2025)
- **hcl.team_game_stats** - Team performance per game (47+ metrics)
- **hcl.team_season_stats** - Aggregated season stats
- Materialized views for performance
- EPA (Expected Points Added) - most important predictive stat

### **API Endpoints (api_routes_hcl.py):**
- `GET /api/hcl/teams` - List all teams
- `GET /api/hcl/teams/<abbr>` - Team season stats
- `GET /api/hcl/teams/<abbr>/games` - Team game history
- `GET /api/hcl/games/<game_id>` - Individual game details

### **Frontend Pages:**
- **Home** - Team standings grid
- **TeamDetail** - Individual team page (stats, charts, game history)
- **MatchupAnalyzer** - Compare two teams
- **GameStatistics** - Historical game lookups
- **MLPredictions** - Neural network predictions
- **Analytics** - Advanced analytics dashboard

### **Current Features (Sprint 10):**
- ✅ 32 NFL teams with live standings
- ✅ Historical data 1999-2025 (7,263 games)
- ✅ 47 statistical metrics per game
- ✅ EPA/Success Rate calculations
- ✅ 3-layer neural network for predictions
- ✅ Chart.js visualizations
- ✅ Team logos from ESPN
- ✅ Responsive design
- ✅ PWA capabilities

---

## 🎯 WHEN USER ASKS FOR CHANGES

### **Step 1: STOP and READ**
- [ ] Read this file (READ_THIS_FIRST.md)
- [ ] Read BEST_PRACTICES.md
- [ ] Read dr.foster/README.md for current sprint
- [ ] Check git status to see what's modified
- [ ] Check git log to see recent commits

### **Step 2: UNDERSTAND the Request**
- [ ] What exactly does user want?
- [ ] What files are involved?
- [ ] What's the current behavior?
- [ ] What should the new behavior be?
- [ ] Have I verified the current code by reading it?

### **Step 3: PLAN in Testbed**
- [ ] Create `testbed/prototypes/[feature_name]/`
- [ ] Write test file with expected behavior
- [ ] Write implementation
- [ ] Run tests until 100% pass

### **Step 4: ASK for Approval**
- [ ] Show user what you tested
- [ ] Show test results (100% pass required)
- [ ] Explain what will change in production
- [ ] Wait for approval before touching production

### **Step 5: DEPLOY Carefully**
- [ ] Create backup: `backups/[filename]_backup_YYYYMMDD_HHMMSS.py`
- [ ] Make ONE change at a time
- [ ] Test after EACH change
- [ ] If anything breaks, rollback immediately

---

## 💡 REMEMBER

**USER HAS SPENT 10 WEEKS BUILDING THIS APP**

You can break it in seconds by:
- Not reading documentation
- Assuming you know better
- Modifying production directly
- Skipping tests
- Being overconfident

**BE HUMBLE. BE CAREFUL. FOLLOW THE RULES.**

---

## 🔧 EMERGENCY RECOVERY

If you broke production:

```powershell
# Step 1: Stop everything
cd "c:\IS330\H.C Lombardo App"
Stop-Process -Name python* -Force

# Step 2: Restore from git
git status  # See what you modified
git restore [filename]  # Restore each file
# OR
git restore .  # Restore everything

# Step 3: Rebuild frontend if needed
cd frontend
npm run build

# Step 4: Restart server
cd ..
START.bat
```

---

## 📌 FINAL CHECKLIST BEFORE EVERY ACTION

- [ ] Did I read this file?
- [ ] Did I check current sprint in dr.foster/README.md?
- [ ] Am I working in testbed/ (not production)?
- [ ] Did I write tests first?
- [ ] Did I get user approval?
- [ ] Do I have backups ready?
- [ ] Do I understand what I'm changing and why?

**IF YOU ANSWERED "NO" TO ANY OF THESE, STOP AND FIX IT.**

---

**Last Updated:** November 20, 2025  
**Reason:** You keep making the same mistakes. Read this file EVERY TIME.  
**Consequence:** User has to restore from git because you broke production.  
**Solution:** FOLLOW THIS FILE EXACTLY.
