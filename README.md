# H.C. Lombardo NFL Analytics App

**Complete Testing Environment** - Mirrors live production system on AWS Amplify + EC2

## Architecture

- **Frontend**: React → AWS Amplify (auto-deploy from GitHub)
- **Backend**: Flask API → EC2 (auto-pull from GitHub)  
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
# Start development mode (React hot reload + Flask API)
START-DEV.bat

# Stop all services
STOP.bat
```

### Testing Before Deployment
1. Make changes in local environment
2. Test thoroughly with `START-DEV.bat`
3. Commit and push to GitHub
4. Changes auto-deploy to production

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

### Documentation (READ FIRST)
- `docs/ai_reference/READ_THIS_FIRST.md` - **START HERE** (AI behavior contracts)
- `docs/ai_reference/ARCHITECTURE.md` - Complete system architecture
- `docs/ai_reference/BEST_PRACTICES.md` - Development workflow
- `docs/ai_reference/NFL_SPREAD_BETTING_GUIDE.md` - Spread betting logic
- `docs/ai_reference/PREDICTION_TRACKING_SYSTEM.md` - ML prediction tracking
- `docs/ai_reference/QUICK_START_HCL.md` - Quick start guide

## GitHub Actions

Automated weekly data updates (Mondays 2 AM UTC):
1. SSH into EC2
2. Update Python packages (nfl-data-py)
3. Load latest NFL game data
4. Calculate EPA and advanced stats

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

Class: IS330 - Database & Application Development  
Student: April V. Sykes  
Instructor: Dr. Foster  
Institution: Olympic College
