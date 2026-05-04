# H.C. Lombardo NFL Analytics — Product Backlog
**Term:** Spring 2026 (April 6 – June 13, 2026)
**Goal:** Public-release-ready application
**Continuing from:** Sprint 11 (completed Nov 20, 2025)
**Next sprint:** Sprint 14

---

## HOW TO READ THIS BACKLOG

Priority: **P1** = Must have | **P2** = Should have | **P3** = Nice to have
Size: **S** = Small (hours) | **M** = Medium (half-day) | **L** = Large (full day+)
Status: **OPEN** | **IN SPRINT** | **DONE**

---

## EPIC 1 — PRODUCTION RESTORATION
*The app is down or broken in production. Nothing else matters until this is fixed.*

| ID | Story | Priority | Size | Status |
|----|-------|----------|------|--------|
| PRD-1 | Verify EC2 service is running (`systemctl status hc-lombardo.service`) | P1 | S | OPEN |
| PRD-2 | Check EC2 logs for errors (`journalctl -u hc-lombardo.service`) | P1 | S | OPEN |
| PRD-3 | Verify REACT_APP_API_URL in AWS Amplify environment variables matches EC2 IP | P1 | S | OPEN |
| PRD-4 | Test every API endpoint from production (`curl http://34.198.25.249:5000/health`) | P1 | M | OPEN |
| PRD-5 | Test every frontend page in production browser and document what's broken | P1 | M | OPEN |
| PRD-6 | Create a "Production Issue Log" listing every broken thing with screenshots | P1 | M | OPEN |
| PRD-7 | Fix any CORS errors preventing frontend from reaching backend | P1 | M | OPEN |
| PRD-8 | Verify PostgreSQL is running and accessible on EC2 | P1 | S | OPEN |
| PRD-9 | Create a new AWS account for EC2 continuity and migrate required runtime/deploy access so active work is not blocked by current account lockout constraints | P1 | M | IN SPRINT |

---

## EPIC 2 — NEW SEASON DATA
*2025 NFL season is complete. Data must be loaded before ML retraining can happen.*

| ID | Story | Priority | Size | Status |
|----|-------|----------|------|--------|
| DAT-1 | Identify data source for 2025 full season (NFLverse, nfl_data_py, ESPN) | P1 | S | OPEN |
| DAT-2 | Load 2025 games into hcl.games (18 weeks regular season + playoffs) | P1 | L | OPEN |
| DAT-3 | Load 2025 team_game_stats (all 60+ columns per game) | P1 | L | OPEN |
| DAT-4 | Verify EPA columns are populated for 2025 games | P1 | M | OPEN |
| DAT-5 | Update public.teams with 2025 final standings | P1 | M | DONE |
| DAT-6 | Verify data integrity: row counts, missing values, team abbreviations | P1 | M | DONE |
| DAT-7 | Update backend season defaults from hardcoded 2025 to dynamic current/latest-season logic | P1 | M | DONE |
| DAT-8 | Verify all 4 analytics views still return data with 2025 loaded | P1 | M | OPEN |

---

## EPIC 3 — CRITICAL BUG FIXES
*These are broken right now regardless of production state.*

| ID | Story | Priority | Size | Status |
|----|-------|----------|------|--------|
| BUG-1 | Fix App.js: /game-statistics routes to TeamComparison (wrong component) | P1 | S | DONE |
| BUG-2 | Fix App.js: /matchup-analyzer routes to TeamComparison (wrong component) | P1 | S | DONE |
| BUG-3 | Remove hardcoded password 'aprilv120' fallback from api_server.py, api_routes_hcl.py, api_routes_live_scores.py | P1 | S | DONE |
| BUG-4 | Remove 7+ print(f"DEBUG:...") statements from api_routes_live_scores.py | P1 | S | DONE |
| BUG-5 | Fix background_updater.py: imports MultiSourceDataFetcher which doesn't exist | P1 | M | DONE |
| BUG-6 | Fix season default logic (hardcoded 2025 throughout) — implement dynamic current-season logic | P1 | M | DONE |
| BUG-7 | Fix team abbreviation mismatches between ESPN (LAR, WSH) and database (LA, WAS) — audit all locations | P2 | M | DONE |
| BUG-8 | Fix background_updater_service.py: hardcoded Linux path breaks Windows dev | P2 | S | OPEN |

---

## EPIC 4 — DEAD CODE CLEANUP
*Per AI_EXECUTION_CONTRACT.md: zero tolerance for dead code.*

| ID | Story | Priority | Size | Status |
|----|-------|----------|------|--------|
| CLN-1 | Delete MLPredictionsRedesign.backup.js | P1 | S | DONE |
| CLN-2 | Evaluate MLPredictions.js (old) vs MLPredictionsRedesign.js (new) — keep one, remove other | P1 | M | OPEN |
| CLN-3 | Evaluate GameStatistics.js vs HistoricalData.js — near duplicates, consolidate | P2 | L | OPEN |
| CLN-4 | Remove legacy ML models: nfl_neural_network.pkl, nfl_neural_network_v2.pkl | P2 | S | OPEN |
| CLN-5 | Remove /ml-predictions-old route from App.js if old component is retired | P2 | S | OPEN |
| CLN-6 | Audit all frontend components for unused imports and dead functions | P2 | M | OPEN |
| CLN-7 | Consolidate get_db_connection() — defined separately in api_server.py, api_routes_hcl.py, api_routes_live_scores.py | P2 | M | OPEN |

---

