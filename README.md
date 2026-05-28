# H.C. Lombardo NFL Analytics App

**Complete Testing Environment** - Mirrors live production system on AWS Amplify + EC2

## Architecture

- **Frontend**: React → AWS Amplify (auto-deploy from GitHub)
- **Backend**: Flask API → EC2 (manual, approved deployments)  
- **Database**: PostgreSQL on EC2 localhost
- **Data Source**: NFLverse (free NFL play-by-play data)

## Project Structure

```
H.C Lombardo App/
├── frontend/              # React app
│   ├── src/              # Source code
│   ├── public/           # Static assets
│   └── build/            # Production build
│
├── docs/                  # All documentation
│   ├── ai_reference/     # AI assistant guides (READ THESE FIRST)
│   ├── deployment/       # Deployment guides
│   ├── sessions/         # Session references
│   └── sprints/          # Sprint documentation
│
├── scripts/               # Python scripts organized by purpose
│   ├── data_loading/     # Data ingestion & updates
│   ├── verification/     # Testing & verification
│   └── maintenance/      # Database maintenance
│
├── .github/workflows/     # GitHub Actions (auto-updates)
├── templates/             # Flask HTML templates
├── ml/                    # Machine learning models
└── [Root Python files]    # Core API files only
```

## Quick Start

### Local Development
```powershell
# Primary control commands (recommended)
python startup.py

# Stop all services
python shutdown.py

# Convenience wrappers (optional)
START-DEV.bat
STOP.bat
```

### Quick Health Check
```powershell
# Verify API + database connectivity
python health_check.py
```

Expected output includes successful database connectivity, and API/frontend readiness checks when those services are running.

### Testing Before Deployment
1. Make changes in local environment
2. Test thoroughly with `python startup.py` (or `START-DEV.bat`)
3. Open a pull request and review changes
4. Merge to `master`
5. Dashboard changes in `pmforge_dashboard/index.html` auto-publish to `gh-pages` via GitHub Actions

## Core Files

### Backend API (Flask)
- `api_server.py` - Main Flask application
- `api_routes_hcl.py` - Historical data endpoints
- `api_routes_ml.py` - ML prediction endpoints  
- `api_routes_live_scores.py` - Live scores (ESPN)
- `db_config.py` - Database configuration

### Data Loading
- `scripts/data_loading/ingest_historical_games.py` - Load NFL game data
- `scripts/data_loading/update_2025_with_epa.py` - Calculate EPA stats
- `scripts/data_loading/auto_update_service.py` - Continuous updates

### Documentation
- `README.md` - Public project overview and local run guidance
- `docs/deployment/DEPLOYMENT_GUIDE.md` - Deployment and environment notes
- `docs/ai_reference/ARCHITECTURE.md` - System architecture details
- `docs/sprints/` - Sprint evidence and delivery artifacts

## GitHub Actions

Manual production data update workflow (approval required):
1. Run the production workflow using `workflow_dispatch`
2. Pull latest approved code on EC2
3. Load selected season data into production schema (`hcl`)
4. Verify production counts/health before release sign-off

Release cadence guardrail:
1. Production releases are batched by ticket bundle only
2. Minimum bundle size is 3 TA tickets (3+ rule)
3. No per-subtask production pushes

## Database

PostgreSQL on EC2 localhost:
- Schema: `hcl` (historical data 1999-2025)
- 7,263 games, 14,398 team-game records
- 64 statistical metrics per game including EPA

## Important Notes

- **No separate production/test environments** - This IS the test environment
- **Production is live** on AWS Amplify + EC2
- **Always test locally before pushing to GitHub**
- **Read AI reference docs before making changes**

## Support

Program: Senior Capstone Project  
Student: April V. Sykes  
Advisor: Richard Becker  
Institution: Olympic College  
Term: Spring 2026 (April 6 – June 13)
