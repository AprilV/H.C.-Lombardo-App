# Sprint Plan — Sprints 12–16
**Term:** Spring 2026
**Duration:** 10 weeks (April 6 – June 13, 2026)
**Cadence:** 2-week sprints
**Continuing from:** Sprint 11 (completed Nov 20, 2025)

---

## SPRINT OVERVIEW

| Sprint | Dates | Theme | Goal |
|--------|-------|-------|------|
| Sprint 12 | Apr 6 – Apr 18 | Diagnose & Restore | Get production running, audit what's broken |
| Sprint 13 | Apr 20 – May 2 | Data & Clean | Load 2025 season, kill dead code, fix critical bugs |
| Sprint 14 | May 4 – May 16 | ML Retrain | Retrain models on new data, validate accuracy |
| Sprint 15 | May 18 – May 30 | UI & UX Polish | Fix all broken pages, improve user experience |
| Sprint 16 | Jun 1 – Jun 13 | Hardening & Release | Security, performance, monitoring, public release |

---

## SPRINT 12 — Diagnose & Restore
**Dates:** April 6 – April 18, 2026
**Goal:** Know exactly what is and isn't working in production before touching any code.

### Sprint Goal
*"The production environment is diagnosed and all broken functionality is documented. We know exactly what needs to be fixed."*

### Sprint Backlog

| ID | Task | Size | Notes |
|----|------|------|-------|
| PRD-1 | SSH into EC2, check service status | S | `systemctl status hc-lombardo.service` |
| PRD-2 | Read EC2 logs | S | `journalctl -u hc-lombardo.service -n 200` |
| PRD-8 | Verify PostgreSQL is running | S | `psql -U postgres -c "\l"` |
| PRD-3 | Check REACT_APP_API_URL in Amplify console | S | Must match 34.198.25.249:5000 |
| PRD-4 | Test all API endpoints from browser/curl | M | Document which pass/fail |
| PRD-5 | Click through every page in production browser | M | Take notes + screenshots |
| PRD-6 | Create Production Issue Log | M | This becomes the Sprint 13+ backlog |
| PRD-7 | Fix CORS errors if blocking all API calls | M | Low-hanging fruit if found |
| DOC-1 | Update CLAUDE.md with current accurate state | S | Do this after diagnosis |

### Definition of Done
- [ ] EC2 service status confirmed (running or restarted)
- [ ] All API endpoints tested, pass/fail documented
- [ ] Every frontend page visited in production, issues logged
- [ ] Production Issue Log created and committed
- [ ] CLAUDE.md updated

### Acceptance Criteria
- We have a written list of every broken thing in production
- We know if the problem is EC2 (backend), Amplify config (env vars), or code

---

## SPRINT 13 — Data & Clean
**Dates:** April 20 – May 2, 2026
**Goal:** Load 2025 season data. Fix critical bugs. Remove dead code.

### Sprint Goal
*"The 2025 NFL season is fully loaded into the database. Critical routing bugs are fixed. Dead code is gone."*

### Sprint Backlog

| ID | Task | Size | Notes |
|----|------|------|-------|
| DAT-1 | Identify/verify data source for 2025 full season | S | Likely nfl_data_py |
| DAT-2 | Load 2025 games into hcl.games | L | 18 weeks + playoffs = ~285 games |
| DAT-3 | Load 2025 team_game_stats | L | 60+ cols × 570 rows |
| DAT-4 | Verify EPA columns populated | M | May need separate data pull |
| DAT-5 | Update public.teams with 2025 standings | M | |
| DAT-6 | Verify data integrity | M | Counts, nulls, abbrev check |
| DAT-7 | Update season defaults (hardcoded 2025 → dynamic) | M | Backend + frontend |
| BUG-1 | Fix /game-statistics route in App.js | S | 5-minute fix |
| BUG-2 | Fix /matchup-analyzer route in App.js | S | 5-minute fix |
| BUG-3 | Remove hardcoded password fallbacks | S | 3 files |
| BUG-4 | Remove DEBUG print statements | S | api_routes_live_scores.py |
| BUG-5 | Fix background_updater.py missing import | M | |
| CLN-1 | Delete MLPredictionsRedesign.backup.js | S | Git has history |
| CLN-2 | Retire old MLPredictions.js or make final decision | M | |
| CLN-7 | Consolidate get_db_connection() into shared module | M | db_config.py already exists |

### Definition of Done
- [ ] 2025 season data loaded and verified
- [ ] All P1 bugs resolved
- [ ] Dead backup files deleted
- [ ] All routes in App.js point to the correct components
- [ ] No hardcoded passwords in codebase

### Acceptance Criteria
- `SELECT COUNT(*) FROM hcl.games WHERE season = 2025` returns ~285
- `/game-statistics` and `/matchup-analyzer` load correct pages
- `grep -r "aprilv120"` returns nothing

---

## SPRINT 14 — ML Retrain
**Dates:** May 4 – May 16, 2026
**Goal:** Retrain models on 2025 data. Validate accuracy. Improve model quality.

### Sprint Goal
*"XGBoost and Elo models are retrained on 2025 data with validated accuracy. Model performance is visible in the UI."*

### Sprint Backlog

