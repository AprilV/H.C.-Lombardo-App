# H.C. Lombardo NFL Analytics App — Claude Context

## Project Overview
NFL analytics web app — senior capstone project at Olympic College.
- **Student**: April V. Sykes
- **Advisor**: Richard Becker
- **Program**: Senior Capstone (self-directed, no in-class instruction; deliverables are performance reports)
- **Term**: Spring 2026 (April 6 – June 13)

## Architecture
- **Frontend**: React (port 3000) → deployed to AWS Amplify (auto-deploy from GitHub)
- **Backend**: Flask API (port 5000) → deployed to EC2 (auto-pull from GitHub)
- **Database**: PostgreSQL on EC2 localhost, schema `hcl`, ~7,263 games (1999–2025)
- **Data Source**: NFLverse (play-by-play), ESPN API (live scores/standings)

## Key Files

### Backend
- `api_server.py` — main Flask app
- `api_routes_hcl.py` — historical data endpoints
- `api_routes_ml.py` — ML prediction endpoints
- `api_routes_live_scores.py` — live scores (ESPN)
- `db_config.py` — database configuration
- `background_updater.py` — background service (team standings only; game data already complete)

### Frontend (`frontend/src/`)
- `App.js` — main router
- `Analytics.js`, `MLPredictions.js`, `MLPredictionsRedesign.js` — analytics/ML views
- `MatchupAnalyzer.js`, `TeamComparison.js`, `TeamDetail.js`, `TeamStats.js` — team tools
- `LiveScores.js`, `GameStatistics.js`, `HistoricalData.js` — game data views
- `ModelPerformance.js` — ML model tracking
- `Admin.js` — admin panel

### ML
- `ml/` directory contains ML models

## Local Development
```bash
# Start dev environment (React hot reload + Flask API)
START-DEV.bat

# Stop all services
STOP.bat
```

## Deployment
- Push to GitHub → auto-deploys frontend to AWS Amplify, backend to EC2
- Always test locally with `START-DEV.bat` before pushing
- No separate staging environment — local IS the test environment

## Database
- PostgreSQL 18 at `localhost:5432`
- Local dev DB: `nfl_analytics`
- Production schema: `hcl`
- 7,263 games, 14,398 team-game records, 64 stats per game including EPA

## REQUIRED: Read These Before Any Work
These documents define mandatory AI behavior for this project. Read them in order before doing anything:

1. `docs/ai_reference/AI_EXECUTION_CONTRACT.md` — absolute rules, no exceptions
2. `docs/ai_reference/READ_THIS_FIRST.md` — orientation and failure conditions
3. `docs/ai_reference/BEST_PRACTICES.md` — coding and development standards
4. `docs/ai_reference/AI_VIOLATION_CHECKLIST.md` — how to identify AI failures

## Additional Reference Docs
- `docs/ai_reference/ARCHITECTURE.md` — full system architecture
- `docs/ai_reference/NFL_SPREAD_BETTING_GUIDE.md` — spread betting logic
- `docs/ai_reference/PREDICTION_TRACKING_SYSTEM.md` — ML prediction tracking
- `docs/ai_reference/TOPOLOGY.md` — system topology

## Current State (as of March 2026)
- Many frontend components have uncommitted changes (Analytics, MLPredictions, MatchupAnalyzer, etc.)
- Background updater simplified to team standings only (game data is complete for the season)
- NFLverse integration fixed with inline implementation and error handling
- Test environment guide and setup scripts exist but are untracked