## EPIC 5 — ML MODEL IMPROVEMENTS
*The core academic deliverable. Models need retraining + improvement.*

| ID | Story | Priority | Size | Status |
|----|-------|----------|------|--------|
| ML-1 | Retrain xgb_winner.pkl on 2025 data | P1 | M | IN SPRINT |
| ML-2 | Retrain xgb_spread.pkl on 2025 data | P1 | M | IN SPRINT |
| ML-3 | Validate retrained models: no data leakage, MAE in expected range | P1 | M | IN SPRINT |
| ML-4 | Rebuild Elo ratings with 2025 games | P1 | M | IN SPRINT |
| ML-5 | Complete predict_ensemble.py: implement upcoming week detection (TODO at line 338) | P2 | L | IN SPRINT |
| ML-6 | Automate ELO predictions: generate and save to ml_predictions_elo at season start | P2 | M | IN SPRINT |
| ML-7 | Add model accuracy dashboard: show season-long AI vs Vegas win rate | P2 | M | IN SPRINT |
| ML-8 | Investigate whether 65.55% accuracy is real or inflated (validate methodology) | P2 | L | IN SPRINT |
| ML-9 | Feature importance visualization: which stats matter most to predictions | P3 | M | IN SPRINT |
| ML-10 | Confidence intervals on score predictions (+/- range) | P3 | M | IN SPRINT |
| ML-11 | Automated weekly retraining pipeline (after each game week) | P3 | L | IN SPRINT |
| ML-12 | Betting ROI tracker: if you followed AI picks, what's your record/profit? | P3 | L | IN SPRINT |

---

## EPIC 6 — UI/UX IMPROVEMENTS
*Interface issues visible after deployment.*

| ID | Story | Priority | Size | Status |
|----|-------|----------|------|--------|
| UI-1 | Full UI audit: go through every page in production, screenshot what's wrong | P1 | M | OPEN |
| UI-2 | Fix any pages that show blank/error in production but work locally | P1 | L | OPEN |
| UI-3 | Fix live scores page: offseason behavior (show "no games" gracefully, not broken) | P2 | M | OPEN |
| UI-4 | MatchupAnalyzer.js — audit what this is supposed to do vs what it actually does | P2 | M | OPEN |
| UI-5 | TeamStats.js — audit current state, decide if it adds value or duplicates | P2 | M | OPEN |
| UI-6 | Add loading states to all pages that fetch data | P2 | M | OPEN |
| UI-7 | Add error states to all pages when API fails | P2 | M | OPEN |
| UI-8 | Make all pages mobile-responsive (if not already) | P2 | L | OPEN |
| UI-9 | Homepage: update to show 2025 season summary + offseason state | P2 | M | OPEN |
| UI-10 | Navigation: verify SideMenu has correct links to all working pages | P2 | S | OPEN |

---

## EPIC 7 — PRODUCTION HARDENING
*What needs to be true before public release.*

| ID | Story | Priority | Size | Status |
|----|-------|----------|------|--------|
| PRH-1 | Move all secrets to environment variables (EC2 .env file) | P1 | M | OPEN |
| PRH-2 | Set up proper logging on EC2 (replace print() with logging module) | P1 | M | OPEN |
| PRH-3 | Verify HTTPS is working on Amplify frontend | P1 | S | OPEN |
| PRH-4 | Add rate limiting to API (prevent abuse) | P2 | M | OPEN |
| PRH-5 | Add input validation to all API endpoints that accept user params | P2 | M | OPEN |
| PRH-6 | Database connection pooling (currently opens/closes per request) | P2 | L | OPEN |
| PRH-7 | Error pages: proper 404 and 500 pages in frontend | P2 | M | OPEN |
| PRH-8 | Remove "educational purposes only" if this is going public (or keep and update disclaimer) | P2 | S | OPEN |
| PRH-9 | Performance: audit slow API queries, add indexes if needed | P3 | L | OPEN |
| PRH-10 | Set up basic monitoring (AWS CloudWatch or uptime check) | P3 | M | OPEN |

---

## EPIC 8 — DOCUMENTATION & ACADEMIC DELIVERABLES
*Required for class + helpful for public release.*

| ID | Story | Priority | Size | Status |
|----|-------|----------|------|--------|
| DOC-1 | Update CLAUDE.md with new season, current sprint, accurate state | P1 | S | OPEN |
| DOC-2 | Write sprint reports for Sprints 12–16 as each completes | P1 | S (per sprint) | OPEN |
| DOC-3 | Write final project summary for Dr. Foster | P1 | M | OPEN |
| DOC-4 | Update README.md with current deployment info and setup instructions | P2 | M | OPEN |
| DOC-5 | Create API documentation (even basic — endpoint list with params and responses) | P3 | L | OPEN |

---

## BACKLOG SUMMARY

| Epic | Items | P1 | P2 | P3 |
|------|-------|----|----|-----|
| Production Restoration | 9 | 9 | 0 | 0 |
| New Season Data | 8 | 8 | 0 | 0 |
| Critical Bug Fixes | 8 | 6 | 2 | 0 |
| Dead Code Cleanup | 7 | 2 | 5 | 0 |
| ML Model Improvements | 12 | 4 | 4 | 4 |
| UI/UX Improvements | 10 | 2 | 8 | 0 |
| Production Hardening | 10 | 2 | 5 | 3 |
| Documentation | 5 | 3 | 1 | 1 |
| **TOTAL** | **69** | **36** | **25** | **8** |

---

*Last updated: May 4, 2026*
*Owner: April V. Sykes*
*Course: IS330 — Olympic College*