| ID | Task | Size | Notes |
|----|------|------|-------|
| ML-1 | Retrain xgb_winner.pkl on 2025 data | M | Use train_xgb_winner.py |
| ML-2 | Retrain xgb_spread.pkl on 2025 data | M | Use train_xgb_spread.py |
| ML-3 | Validate models: no leakage, MAE in range | M | Compare before/after metrics |
| ML-4 | Rebuild Elo ratings with 2025 games | M | elo_tracker.py |
| ML-8 | Investigate claimed 65.55% accuracy | L | Re-run validation methodology |
| ML-5 | Complete predict_ensemble.py (TODO line 338) | L | Upcoming week detection |
| ML-6 | Automate ELO prediction saving | M | |
| ML-7 | Model accuracy dashboard in UI | M | Season-long AI vs Vegas record |

### Definition of Done
- [ ] Both XGBoost models retrained and saved
- [ ] Elo ratings rebuilt through 2025
- [ ] Accuracy validated with correct time-based splits
- [ ] Model performance visible on ModelPerformance page
- [ ] No TODO comments remaining in predict_ensemble.py

### Acceptance Criteria
- Winner model accuracy ≥ 58% on 2025 hold-out set (Vegas baseline ~52.5%)
- MAE on spread model ≤ 11.5 points (Vegas typical ~10.5)
- ML Predictions page loads with 2025/2026 data without errors

---

## SPRINT 15 — UI & UX Polish
**Dates:** May 18 – May 30, 2026
**Goal:** Every page works correctly in production. App looks and feels production-ready.

### Sprint Goal
*"Every page in the application works correctly in production. No blank screens, no broken data, no obvious UI bugs."*

### Sprint Backlog

| ID | Task | Size | Notes |
|----|------|------|-------|
| UI-1 | Full UI audit (if not done in Sprint 12) | M | Every page, every interaction |
| UI-2 | Fix production-only page failures | L | Based on Sprint 12 issue log |
| UI-3 | Fix live scores offseason behavior | M | "No games scheduled" gracefully |
| UI-4 | Audit MatchupAnalyzer — fix or remove | M | |
| UI-5 | Audit TeamStats — fix or remove | M | |
| UI-6 | Add loading states to all data-fetching pages | M | |
| UI-7 | Add error states when API fails | M | |
| UI-8 | Mobile responsiveness audit | L | |
| UI-9 | Homepage: update for 2025 season / offseason | M | |
| UI-10 | Verify SideMenu links are all correct | S | |
| PRH-7 | 404 and 500 error pages | M | |
| CLN-3 | Consolidate GameStatistics.js / HistoricalData.js | L | If they are truly duplicates |

### Definition of Done
- [ ] Every page loads without errors in production
- [ ] Loading and error states exist on all data-fetching pages
- [ ] Mobile layout tested on 375px viewport
- [ ] SideMenu links verified correct
- [ ] 404 page exists for invalid routes

### Acceptance Criteria
- Click every link in SideMenu → no blank pages, no console errors
- Turn off EC2 → frontend shows error message, not broken/blank

---

## SPRINT 16 — Hardening & Release
**Dates:** June 1 – June 13, 2026
**Goal:** Security, stability, documentation. Ready for public users.

### Sprint Goal
*"The application is secure, stable, documented, and ready for public release. Academic deliverables are complete."*

### Sprint Backlog

| ID | Task | Size | Notes |
|----|------|------|-------|
| PRH-1 | All secrets in environment variables only | M | Audit .env on EC2 |
| PRH-2 | Replace print() with logging throughout | M | All Python files |
| PRH-3 | Verify HTTPS on Amplify frontend | S | |
| PRH-4 | Add basic rate limiting to API | M | Flask-Limiter |
| PRH-5 | Input validation on API endpoints | M | SQL injection prevention |
| PRH-6 | Database connection pooling | L | psycopg2 connection pool |
| PRH-8 | Update / finalize legal disclaimer | S | "Educational purposes only" |
| PRH-10 | Set up basic uptime monitoring | M | AWS CloudWatch or similar |
| DOC-3 | Final project summary for Dr. Foster | M | |
| DOC-4 | Update README.md | M | |
| DOC-2 | Sprint reports for all new sprints | S | |

### Definition of Done
- [ ] Zero hardcoded secrets in any committed file
- [ ] All logging via Python logging module, not print()
- [ ] App loads over HTTPS
- [ ] README accurate and complete
- [ ] Final report submitted to Dr. Foster

### Acceptance Criteria
- `grep -r "aprilv120"` returns nothing in any tracked file
- Production URL loads over HTTPS without warnings
- Dr. Foster submission completed

---

## SPRINT VELOCITY ESTIMATE

Each sprint = 10 working days (assuming ~2-4 hours/day for a student project)
Estimated total capacity per sprint: ~20-40 hours

| Sprint | Story Points Est. | Risk |
|--------|-------------------|------|
| Sprint 12 | Low (diagnosis only) | Low — mostly read-only work |
| Sprint 13 | High (data loading) | Medium — DB operations are risky |
| Sprint 14 | High (ML work) | Medium-High — model accuracy unpredictable |
| Sprint 15 | Medium (UI fixes) | Medium — depends on Sprint 12 issue log |
| Sprint 16 | Medium (hardening) | Low — cleanup + docs |

---

*Last updated: April 3, 2026*
*Owner: April V. Sykes*
*Course: IS330 — Olympic College*
