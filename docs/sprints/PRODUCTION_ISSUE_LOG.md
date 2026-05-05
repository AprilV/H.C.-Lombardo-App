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

These were confirmed issues from earlier code review. Status below reflects verification as of Apr 27, 2026.

| # | Issue | File | Line | Severity | Status | Sprint |
|---|-------|------|------|----------|--------|--------|
| BUG-001 | /game-statistics routes to wrong component | frontend/src/App.js | ~58 | P2 | FIXED | S12 |
| BUG-002 | /matchup-analyzer routes to wrong component | frontend/src/App.js | ~59 | P2 | FIXED | S12 |
| BUG-003 | Hardcoded password 'aprilv120' fallback | api_server.py | ~77 | P1 | FIXED | S12 |
| BUG-004 | Hardcoded password 'aprilv120' fallback | api_routes_hcl.py | ~22 | P1 | FIXED | S12 |
| BUG-005 | Hardcoded password 'aprilv120' fallback | api_routes_live_scores.py | ~29 | P1 | FIXED | S12 |
| BUG-006 | 7+ DEBUG print statements in production | api_routes_live_scores.py | various | P3 | FIXED | S12 |
| BUG-007 | background_updater.py missing import | background_updater.py | — | P2 | FIXED | S12 |
| BUG-008 | train_xgb_winner.py uses hcl_test schema | ml/train_xgb_winner.py | 255 | P2 | OPEN | S14 |
| BUG-009 | Broken SQL WINDOW clause in spread training | ml/train_xgb_spread.py | 95-116 | P2 | OPEN | S14 |
| BUG-010 | EPA features loaded in SQL but not used in model | ml/train_xgb_spread.py | 174-181 | P3 | OPEN | S14 |
| BUG-011 | predict_ensemble.py TODO at line 338 (incomplete) | ml/predict_ensemble.py | 338 | P2 | OPEN | S14 |
| BUG-012 | Default season hardcoded as 2025 throughout backend | various | — | P2 | FIXED | S13 |
| BUG-013 | MLPredictionsRedesign.backup.js still in src/ | frontend/src/ | — | P4 | FIXED | S12 |

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
| NEW-001 | Data | 2025 games are incomplete (272 loaded; target with playoffs is ~285) | P1 | OPEN | S13 | Query result: MAX(season)=2025, season=2025 count=272 |
| NEW-002 | Data | 2025 team_game_stats incomplete for completed games | P1 | OPEN | S13 | DAT-6 rerun (Apr 27): completed games=272 -> expected rows=544, actual=468, missing=76 (all weeks now scored) |
| NEW-003 | Data Quality | 80 season-2025 team_game_stats rows have NULL epa_per_play | P2 | OPEN | S13 | DAT-6 audit: NULL EPA rows all on completed games (80) - blocks DAT-4 |
| NEW-004 | Data | public.teams is empty (0 rows) and standings sync target not populated | P1 | FIXED | S13 | Fixed Apr 27, 2026 in active DB (nfl_analytics): seeded via insert_teams.sql and synced standings via scripts/data_loading/update_public_teams_from_games.py; rows_updated=32 |
| NEW-005 | Data Quality | 34 season-2025 games had missing final scores | P2 | FIXED | S13 | Fixed Apr 27 via scripts/data_loading/backfill_missing_scores_from_espn.py (updates_applied=34); DAT-6 now reports games_missing_scores=0 |
| NEW-006 | Data Quality | Team abbreviation mismatch between sources (`LA` vs `LAR`) breaks strict joins | P2 | FIXED | S13 | Apr 27: centralized normalization in team_abbreviations.py and applied to core HCL/live-scores routes + standings/audit scripts. DAT-6 canonical checks now empty; API verifies LAR externally while querying LA-backed hcl data. |
| NEW-007 | Backend / Updater | live_data_updater.py fails continuous update cycle: missing root fetcher path (`multi_source_data_fetcher.py`) | P2 | OPEN | S14 | Observed May 4, 2026 in startup updater window: `[ERROR] Multi-source fetcher not found: C:\ReactGitEC2\IS330\H.C Lombardo App\multi_source_data_fetcher.py`. Current code checks `self.project_root / "multi_source_data_fetcher.py"` in live_data_updater.py line ~26. |
| NEW-008 | Dashboard / Logbook | log_watcher.py recursively tracks its own archive writes, creating a rapid `MODIFIED docs/devlog/archive/YYYY-MM-DD.json` loop and watcher thread crash (`OSError: [Errno 22] Invalid argument` while writing `archive/index.json`) | P2 | IN PROGRESS | S14 | Observed May 4, 2026 from live watcher output and traceback in log_watcher.py (`on_modified -> add_entry -> save_day -> update_index`). Local mitigation applied: exclude `docs/devlog/archive` from tracking, debounce duplicate events, and guard handler exceptions; requires watcher restart validation. |

---

## SPRINT ASSIGNMENT SUMMARY

*Fill this in at the end of Sprint 12 after all issues are logged.*

| Sprint | Issues Assigned |
|--------|----------------|
| Sprint 12 (immediate) | |
| Sprint 13 (Data & Clean) | NEW-001 through NEW-003 |
| Sprint 14 (ML Retrain) | BUG-008, BUG-009, BUG-010, BUG-011 |
| Sprint 15 (UI Polish) | All UI-* issues |
| Sprint 16 (Hardening) | Security, perf, monitoring |

---

## METRICS

| Metric | Count |
|--------|-------|
| Total issues logged | 21 |
| P1 issues | 3 |
| P2 issues | 9 |
| P3 issues | 1 |
| P4 issues | 0 |
| API endpoints passing | 0 / 22 |
| Frontend pages loading | 0 / 14 |

*Update these numbers at the end of Sprint 12.*

---

*Last updated: May 4, 2026*  
*This is a living document — update it continuously during Sprint 12*
