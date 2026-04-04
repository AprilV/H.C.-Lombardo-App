# Production Issue Log & Backlog Register
**Created:** April 3, 2026  
**Purpose:** Living document. Every issue found during Sprint 12 discovery goes here.  
**Owner:** April V. Sykes

---

## HOW TO USE THIS DOCUMENT

- Add issues as they are discovered — do not wait until the end of the sprint
- Assign a severity immediately
- Do NOT fix P2/P3 issues during Sprint 12 — log and move on
- P1 issues blocking discovery may be fixed inline
- This document becomes the Sprint 13+ backlog

### Severity Levels
| Level | Meaning |
|-------|---------|
| **P1** | Blocks the app entirely — nothing works without this |
| **P2** | Major feature broken — significant impact to users |
| **P3** | Minor issue — broken but workaround exists |
| **P4** | Polish / nice to have |

### Status Values
`OPEN` · `IN PROGRESS` · `FIXED` · `WONT FIX` · `NEEDS INFO`

---

## SECTION 1 — EC2 / BACKEND

| # | Issue | Severity | Status | Sprint | Notes |
|---|-------|----------|--------|--------|-------|
| EC2-001 | | | | | |

*Add rows as issues are found during Sprint 12 discovery.*

---

## SECTION 2 — DATABASE

| # | Issue | Severity | Status | Sprint | Notes |
|---|-------|----------|--------|--------|-------|
| DB-001 | | | | | |

---

## SECTION 3 — API ENDPOINTS

| # | Endpoint | Result | Error | Severity | Status | Sprint |
|---|----------|--------|-------|----------|--------|--------|
| API-001 | GET /health | | | | | |
| API-002 | GET /api/hcl/teams | | | | | |
| API-003 | GET /api/hcl/summary | | | | | |
| API-004 | GET /api/hcl/teams/:abbr | | | | | |
| API-005 | GET /api/hcl/teams/:abbr/games | | | | | |
| API-006 | GET /api/hcl/games/week/:s/:w | | | | | |
| API-007 | GET /api/hcl/analytics/betting | | | | | |
| API-008 | GET /api/hcl/analytics/weather | | | | | |
| API-009 | GET /api/hcl/analytics/rest | | | | | |
| API-010 | GET /api/hcl/analytics/referees | | | | | |
| API-011 | GET /api/ml/model-info | | | | | |
| API-012 | GET /api/ml/model-performance | | | | | |
| API-013 | GET /api/ml/predict-week/2024/18 | | | | | |
| API-014 | GET /api/ml/predict-upcoming | | | | | |
| API-015 | GET /api/ml/available-weeks | | | | | |
| API-016 | GET /api/ml/season-ai-vs-vegas/2024 | | | | | |
| API-017 | GET /api/ml/performance-stats | | | | | |
| API-018 | GET /api/elo/ratings/current | | | | | |
| API-019 | GET /api/elo/predict-week/2024/18 | | | | | |
| API-020 | GET /api/predictions/current-week | | | | | |
| API-021 | GET /api/predictions/combined/2024/18 | | | | | |
| API-022 | GET /api/live-scores | | | | | |

---

## SECTION 4 — FRONTEND PAGES

| # | Page | Route | Status | Issues Found | Severity | Sprint |
|---|------|-------|--------|-------------|----------|--------|
| UI-001 | Homepage | / | | | | |
| UI-002 | Live Scores | /live-scores | | | | |
| UI-003 | Analytics | /analytics | | | | |
| UI-004 | ML Predictions | /ml-predictions | | | | |
| UI-005 | ML Predictions Redesign | /ml-predictions-redesign | | | | |
| UI-006 | Model Performance | /model-performance | | | | |
| UI-007 | Team Stats | /team-stats | | | | |
| UI-008 | Team Comparison | /team-comparison | | | | |
| UI-009 | Team Detail | /team-detail | | | | |
| UI-010 | Matchup Analyzer | /matchup-analyzer | | | | |
| UI-011 | Game Statistics | /game-statistics | | | | |
| UI-012 | Historical Data | /historical-data | | | | |
| UI-013 | Admin | /admin | | | | |
| UI-014 | Settings | /settings | | | | |
| UI-015 | Side Menu links | — | | | | |

