# Sprint 12 — Detailed Task Breakdown
**Theme:** Diagnose & Restore  
**Dates:** April 6 – April 18, 2026  
**Approach:** Treat this as a NEW project. Assume everything is broken. Prove otherwise.  
**Output:** A completed Production Issue Log that drives all work in Sprints 13–16.

---

## RULE FOR THIS SPRINT
Do NOT fix anything unless it takes under 5 minutes and is blocking discovery.  
Document everything. Fix later.

---

## AREA 1 — EC2 / Backend Server

### 1.1 SSH Access
- [ ] Confirm SSH key is available locally
- [ ] SSH into EC2 (`ssh -i <key>.pem ec2-user@34.198.25.249`)
- [ ] Confirm you can connect without errors
- [ ] Log result → Issue Log

### 1.2 Service Status
- [ ] `systemctl status hc-lombardo.service`
- [ ] Is it active/running or failed/inactive?
- [ ] `journalctl -u hc-lombardo.service -n 200` — read last 200 log lines
- [ ] Look for: import errors, missing packages, port conflicts, DB connection failures
- [ ] `ps aux | grep python` — is Flask process actually running?
- [ ] `netstat -tlnp | grep 5000` — is port 5000 actually listening?
- [ ] Log all findings → Issue Log

### 1.3 EC2 Environment
- [ ] `df -h` — check disk space (full disk kills everything)
- [ ] `free -m` — check memory
- [ ] `python3 --version` — confirm Python version
- [ ] `pip3 list | grep -E "flask|xgboost|psycopg2|pandas|sklearn"` — confirm packages installed
- [ ] Check if `.env` file exists on EC2 with correct DB password
- [ ] Check if `backups/` or other large folders eating disk
- [ ] Log findings → Issue Log

### 1.4 Security Group / Firewall
- [ ] Confirm port 5000 is open in AWS Security Group (EC2 console)
- [ ] Confirm port 5432 is NOT open externally (PostgreSQL should be local only)
- [ ] `curl http://localhost:5000/health` from inside EC2 — does Flask respond locally?
- [ ] Log findings → Issue Log

---

## AREA 2 — Database (PostgreSQL)

### 2.1 Service Status
- [ ] `systemctl status postgresql` — is DB running?
- [ ] `psql -U postgres -c "\l"` — list databases, confirm `nfl_analytics` exists
- [ ] `psql -U postgres -d nfl_analytics -c "\dn"` — confirm `hcl` schema exists
- [ ] Log findings → Issue Log

### 2.2 Table Integrity
- [ ] `SELECT COUNT(*) FROM hcl.games;` — expect ~7,263
- [ ] `SELECT COUNT(*) FROM hcl.team_game_stats;` — expect ~14,398
- [ ] `SELECT COUNT(*) FROM hcl.ml_predictions;`
- [ ] `SELECT COUNT(*) FROM hcl.betting_lines;`
- [ ] `SELECT COUNT(*) FROM public.teams;` — expect 32
- [ ] `SELECT season, COUNT(*) FROM hcl.games GROUP BY season ORDER BY season;` — check season coverage
- [ ] `SELECT MAX(season) FROM hcl.games;` — what is the most recent season loaded?
- [ ] Log findings → Issue Log

### 2.3 Data Quality Spot Check
- [ ] `SELECT COUNT(*) FROM hcl.team_game_stats WHERE epa_per_play IS NULL;` — check EPA population
- [ ] `SELECT COUNT(*) FROM hcl.games WHERE home_score IS NULL;` — check for incomplete games
- [ ] Log findings → Issue Log

### 2.4 Views
- [ ] `SELECT COUNT(*) FROM hcl.v_team_betting_performance;` — views intact?
- [ ] `SELECT COUNT(*) FROM hcl.v_weather_impact_analysis;`
- [ ] Log findings → Issue Log

---

## AREA 3 — API Endpoints

Test every endpoint. Use browser or curl. Format: `http://34.198.25.249:5000/<endpoint>`

### 3.1 Health & Core
- [ ] `GET /health` — basic health check
- [ ] `GET /api/hcl/teams` — returns 32 teams?
- [ ] `GET /api/hcl/summary` — summary stats

### 3.2 Historical Data Endpoints
- [ ] `GET /api/hcl/teams/NE` — single team
- [ ] `GET /api/hcl/teams/NE/games` — team games
- [ ] `GET /api/hcl/games/week/2024/10` — week data
- [ ] `GET /api/hcl/analytics/betting` — betting analytics
- [ ] `GET /api/hcl/analytics/weather` — weather impact
- [ ] `GET /api/hcl/analytics/rest` — rest advantage
- [ ] `GET /api/hcl/analytics/referees` — referee tendencies

### 3.3 ML Endpoints
- [ ] `GET /api/ml/model-info` — model loaded?
- [ ] `GET /api/ml/model-performance` — performance data
- [ ] `GET /api/ml/predict-week/2024/18` — predictions for a known week
- [ ] `GET /api/ml/predict-upcoming` — upcoming week
- [ ] `GET /api/ml/available-weeks` — what weeks are available?
- [ ] `GET /api/ml/season-ai-vs-vegas/2024` — full season comparison
- [ ] `GET /api/elo/ratings/current` — Elo ratings loaded?
- [ ] `GET /api/elo/predict-week/2024/18` — Elo predictions
- [ ] `GET /api/predictions/current-week` — combined predictions
- [ ] `GET /api/predictions/combined/2024/18`