---

## SECTION 5 — KNOWN BUGS (Pre-Sprint 12)

These are confirmed issues from code review before discovery. Verify they still exist.

| # | Issue | File | Line | Severity | Status | Sprint |
|---|-------|------|------|----------|--------|--------|
| BUG-001 | /game-statistics routes to wrong component | frontend/src/App.js | ~58 | P2 | OPEN | S13 |
| BUG-002 | /matchup-analyzer routes to wrong component | frontend/src/App.js | ~59 | P2 | OPEN | S13 |
| BUG-003 | Hardcoded password 'aprilv120' fallback | api_server.py | ~77 | P1 | OPEN | S13 |
| BUG-004 | Hardcoded password 'aprilv120' fallback | api_routes_hcl.py | ~22 | P1 | OPEN | S13 |
| BUG-005 | Hardcoded password 'aprilv120' fallback | api_routes_live_scores.py | ~29 | P1 | OPEN | S13 |
| BUG-006 | 7+ DEBUG print statements in production | api_routes_live_scores.py | various | P3 | OPEN | S13 |
| BUG-007 | background_updater.py missing import | background_updater.py | — | P2 | OPEN | S13 |
| BUG-008 | train_xgb_winner.py uses hcl_test schema | ml/train_xgb_winner.py | 255 | P2 | OPEN | S14 |
| BUG-009 | Broken SQL WINDOW clause in spread training | ml/train_xgb_spread.py | 95-116 | P2 | OPEN | S14 |
| BUG-010 | EPA features loaded in SQL but not used in model | ml/train_xgb_spread.py | 174-181 | P3 | OPEN | S14 |
| BUG-011 | predict_ensemble.py TODO at line 338 (incomplete) | ml/predict_ensemble.py | 338 | P2 | OPEN | S14 |
| BUG-012 | Default season hardcoded as 2025 throughout backend | various | — | P2 | OPEN | S13 |
| BUG-013 | MLPredictionsRedesign.backup.js still in src/ | frontend/src/ | — | P4 | OPEN | S13 |

---

## SECTION 6 — AMPLIFY / DEPLOYMENT

| # | Issue | Severity | Status | Sprint | Notes |
|---|-------|----------|--------|--------|-------|
| DEP-001 | | | | | |

---

## SECTION 7 — NEW ISSUES (Discovered During Sprint 12)

*This section fills up as you work through the discovery checklist.*

| # | Area | Issue Description | Severity | Status | Sprint | Notes |
|---|------|-------------------|----------|--------|--------|-------|
| NEW-001 | | | | | | |

---

## SPRINT ASSIGNMENT SUMMARY

*Fill this in at the end of Sprint 12 after all issues are logged.*

| Sprint | Issues Assigned |
|--------|----------------|
| Sprint 12 (immediate) | |
| Sprint 13 (Data & Clean) | BUG-001 through BUG-013 + new |
| Sprint 14 (ML Retrain) | BUG-008, BUG-009, BUG-010, BUG-011 |
| Sprint 15 (UI Polish) | All UI-* issues |
| Sprint 16 (Hardening) | Security, perf, monitoring |

---

## METRICS

| Metric | Count |
|--------|-------|
| Total issues logged | 0 |
| P1 issues | 0 |
| P2 issues | 0 |
| P3 issues | 0 |
| P4 issues | 0 |
| API endpoints passing | 0 / 22 |
| Frontend pages loading | 0 / 14 |

*Update these numbers at the end of Sprint 12.*

---

*Last updated: April 3, 2026*  
*This is a living document — update it continuously during Sprint 12*