### 3.4 Live Scores
- [ ] `GET /api/live-scores` — ESPN response (will be empty/offseason but should not error)

### 3.5 CORS Check
- [ ] Open browser DevTools → Network tab → load production frontend → look for CORS errors
- [ ] Note which endpoints return CORS errors vs which work
- [ ] Log findings → Issue Log

---

## AREA 4 — Frontend / AWS Amplify

### 4.1 Amplify Configuration
- [ ] Log into AWS Amplify console
- [ ] Confirm app is deployed and build is not failed
- [ ] Check `REACT_APP_API_URL` environment variable — must be `http://34.198.25.249:5000`
- [ ] Note the current production URL
- [ ] Check last successful build date
- [ ] Log findings → Issue Log

### 4.2 Page-by-Page Audit
Open the production URL in browser. Visit every page. For each:  
Record: Loads / Blank / Error / Partial

- [ ] **Homepage** — loads? data displays?
- [ ] **Live Scores** (`/live-scores`) — loads? (offseason = no games, but no crash)
- [ ] **Analytics** (`/analytics`) — loads? charts render?
- [ ] **ML Predictions** (`/ml-predictions`) — loads? predictions showing?
- [ ] **ML Predictions Redesign** (`/ml-predictions-redesign`) — loads?
- [ ] **Model Performance** (`/model-performance`) — loads? accuracy data?
- [ ] **Team Stats** (`/team-stats`) — loads? dropdown works?
- [ ] **Team Comparison** (`/team-comparison`) — loads?
- [ ] **Team Detail** (`/team-detail`) — loads? pick a team and view?
- [ ] **Matchup Analyzer** (`/matchup-analyzer`) — loads?
- [ ] **Game Statistics** (`/game-statistics`) — loads? (known routing bug)
- [ ] **Historical Data** (`/historical-data`) — loads?
- [ ] **Admin** (`/admin`) — loads? buttons work?
- [ ] **Settings** (`/settings`) — loads? theme switching works?
- [ ] Log ALL issues → Issue Log with page name and description

### 4.3 Console Error Check
- [ ] Open DevTools Console on each broken page
- [ ] Note error messages (especially: 404, CORS, "Cannot read properties of undefined")
- [ ] Log findings → Issue Log

### 4.4 Side Menu
- [ ] Every link in the side menu — does it navigate to the right page?
- [ ] Any broken/missing links?
- [ ] Log findings → Issue Log

---

## AREA 5 — Local Code Audit

### 5.1 Uncommitted Changes
- [ ] `git status` — list all modified files
- [ ] `git diff frontend/src/App.js` — check known routing bugs
- [ ] Review each modified file — is the change an improvement or a broken experiment?
- [ ] Log findings → Issue Log

### 5.2 Known Bugs (Pre-confirmed)
- [ ] Confirm App.js routing bug: `/game-statistics` → routes to wrong component
- [ ] Confirm App.js routing bug: `/matchup-analyzer` → routes to wrong component
- [ ] Confirm hardcoded password `REDACTED_DB_PASSWORD` still in: `api_server.py`, `api_routes_hcl.py`, `api_routes_live_scores.py`
- [ ] Confirm `background_updater.py` import issue
- [ ] Confirm DEBUG print statements in `api_routes_live_scores.py`
- [ ] Confirm `train_xgb_winner.py` uses `hcl_test` schema (wrong)
- [ ] Confirm broken SQL in `train_xgb_spread.py`
- [ ] Log all confirmations → Issue Log

### 5.3 ML Models on EC2
- [ ] SSH: confirm `ml/models/xgb_winner.pkl` exists on EC2
- [ ] SSH: confirm `ml/models/xgb_spread.pkl` exists on EC2
- [ ] SSH: confirm `ml/models/elo_ratings_current.json` exists on EC2
- [ ] SSH: `ls -lh ml/models/` — check file sizes and dates
- [ ] Log findings → Issue Log

---

## AREA 6 — CORS & Connectivity End-to-End

- [ ] From local machine: `curl http://34.198.25.249:5000/health`
- [ ] From production frontend URL: open DevTools and attempt an API call
- [ ] Identify if CORS is blocking frontend → backend
- [ ] Check `api_server.py` CORS configuration — does it allow the Amplify domain?
- [ ] Log findings → Issue Log

---

## SPRINT 12 DEFINITION OF DONE

- [ ] Every item in this checklist attempted and result logged
- [ ] Production Issue Log has an entry for every problem found
- [ ] Every API endpoint has a pass/fail status
- [ ] Every frontend page has a load status
- [ ] EC2 service status confirmed
- [ ] Database record counts verified
- [ ] CLAUDE.md updated to reflect actual current state

---

## DELIVERABLE

A completed [PRODUCTION_ISSUE_LOG.md](PRODUCTION_ISSUE_LOG.md) with:
- Every broken thing documented
- Severity assigned (P1/P2/P3)
- Which sprint will fix it
- No guessing — only what was actually observed

---

*Sprint 12 begins April 6, 2026*  
*Owner: April V. Sykes*
