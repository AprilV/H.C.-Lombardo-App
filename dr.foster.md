# H.C. Lombardo NFL Analytics Platform - Dr. Foster Dashboard

**Student:** April V  
**Course:** IS330  
**Last Updated:** November 11, 2025  
**Status:** Weeks 7-8 Complete ✅ (Nov 2-11, 2025)  
**GitHub:** https://github.com/AprilV/H.C.-Lombardo-App

---

## 📊 WEEKS 7-8: MACHINE LEARNING & ADVANCED ANALYTICS (November 2-11, 2025)

### Week 7: Sprint 9 - Machine Learning Neural Network (Nov 6, 2025) ✅

####  November 6: Neural Network Training & Deployment - COMPLETE
- **3-Layer Deep Neural Network** for game outcome prediction
- **Architecture**: 41 inputs → 128 → 64 → 32 → 1 output (binary classification)
- **Total Parameters**: 20,097 learnable weights and biases
- **Training Data**: 5,477 games (1999-2023) with rolling features
- **Validation**: 267 games (2024 season)
- **Test Set**: 128 games (2025 season)
- **Final Accuracy**: 65.55% test accuracy (beats Vegas 52-55% baseline)
- **Training Time**: 2.7 seconds on Windows CPU
- **Data Leakage Fixed**: V1 (99.8% - leaked) → V2 (65.55% - proper rolling windows)

**Feature Engineering (41 Features):**
1. **Season Statistics (8)**: PPG, EPA/play, success rate, yards/play, completion %, total yards, turnovers, 3rd down %
2. **Recent Form (8)**: L3/L5 EPA, success rate, PPG, yards/play
3. **Matchup Differentials (16)**: Home vs away differences, L3/L5 momentum indicators
4. **Vegas Lines (9)**: Spread, total, moneylines, implied probabilities, line movement, public %, sharp money

**Production Deployment:**
- **Backend**: Flask API with 6 endpoints (`/api/ml/predict-week`, `/predict-upcoming`, `/predict-game`, `/model-info`, `/explain`, `/features`)
- **Frontend**: React component with 4 tabs (Predictions, Upcoming Games, Model Info, Legend)
- **Database**: PostgreSQL HCL schema integration
- **Weekly Workflow**: Monday predictions, live game tracking, Wednesday updates

**Status:** Production deployed and operational ✅

---

### Week 8: Sprint 10 - Historical Data & 3D Visualization (Nov 7-11, 2025) ✅

#### 📊 November 7-11: Historical Data Redesign
- **Spreadsheet-Style Interface** with three interactive dropdowns:
  - **Team Selector**: All 32 NFL teams
  - **Season Selector**: 1999-2025 (27 years of data)
  - **Stat Category Selector**: 8 categories (All, Offense, Defense, Passing, Rushing, Advanced, Efficiency, Scoring)
- **Professional Blue Gradient Theme** matching ML Predictions page
- **3-Column Table Layout**: Statistic | Value | Category
- **41 Total Statistics** across all categories
- **Team Info Banner**: Displays team name and selected season
- **Responsive Design**: Optimized for desktop and mobile

#### 🧠 November 7-11: Dr. Foster Dashboard ML Tab
- **Interactive 3D Neural Network Visualization** using Three.js
- **5 Layers Rendered**: Input (41), Hidden1 (128), Hidden2 (64), Hidden3 (32), Output (1)
- **Color-Coded Neurons**: Blue (input), Green (H1), Purple (H2), Pink (H3), Yellow (output)
- **Animated Neurons**: Pulsing effects with emissive materials
- **Connection Lines**: Semi-transparent connections between layers
- **OrbitControls**: Mouse drag to rotate, scroll to zoom, auto-rotate enabled
- **Comprehensive Documentation**: 9 sections covering problem, data, features, architecture, training, deployment
- **Educational Content**: Data leakage prevention, V1 vs V2 comparison, academic learning outcomes

**Status:** Historical Data complete ✅ | Dashboard 3D visualization complete ✅

---

## 📚 PREVIOUS WEEKS SUMMARY

### Week 6 Highlights (Oct 28 - Nov 1)

#### 🎨 November 1: Premium Gold Branding
- **Gold Shimmer Effect** on H.C. LOMBARDO header
- Italian quote: "È FOTTUTAMENTE INCREDIBILE!"
- 9-stop gradient, 4.5s right-to-left animation
- Realistic metallic look (no glow)
- Production build: 215.71 kB JS, 6.91 kB CSS

#### 📊 October 28-31: Historical Database Infrastructure (Sprint 8)
- **950+ games** loaded (2022-2025 seasons)
- **1,900+ team-game records** with 47+ metrics each
- Complete HCL schema in Third Normal Form
- Automated data loader (`ingest_historical_games.py`)
- Comprehensive testing infrastructure

### Week 5 Highlights (Oct 21-27)

#### 📅 October 26-27: React Frontend Integration (Sprint 7)
- **HistoricalData.jsx** - 32-team grid view with stats
- **TeamDetail.jsx** - Individual team analysis with Chart.js graphs
- React Router navigation (/historical, /team/:abbr)
- CORS-enabled Flask-React communication

#### 📅 October 22: Historical Data API (Sprint 6)
- Flask REST API with 4 HCL endpoints
- 100% test coverage (6/6 tests passed)
- Blueprint pattern integration
- JSON responses with proper HTTP codes

#### 📅 October 21-22: Database Design (Sprint 5)
- HCL schema designed in 3NF
- 3 core tables (games, team_game_stats, team_season_stats)
- 3 database views for efficient querying
- 2025 Week 7 test data loaded

### Week 4 Highlights (Oct 14-20)
- Three-tier architecture planning
- Infrastructure setup and testing
- Documentation framework established

---

## Sprint 9: Neural Network Visual Schematic

### Architecture Overview

Our neural network uses a **deep feed-forward architecture** with 3 hidden layers. Here's how data flows from inputs to prediction:

```
INPUT LAYER (75 features)
┌─────────────────────────────────┐
│  Basic Stats (51 features)      │
│  - Points, Touchdowns, Yards    │
│  - Turnovers, Field Goals       │
│  - Passing, Rushing, Penalties  │
│                                  │
│  EPA Metrics (13 features)      │
│  - EPA per play                 │
│  - Success rate                 │
│  - Pass EPA, Rush EPA           │
│  - WPA, CPOE                    │
│                                  │
│  Context (11 features)          │
│  - Season, Week, is_home        │
│  - Betting lines (spread/total) │
│  - Moneylines                   │
└──────────────┬──────────────────┘
               │
               │ 75 connections to each hidden neuron
               ▼
HIDDEN LAYER 1 (128 neurons)
┌───────────────────────────────────────────────────────────┐
│  [N1] [N2] [N3] [N4] ... [N124] [N125] [N126] [N127] [N128] │
│   ●    ●    ●    ●   ...   ●      ●      ●      ●      ●    │
└───────────────────────┬───────────────────────────────────┘
                        │ ReLU Activation
                        │ 9,728 parameters (75×128 + 128)
                        ▼
HIDDEN LAYER 2 (64 neurons)
┌─────────────────────────────────────────────┐
│  [N1] [N2] [N3] ... [N62] [N63] [N64]      │
│   ●    ●    ●   ...   ●     ●     ●        │
└──────────────────┬──────────────────────────┘
                   │ ReLU Activation
                   │ 8,256 parameters (128×64 + 64)
                   ▼
HIDDEN LAYER 3 (32 neurons)
┌───────────────────────────────────┐
│  [N1] [N2] ... [N31] [N32]       │
│   ●    ●   ...   ●     ●         │
└────────────┬──────────────────────┘
             │ ReLU Activation
             │ 2,080 parameters (64×32 + 32)
             ▼
OUTPUT LAYER (1 neuron)
┌────────────────────────┐
│   Win Probability      │
│         ●              │
│      (0.0 - 1.0)       │
└────────────────────────┘
   Sigmoid Activation
   33 parameters (32×1 + 1)

TOTAL: 20,097 parameters
```

### How a Single Neuron Works

**Example: Neuron in Hidden Layer 1**

```
Inputs from previous layer (75 features):
┌─────────┬─────────┬─────────┬─────┬─────────┐
│  x₁     │  x₂     │  x₃     │ ... │  x₇₅    │
│ 0.52    │ -0.31   │  0.88   │ ... │  0.15   │
└─────────┴─────────┴─────────┴─────┴─────────┘
      ↓         ↓         ↓              ↓
    × w₁      × w₂      × w₃           × w₇₅
      ↓         ↓         ↓              ↓
    0.35      0.06      0.72           0.08
      └─────────┴─────────┴─────────────┘
                    │
                    ▼
            Weighted Sum + Bias
         z = (Σ xᵢ × wᵢ) + b
         z = 1.23 + 0.1 = 1.33
                    │
                    ▼
            ReLU Activation
         output = max(0, z)
         output = 1.33
                    │
                    ▼
         Passes to next layer
```

### Data Flow Example

**Predicting: Kansas City Chiefs @ Buffalo Bills (Week 11, 2025)**

```
INPUT FEATURES (sample):
┌────────────────────────────┬────────┐
│ is_home                    │   1    │ ← Home team advantage
│ season                     │ 2025   │
│ week                       │  11    │
│ epa_per_play (Chiefs)      │ 0.18   │ ← Strong offense
│ success_rate (Chiefs)      │ 0.48   │
│ epa_per_play (Bills)       │ 0.15   │
│ success_rate (Bills)       │ 0.45   │
│ spread_line                │ -3.5   │ ← Chiefs favored
│ total_line                 │ 47.5   │
│ ... (66 more features)     │  ...   │
└────────────────────────────┴────────┘
        │
        ▼
LAYER 1: Learns basic patterns
  Neuron 1: "Home team scoring"     → 0.82
  Neuron 2: "EPA advantage"         → 0.91
  Neuron 3: "Betting line strength" → 0.75
  ... (125 more neurons)
        │
        ▼
LAYER 2: Combines patterns
  Neuron 1: "Home + Strong Offense" → 0.88
  Neuron 2: "EPA + Betting Odds"    → 0.79
  ... (62 more neurons)
        │
        ▼
LAYER 3: High-level abstractions
  Neuron 1: "Dominant team at home" → 0.85
  Neuron 2: "Close game factors"    → 0.42
  ... (30 more neurons)
        │
        ▼
OUTPUT: Win Probability
  Sigmoid(weighted_sum) = 0.67
        │
        ▼
  PREDICTION: 67% chance Chiefs win
```

### Training Process Visualization

**How the Network Learns**

```
EPOCH 1 (First Pass):
──────────────────────────────────────────
Input: [Chiefs game stats]
Prediction: 0.52 (52% win probability)
Actual: 1 (Chiefs won)
Error: 0.52 - 1.00 = -0.48 (underpredicted)

Backpropagation:
   Output Layer ← Calculate error gradient
        ↓
   Hidden Layer 3 ← Propagate error backward
        ↓
   Hidden Layer 2 ← Adjust weights
        ↓
   Hidden Layer 1 ← Update all 20,097 parameters

Weight Update Example:
   Old weight: 0.500
   Gradient: 0.200 (error contribution)
   Learning rate: 0.001
   New weight = 0.500 - (0.001 × 0.200)
              = 0.4998 (slightly adjusted)

──────────────────────────────────────────
EPOCH 50 (After Learning):
Input: [Chiefs game stats] (same game)
Prediction: 0.68 (68% win probability)
Actual: 1 (Chiefs won)
Error: 0.68 - 1.00 = -0.32 (better!)
```

### Sample Weighting Strategy

**Why Recent Games Matter More**

```
TRAINING DATA DISTRIBUTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Era: 2020-2023 (Modern NFL)
Games: 2,136
Weight: 1.0 ████████████████████ 100%
Influence: 2,136 effective games

Era: 2010-2019 (Recent NFL)
Games: 5,340
Weight: 0.6 ████████████ 60%
Influence: 3,204 effective games

Era: 1999-2009 (Historical NFL)
Games: 5,886
Weight: 0.2 ████ 20%
Influence: 1,177 effective games

Total: 13,362 games → 5,898 effective
```

**Impact on Training:**
```
If model makes same error on games from different eras:

2023 Game Error: 0.3 × 1.0 = 0.30 penalty
2015 Game Error: 0.3 × 0.6 = 0.18 penalty
2003 Game Error: 0.3 × 0.2 = 0.06 penalty

Model learns to prioritize modern NFL patterns!
```

### Performance Expectations

**Comparison to Industry Standards**

```
                    Accuracy Target
                    ├──────────┤
Random Guessing     50%   ░░░░░░░░░░
                          │
Coin Flip           50%   ░░░░░░░░░░
                          │
Vegas Lines         52-55% ████████████
                          │
Best Models         57-60% ████████████████
                          │
Our Target (EPA)    60-65% ████████████████████
                          │
Perfect Prediction  100%  (impossible due to chaos)
```

**Why 60-65% is Excellent:**
- NFL has parity by design (salary cap, draft order)
- Injuries and weather aren't in our data
- "Any Given Sunday" - upsets happen
- Human factors (coaching, motivation) are unpredictable

### Academic Concepts Demonstrated

✅ **Artificial Neural Networks** - Inspired by biological neurons  
✅ **Deep Learning** - Multiple hidden layers enable hierarchical learning  
✅ **Backpropagation** - Gradient-based optimization algorithm  
✅ **Activation Functions** - Non-linear transformations (ReLU, Sigmoid)  
✅ **Regularization** - Sample weighting, early stopping, L2 penalty  
✅ **Supervised Learning** - Training with labeled data (win/loss)  
✅ **Train/Validation/Test Split** - Proper evaluation methodology  
✅ **Feature Engineering** - Selecting and preparing 75 input features  

---

## Project OverviewThe H.C. Lombardo NFL Analytics Platform is a comprehensive sports analytics application designed for professional NFL gambling analysis. Named after H.C. Lombardo, a professional gambler who is developing proprietary betting formulas, this platform serves as the technical infrastructure to support data-driven sports betting decisions.



---**Core Purpose:**

This application collects, processes, and analyzes extensive NFL statistical data to generate "honest lines" for NFL games - mathematical predictions that can be compared against Vegas betting lines to identify value betting opportunities.

## Project Overview

**Target User:**

**What This App Is:**Professional gamblers and serious sports bettors who need:

The H.C. Lombardo NFL Analytics Platform is a modern, full-stack sports analytics application designed for professional NFL data analysis. Built with React and Flask, it provides comprehensive historical game data, advanced metrics, and interactive visualizations for serious sports analysis.- Comprehensive historical and current NFL statistics

- Advanced analytics (EPA, Success Rate, yards per play)

**Core Purpose:**- Historical game-by-game performance tracking

- Collect and store historical NFL game data with advanced metrics- Interactive data visualization with Chart.js

- Provide interactive visualizations of team performance over time- Automated data collection and processing

- Enable game-by-game analysis with EPA, Success Rate, and efficiency metrics- Custom formula implementation capabilities

- Support data-driven decision making with clean, professional UI- Performance tracking and analysis



**Target User:****Key Features:**

Analysts and sports enthusiasts who need:1. **Comprehensive Database** - PostgreSQL-powered storage with HCL historical schema containing 2025 season data (Weeks 1-7, 108 games, 216 team-game records)

- Historical NFL game data (2025 season)2. **Historical Data System** - Complete game-by-game tracking with advanced metrics (EPA/Play, Success Rate, 3rd Down %, Red Zone Efficiency)

- Advanced analytics (EPA/Play, Success Rate, Yards/Play, efficiency metrics)3. **Modern React Frontend** - Single Page Application with responsive design, interactive charts, team detail pages

- Interactive charts showing performance trends4. **RESTful API Architecture** - Flask backend with 6+ endpoints serving JSON data to React frontend

- Team-by-team season overviews5. **Real-time Data Updates** - Automated refresh cycles with live timestamp tracking

- Game-by-game detailed statistics6. **Professional Logging** - Complete activity tracking for debugging and performance analysis

7. **Testbed Environment** - Safe development space for testing new features and data sources

---

**Technical Architecture:**

## Current Status: Sprint 7 Complete ✅- **Frontend:** React 18.2.0 with React Router, Chart.js for visualization

- **Backend:** Python Flask REST API with CORS support

### What's Working Right Now:- **Database:** PostgreSQL 15+ with HCL schema (historical data) and production schema (current stats)

- ✅ **React Frontend** - Modern SPA on port 3000- **Data Sources:** nflverse (nfl-data-py) for historical data, TeamRankings.com for live updates

- ✅ **Flask REST API** - 6+ endpoints on port 5000- **Infrastructure:** Three-tier architecture, automated refresh cycles, comprehensive logging, version control

- ✅ **PostgreSQL Database** - HCL schema with 108 games (2025 Weeks 1-7)

- ✅ **Historical Data Tab** - Grid view of all 32 teams with stats**Development Philosophy:**

- ✅ **Team Detail Pages** - Individual team pages with Chart.js graphsBuilt with professional gambling in mind - reliability, accuracy, and comprehensive data coverage are paramount. The platform is designed to handle the rigorous demands of daily betting analysis while providing the flexibility to implement and test new statistical approaches. All development follows rigorous testbed methodology before production deployment.

- ✅ **Team Stats Page** - Dropdown selection with current season data

- ✅ **CORS Enabled** - Full frontend-backend communication**Academic Context:**

- ✅ **Live Timestamps** - Accurate data freshness indicatorsDeveloped as part of IS330 coursework to demonstrate database design (3NF normalization, view creation), web development (React SPA, REST APIs), API integration (nflverse, web scraping), data visualization (Chart.js), and full-stack application architecture in a real-world application scenario.



------



## Sprint Timeline# H.C. Lombardo NFL Analytics - Dr. Foster Assignment



### 📅 Sprint 5: Database Design & Historical Schema (October 21-22, 2025)**Student:** April V  

**Course:** IS330  

**Goal:** Create scalable database schema for historical NFL data storage**Date:** October 8, 2025  

**GitHub:** https://github.com/AprilV/H.C.-Lombardo-App

**Accomplishments:**

- ✅ Designed HCL (Historical Competitive League) schema in Third Normal Form (3NF)---

- ✅ Created three core tables:

  - `hcl.games` - Game metadata (game_id, week, season, teams, scores, date, location)# Weeks 2-4: Database Migration & Live Data Integration

  - `hcl.team_game_stats` - Team performance per game (47 advanced metrics)

  - `hcl.team_season_stats` - Season aggregates (deprecated in favor of views)**Latest Update:** October 9, 2025  

- ✅ Built three database views for efficient querying:**Student:** April V

  - `v_team_season_stats` - Aggregated season statistics per team

  - `v_team_game_details` - Game-level details with opponent info### Major Upgrades Completed ✅

  - `v_team_weekly_trends` - Rolling averages (L3, L5 games)

- ✅ Loaded 2025 Week 7 test data (15 games, 30 team-game records)## October 9, 2025 - Production Three-Tier Architecture

- ✅ Validated schema with 7-step SQL verification process

#### 1. Production Three-Tier Architecture ✅

**Technical Details:****Implementation Date:** October 9, 2025

- Database: PostgreSQL 15+ 

- Schema: `hcl` (separate from production `public` schema)**What We Built:**

- Normalization: 3NF (eliminates data redundancy)Professional-grade separation of concerns using industry-standard three-tier architecture:

- Advanced Metrics: EPA per play, Success Rate, 3rd Down %, Red Zone Efficiency, Yards/Play, Turnovers- **Presentation Layer:** React frontend (modern UI framework)

- Views: Dynamic aggregation replacing static aggregate tables- **Application Layer:** Flask REST API (business logic and routing)

- **Data Layer:** PostgreSQL database (persistent storage)

**Files Created:**

- `testbed/schema/hcl_schema.sql` - Database schema definition**Why This Matters:**

- `testbed/nflverse_data_loader.py` - Data loader using nfl-data-py library- Each tier can be scaled independently

- `testbed/validate_database.sql` - 7-step validation queries- Frontend and backend can be developed separately

- `HISTORICAL_DATA_STORAGE_PLAN.md` - Complete documentation- Industry-standard approach used by major companies

- Enables future mobile app development (same API)

**Why This Matters:**- Better security (database never exposed to frontend)

- Proper 3NF design prevents data inconsistencies- Easier testing and maintenance

- Views allow flexible querying without data duplication

- Scalable to multiple seasons (2022-2024 and beyond)**Files Created:**

- Foundation for all historical analytics features- `api_server.py` - Production Flask REST API server

- `frontend/` - Complete React application with npm dependencies

---- `frontend/package.json` - React configuration and dependencies

- `frontend/src/App.js` - Main React component

### 📅 Sprint 6: Historical Data API (October 22, 2025)- `frontend/src/App.css` - Production styling with gradients

- `PRODUCTION_DEPLOYMENT.md` - Complete deployment documentation

**Goal:** Build REST API layer to query historical data- `README.md` - Project overview and quick start guide



**Accomplishments:****Testing Methodology:**

- ✅ Created Flask REST API with 4 endpoints:- Applied slow, step-by-step verification process

  - `GET /api/hcl/teams` - List all teams with season stats- Each component tested before moving to next step

  - `GET /api/hcl/teams/<abbr>` - Individual team season overview- 10 verification steps all passed before completion

  - `GET /api/hcl/teams/<abbr>/games` - Game-by-game history- Same rigorous approach used in testbed environment

  - `GET /api/games?season=X&week=Y` - All games for specific week

- ✅ Integrated with HCL database views**Production URLs:**

- ✅ Built comprehensive test suite (6/6 tests passed)- Frontend: http://localhost:3000 (React UI)

- ✅ Validated API responses with sample queries- API: http://127.0.0.1:5000 (Flask REST endpoints)

- ✅ Prepared API for frontend integration- Database: localhost:5432 (PostgreSQL)



**Technical Details:**### Current Architecture: Three-Tier Production System

- Framework: Flask 3.0+ with flask-cors

- Database: RealDictCursor for JSON-friendly responses```

- Test Coverage: 100% (all endpoints tested)                USER INTERFACE

- Response Format: JSON with proper HTTP status codes┌───────────────────────────────────────────────────┐

│         React Frontend (Port 3000)                │

**Files Created:**│         frontend/                                 │

- `testbed/api_routes_hcl.py` - Flask blueprint with 4 endpoints (500+ lines)│  • Modern UI with React 18.2.0                    │

- `testbed/test_api_endpoints.py` - Automated test suite (277 lines)│  • Displays all 32 NFL teams                      │

- `SPRINT_6_COMPLETE.md` - Sprint documentation│  • Real-time status monitoring                    │

│  • Professional gradient styling                  │

**API Examples:**│  • Responsive card-based layout                   │

```bash└─────────────────┬─────────────────────────────────┘

# Get all teams                  │

GET /api/hcl/teams?season=2025                  ↕ HTTP Request/Response (JSON)

Response: {"teams": [32 teams with stats], "count": 32}                  │ Request: GET /api/teams

                  │ Response: {"teams": [...]}

# Get Dallas Cowboys overview                    │

GET /api/hcl/teams/DAL?season=2025┌─────────────────┴─────────────────────────────────┐

Response: {"team": "DAL", "wins": 3, "losses": 4, "ppg": 31.7, ...}│         Flask REST API (Port 5000)                │

│         api_server.py                             │

# Get Cowboys game history│  • REST endpoints for data access                 │

GET /api/hcl/teams/DAL/games?season=2025│  • CORS enabled for React communication           │

Response: {"games": [7 games with all stats]}│  • Business logic and validation                  │

```│  • Integrated logging system                      │

│  • Error handling and status monitoring           │

**Why This Matters:**│                                                    │

- Clean separation between data layer and presentation layer│  Endpoints:                                        │

- RESTful design enables multiple frontend options (web, mobile)│    GET /              - Welcome message           │

- Comprehensive testing ensures reliability│    GET /health        - System health check       │

- Blueprint pattern allows easy integration into main app│    GET /api/teams     - All teams data            │

│    GET /api/teams/count - Team count              │

---│    GET /api/teams/<abbr> - Single team            │

└─────────────────┬─────────────────────────────────┘

### 📅 Sprint 7: React Frontend Integration (October 26-27, 2025)                  │

                  ↕ SQL Query/Result

**Goal:** Build modern React frontend with interactive visualizations                  │ Query: SELECT * FROM teams

                  │ Result: 32 rows returned

**Accomplishments:**                  │

┌─────────────────┴─────────────────────────────────┐

#### Phase 1: Historical Data Components ✅│      PostgreSQL Database (Port 5432)              │

- ✅ Created `HistoricalData.jsx` - 32-team grid view component│      nfl_analytics database                       │

  - Displays all teams with key stats (Wins-Losses, PPG, EPA/Play, Success Rate, Yards/Play)│  • 32 NFL teams with complete stats               │

  - Color-coded stats (green for good, red for bad)│  • Real-time PPG and PA data                      │

  - Click-to-navigate to team details│  • Update metadata tracking                       │

  - Responsive grid layout (1-4 columns based on screen size)│  • Persistent data storage                        │

  - Fetches from `/api/hcl/teams` endpoint│  • Enterprise-grade RDBMS                         │

└───────────────────────────────────────────────────┘

- ✅ Created `TeamDetail.jsx` - Individual team analysis page                  ▲

  - Season overview with 8 stat boxes (Wins, Losses, PPG, EPA, Success Rate, Yards/Play, 3rd Down %, Red Zone %)                  │

  - Chart.js line graph showing EPA/Play and Success Rate trends over weeks                  │ Data Updates

  - Game history table with all games (Week, Opponent, Result, Score, Stats)┌─────────────────┴─────────────────────────────────┐

  - Back button navigation│      Data Refresh Layer (scrape_teamrankings)     │

  - Fetches from `/api/hcl/teams/<abbr>` and `/api/hcl/teams/<abbr>/games`│  • Scrapes TeamRankings.com                       │

│  • Combines PPG + PA data                         │

- ✅ Installed Chart.js dependencies:│  • Updates PostgreSQL via SQL                     │

  - `chart.js@4.4.0` - Core charting library│  • Logs scraping performance and results          │

  - `react-chartjs-2@5.2.0` - React wrapper for Chart.js└───────────────────────────────────────────────────┘



#### Phase 2: Routing & Navigation ✅SUPPORTING INFRASTRUCTURE

- ✅ Added React Router routes:┌───────────────────────────────────────────────────┐

  - `/` - Homepage│           Logging System (logs/)                  │

  - `/team-stats` - Team Stats page (existing)│  • Daily rotated log files                        │

  - `/historical` - Historical Data grid view (NEW)│  • Component-based activity tracking              │

  - `/team/:teamAbbr` - Team Detail page (NEW)│  • Built-in viewers and analysis tools            │

│  • Complete audit trail of all operations         │

- ✅ Updated `SideMenu.jsx` with Historical Data link (📜 icon)└───────────────────────────────────────────────────┘

```

#### Phase 3: Production Integration ✅

- ✅ Integrated HCL API blueprint into main `app.py`**Communication Flow:**

  - Registered blueprint with `/api/hcl` prefix1. **User → React**: User opens browser at http://localhost:3000

  - All 3 HCL endpoints accessible in production2. **React → Flask API**: `fetch('http://localhost:5000/api/teams')`

3. **Flask → PostgreSQL**: `cursor.execute("SELECT * FROM teams")`

- ✅ Enabled CORS for React-Flask communication4. **PostgreSQL → Flask**: Returns 32 teams with all statistics

  - Added `flask-cors` package5. **Flask → React**: Sends JSON response `{"teams": [...]}`

  - Configured CORS(app) for localhost:30006. **React → User**: Displays teams in beautiful card-based UI



- ✅ Fixed missing API endpoints:**Key Benefits of This Architecture:**

  - Added `/health` endpoint for status checks- ✅ Separation of concerns (UI, logic, data)

  - Added `/api/teams` endpoint for team list- ✅ Scalable (can add more API servers)

  - Added `/api/teams/<abbreviation>` for team details- ✅ Testable (each tier tested independently)

  - Fixed response structures to match frontend expectations- ✅ Maintainable (changes in one tier don't affect others)

- ✅ Secure (database credentials only in API server)

- ✅ Fixed data parsing issues:- ✅ Future-ready (can add mobile apps using same API)

  - Updated TeamStats.js to extract nested `team` object

  - Fixed timestamp to show current time (NOW() in SQL)---



#### Phase 4: Testing & Validation ✅## October 9, 2025 - DHCP-Inspired Port Management System

- ✅ Built React production bundle (`npm run build`)

- ✅ Started both servers (Flask on 5000, React on 3000)#### Intelligent Port Management (April's Innovation) ✅

- ✅ Tested all pages:**Problem Identified:**

  - Homepage loads ✅During development, frequent "port already in use" errors disrupted workflow. Flask would fail to start if port 5000 was busy, React wouldn't start if port 3000 was occupied. Manual troubleshooting required checking ports, killing processes, and restarting - time-consuming and frustrating.

  - Team Stats page with dropdown populated ✅

  - Historical Data grid with 32 teams ✅**Solution Concept:**

  - Team Detail pages with charts ✅Applied **DHCP (Dynamic Host Configuration Protocol) principles** from networking to application-level port management. Just as DHCP automatically assigns IP addresses from a pool to avoid conflicts, this system automatically assigns ports from a managed range.

- ✅ Verified all API endpoints returning correct data

- ✅ Confirmed CORS working (no browser errors)**April's Innovation:**

This approach adapts enterprise-grade networking concepts (DHCP) to solve a development environment challenge. While dynamic port allocation exists in production systems (Docker, Kubernetes), applying DHCP-style management to Flask development environments is an original implementation that bridges networking theory with practical software engineering.

**Technical Details:**

- Frontend: React 18.2.0, React Router 7.9.4, Chart.js 4.4.0**Technical Implementation:**

- Backend: Flask with CORS, 6 production endpoints

- Database: PostgreSQL with HCL schema (108 games, 216 team-game records)```

- Data: 2025 NFL season Weeks 1-7DHCP Network Management          →    Port Management (Our Solution)

- Styling: Responsive CSS with gradients, card layouts, hover effects═══════════════════════════════════════════════════════════════════

IP Address Pool: 192.168.1.100-200    Port Range: 5000-5010

**Files Created/Modified:**Client requests IP address            Service requests port number

- `frontend/src/HistoricalData.js` - Team grid component (NEW)DHCP server assigns available IP      PortManager assigns available port

- `frontend/src/HistoricalData.css` - Responsive styling (NEW)Lease tracking (MAC → IP)             Service mapping (flask_api → 5000)

- `frontend/src/TeamDetail.js` - Team analysis component (NEW)Address conflict detection            Port conflict detection

- `frontend/src/TeamDetail.css` - Component styling (NEW)Automatic IP renewal                  Port persistence across restarts

- `frontend/src/App.js` - Added new routes (MODIFIED)DHCP reservation (static mapping)     Preferred port assignment

- `frontend/src/SideMenu.js` - Added Historical Data link (MODIFIED)```

- `frontend/src/TeamStats.js` - Fixed data parsing (MODIFIED)

- `frontend/package.json` - Added Chart.js dependencies (MODIFIED)**Core Components:**

- `app.py` - Integrated HCL blueprint, added endpoints, enabled CORS (MODIFIED)

- `api_routes_hcl.py` - HCL API blueprint (INTEGRATED)1. **Port Availability Detection** (Networking Layer)

   - Uses TCP socket binding test (`socket.bind()`)

**Why This Matters:**   - Checks for `EADDRINUSE` (Address Already In Use) error

- Modern React SPA provides smooth user experience   - Same mechanism the OS uses internally

- Chart.js enables professional data visualization   - Detects both managed and external port conflicts

- Component-based architecture is maintainable and scalable

- Responsive design works on desktop, tablet, mobile2. **Port Range Allocation** (DHCP Pool)

- Full-stack integration demonstrates complete web development skills   - Reserved range: 5000-5010 (11 ports)

   - Configurable like DHCP scopes

---   - Prevents conflicts with system ports (<1024)

   - Avoids ephemeral port range (49152-65535)

## Current Architecture: Modern Three-Tier System

3. **Intelligent Assignment Algorithm**

```   ```python

┌─────────────────────────────────────────────────────────────┐   Strategy (similar to DHCP):

│                    PRESENTATION LAYER                        │   1. Try preferred port (like DHCP reservation)

│              React Frontend (Port 3000)                      │   2. Try last successfully used port (like lease renewal)

│                                                              │   3. Scan range for first available (like DHCP pool allocation)

│  Pages:                                                      │   4. Fail gracefully if all ports busy (like DHCP exhaustion)

│    • Homepage (/)                                            │   ```

│    • Team Stats (/team-stats)                               │

│    • Historical Data (/historical) ← NEW!                   │4. **Service Registration** (Like DNS + DHCP)

│    • Team Detail (/team/:abbr) ← NEW!                       │   - Maps services to ports: `flask_api → 5000`

│                                                              │   - Persists configuration in `.port_config.json`

│  Components:                                                 │   - Tracks port usage across application restarts

│    • SideMenu - Navigation with hamburger menu              │   - Enables consistent port assignment

│    • Homepage - Landing page                                │

│    • TeamStats - Team selection dropdown                    │5. **Conflict Detection & Diagnostics**

│    • HistoricalData - 32-team grid ← NEW!                   │   - Identifies external services (React on 3000, PostgreSQL on 5432)

│    • TeamDetail - Charts + game history ← NEW!              │   - Detects ports in use within managed range

│                                                              │   - Provides `/port-status` API endpoint for monitoring

│  Libraries:                                                  │   - Real-time diagnostics similar to DHCP lease tables

│    • React 18.2.0 - UI framework                            │

│    • React Router 7.9.4 - Client-side routing               │**Files Created:**

│    • Chart.js 4.4.0 - Data visualization ← NEW!             │- `port_manager.py` - Core port management system (300 lines)

│    • react-chartjs-2 5.2.0 - React wrapper ← NEW!           │- `api_server_v2.py` - Enhanced Flask API with PortManager integration

└─────────────────────┬───────────────────────────────────────┘- `testbed/prototypes/port_management/` - Complete test suite

                      │

                      ↕ HTTP/JSON (fetch API)**Testing Methodology:**

                      │ CORS enabled for localhost:3000Following Dr. Foster's guidance on rigorous testing, all development occurred in testbed environment first:

                      │

┌─────────────────────┴───────────────────────────────────────┐**Testbed Validation Results:**

│                    APPLICATION LAYER                         │- `test_port_manager.py` - Unit tests: **12/12 passed (100%)**

│               Flask REST API (Port 5000)                     │- `test_flask_with_ports.py` - Flask integration: **100% functional**

│                                                              │- `test_full_api.py` - Complete API test: **6/6 endpoints working**

│  Production Endpoints:                                       │- `final_integration_test.py` - Full integration: **4/4 scenarios passed**

│    GET /health                                              │

│    GET /api/teams                                           │**Test Coverage:**

│    GET /api/teams/<abbr>                                    │✅ Port availability checking  

│                                                              │✅ Port range scanning  

│  HCL Historical Endpoints: ← NEW!                           │✅ Service registration  

│    GET /api/hcl/teams                                       │✅ Conflict detection (identified React on 3000, PostgreSQL on 5432)  

│    GET /api/hcl/teams/<abbr>                                │✅ Port status reporting  

│    GET /api/hcl/teams/<abbr>/games                          │✅ Configuration persistence  

│                                                              │✅ Database integration (32 teams verified)  

│  Features:                                                   │✅ All REST API endpoints functional  

│    • CORS enabled (flask-cors) ← NEW!                       │

│    • RealDictCursor for JSON responses                      │**Networking Concepts Applied:**

│    • Error handling with proper HTTP codes                  │

│    • Activity logging to files                              │| Concept | Implementation |

│    • Environment variable configuration                     │|---------|----------------|

└─────────────────────┬───────────────────────────────────────┘| **TCP Socket Binding** | `socket.bind()` test for port availability |

                      │| **Port Scanning** | Non-intrusive iteration through port range |

                      ↕ SQL Queries (psycopg2)| **Service Discovery** | Service-to-port mapping with persistence |

                      │| **Address Resolution** | Automatic port assignment with fallback |

┌─────────────────────┴───────────────────────────────────────┐| **Conflict Detection** | Socket binding tests identify busy ports |

│                      DATA LAYER                              │| **Resource Pooling** | Managed port range (5000-5010) |

│           PostgreSQL Database (Port 5432)                    │

│              Database: nfl_analytics                         │**Benefits:**

│                                                              │

│  Production Schema (public):                                │**Before (Manual Port Management):**

│    • teams - Current season data                            │```

│    • update_metadata - Refresh tracking                     │You: python api_server.py

│                                                              │OS: Error! Port 5000 already in use (EADDRINUSE)

│  Historical Schema (hcl): ← NEW!                            │You: *check which process is using port*

│    • games - Game metadata (108 games)                      │You: *kill process or manually change port*

│    • team_game_stats - Performance per game (216 records)   │You: python api_server.py --port 5001

│    • v_team_season_stats - Season aggregates (VIEW)         │```

│    • v_team_game_details - Game details (VIEW)              │

│    • v_team_weekly_trends - Rolling averages (VIEW)         │**After (Automatic DHCP-Style Management):**

│                                                              │```

│  Data Coverage:                                              │You: python api_server_v2.py

│    • 2025 Season Weeks 1-7                                  │PortManager: Checking port 5000... BUSY

│    • 32 NFL teams                                           │PortManager: Checking port 5001... AVAILABLE

│    • 47 metrics per game (EPA, Success Rate, etc.)          │PortManager: Assigned port 5001 to flask_api

└──────────────────────────────────────────────────────────────┘Flask: Starting on 127.0.0.1:5001 ✓

```

SUPPORTING INFRASTRUCTURE

┌──────────────────────────────────────────────────────────────┐**Production Readiness:**

│  Logging System (logs/)                                      │- ✅ 100% test pass rate in testbed

│    • Daily rotated log files                                 │- ✅ Comprehensive test suite (6 test files, 4 documentation files)

│    • Component-based tracking                                │- ✅ Database integration verified

│    • log_viewer.py and quick_logs.py                         │- ✅ All API endpoints tested and working

└──────────────────────────────────────────────────────────────┘- ✅ Conflict detection validated

- ✅ Ready for production deployment

┌──────────────────────────────────────────────────────────────┐

│  Data Refresh Layer                                          │**Deployment & Rollback Procedures:**

│    • scrape_teamrankings.py - Live data updates             │

│    • nflverse_data_loader.py - Historical data loading      │*Production Deployment:*

│    • Automated 24-hour refresh cycles                        │```powershell

└──────────────────────────────────────────────────────────────┘# Step 1: Stop current production server

```Stop-Process -Name python* -Force



---# Step 2: Backup current production file

cd "c:\IS330\H.C Lombardo App"

## Technical StackCopy-Item api_server.py api_server_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').py



### Frontend (Presentation Layer)# Step 3: Deploy new version

- **Framework:** React 18.2.0python api_server_v2.py

- **Routing:** React Router DOM 7.9.4

- **Visualization:** Chart.js 4.4.0 + react-chartjs-2 5.2.0# Step 4: Verify endpoints

- **HTTP Client:** Fetch APIcurl http://127.0.0.1:5000/health

- **Styling:** CSS3 (Gradients, Flexbox, Grid)curl http://127.0.0.1:5000/port-status

- **Build Tool:** react-scripts 5.0.1```

- **Package Manager:** npm (1331 packages)

*Rollback Procedure (if issues occur):*

### Backend (Application Layer)```powershell

- **Framework:** Python 3.11 + Flask 3.0+# IMMEDIATE ROLLBACK - Return to stable version

- **CORS:** flask-cors 6.0.1Stop-Process -Name python* -Force

- **Database Driver:** psycopg2-binary 2.9+cd "c:\IS330\H.C Lombardo App"

- **Environment:** python-dotenv 1.0+python api_server.py  # Original stable version

- **Architecture:** Blueprint pattern for modular API design

# OR: Restore from backup

### Database (Data Layer)Copy-Item api_server_backup_YYYYMMDD_HHMMSS.py api_server.py

- **RDBMS:** PostgreSQL 15+python api_server.py

- **Schemas:** ```

  - `public` - Production current season data

  - `hcl` - Historical game data (3NF design)*Return to Testbed for Further Testing:*

- **Views:** 3 materialized-style views for performance```powershell

- **Normalization:** Third Normal Form (3NF)# Stop production

Stop-Process -Name python* -Force

### Data Sources

- **Historical:** nflverse (nfl-data-py library)# Move to testbed for debugging

- **Live:** TeamRankings.com (web scraping)cd "c:\IS330\H.C Lombardo App\testbed\prototypes\port_management"

- **Images:** ESPN CDN (team logos)

# Run comprehensive tests

### Development Toolspython test_port_manager.py        # Unit tests

- **Version Control:** Git + GitHubpython test_flask_with_ports.py    # Flask integration

- **IDE:** VS Codepython test_full_api.py             # Complete API test

- **Testing:** Manual validation + automated test suitespython final_integration_test.py   # Full integration

- **Deployment:** PowerShell scripts (START.bat, STOP.bat)

- **Methodology:** Testbed-first development# Test live server in testbed

python test_full_api.py --live

---# Manually test: http://127.0.0.1:5000/health



## Database Schema# Fix issues, then re-test before returning to production

```

### Production Schema (public)

```sql*Verification Checklist After Deployment:*

CREATE TABLE teams (- [ ] Flask API responds on assigned port

    id SERIAL PRIMARY KEY,- [ ] `/health` endpoint returns healthy status

    name TEXT NOT NULL,- [ ] `/port-status` shows no critical conflicts

    abbreviation TEXT UNIQUE,- [ ] `/api/teams` returns all 32 teams

    wins INTEGER DEFAULT 0,- [ ] Database connection successful

    losses INTEGER DEFAULT 0,- [ ] React frontend can communicate with API

    ties INTEGER DEFAULT 0,- [ ] No port conflict errors in logs

    ppg REAL,              -- Points Per Game

    pa REAL,               -- Points Allowed*Rollback Criteria (When to Rollback):*

    games_played INTEGER,- API fails to start within 30 seconds

    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP- Database connection errors persist

);- Port conflicts cannot be resolved

```- React frontend cannot connect to API

- Any critical endpoint returns 500 errors

### Historical Schema (hcl) - NEW!- Port manager throws unhandled exceptions

```sql

-- Game metadata**Academic Significance:**

CREATE TABLE hcl.games (This implementation demonstrates:

    game_id TEXT PRIMARY KEY,- Application of networking theory (DHCP) to software engineering

    season INTEGER NOT NULL,- Systematic problem-solving approach

    week INTEGER NOT NULL,- Comprehensive testing methodology (testbed before production)

    game_type TEXT,- **Professional deployment practices** (backup, rollback, verification)

    home_team TEXT,- Documentation and knowledge transfer

    away_team TEXT,- Bridge between IS330 networking concepts and practical development

    home_score INTEGER,

    away_score INTEGER,**Industry Relevance:**

    game_date DATE,While large-scale systems (Docker, Kubernetes, cloud platforms) use similar dynamic port allocation, this specific application to Flask development environments represents an original solution to a common developer pain point. The DHCP analogy provides a clear mental model for understanding the system's behavior. The deployment procedures follow industry-standard DevOps practices for safe production changes.

    stadium TEXT,

    city TEXT,---

    state TEXT

);## October 8, 2025 - Database & Logging Infrastructure



-- Team performance per game#### 2. PostgreSQL Migration ✅

CREATE TABLE hcl.team_game_stats (**Previous:** SQLite (single-file database)  

    id SERIAL PRIMARY KEY,**Current:** PostgreSQL 18 (enterprise-grade RDBMS)

    game_id TEXT REFERENCES hcl.games(game_id),

    team TEXT NOT NULL,**Why the upgrade:**

    opponent TEXT NOT NULL,- Better scalability for large datasets

    is_home BOOLEAN,- Concurrent access support

    won BOOLEAN,- Industry-standard database system

    points_scored INTEGER,- Advanced features and performance

    points_allowed INTEGER,

    -- Advanced metrics (47 total fields)**Implementation:**

    epa_per_play REAL,- Installed PostgreSQL 18 locally

    success_rate REAL,- Created `nfl_analytics` database

    yards_per_play REAL,- Migrated all team data

    total_plays INTEGER,- Updated all database connections

    turnovers_lost INTEGER,- Secured credentials with `.env` file

    third_down_rate REAL,

    red_zone_efficiency REAL,#### 3. Live Data Integration ✅

    -- ... (40 more fields)**Data Source:** TeamRankings.com (Web Scraping)

    UNIQUE(game_id, team)

);**Features:**

- Automatic 24-hour refresh cycle

-- Season aggregates view- Scrapes real-time PPG (Points Per Game)

CREATE VIEW hcl.v_team_season_stats AS- Scrapes real-time PA (Points Allowed)

SELECT - Updates PostgreSQL automatically

    team,- Metadata tracking for last update time

    season,

    COUNT(*) as games_played,**Files:**

    SUM(CASE WHEN won THEN 1 ELSE 0 END) as wins,- `scrape_teamrankings.py` - Live data scraper

    SUM(CASE WHEN NOT won THEN 1 ELSE 0 END) as losses,- `espn_data_fetcher.py` - Backup ESPN API option

    AVG(points_scored) as avg_ppg_for,- `app.py` - Auto-refresh logic

    AVG(epa_per_play) as avg_epa_offense,

    AVG(success_rate) as avg_success_rate_offense,#### 4. Professional Web Dashboard ✅

    AVG(yards_per_play) as avg_yards_per_play**Technology:** Flask web framework

    -- ... (aggregates for all 47 metrics)

FROM hcl.team_game_stats**Features:**

GROUP BY team, season;- Displays all 32 NFL teams (not just top 10)

```- Scrollable lists with custom styling

- Official NFL and team logos from ESPN CDN

---- Top 5 teams highlighted in gold

- Professional color scheme (NFL blue gradient)

## Project Structure (Updated October 27, 2025)- Glassmorphism design effects

- Responsive layout

```

H.C Lombardo App/**Visual Enhancements:**

├── START.bat                       # Start Flask + React servers- Gold gradient title text

├── STOP.bat                        # Stop all servers- NFL shield logo in header

├── app.py                          # Main Flask application (CORS enabled)- Individual team logos next to each team

├── api_routes_hcl.py               # HCL historical API blueprint- Hover effects with animations

├── api_server.py                   # Original REST API server- Custom gold-themed scrollbars

├── db_config.py                    # Database configuration

├── logging_config.py               # Logging system#### 5. Development Best Practices ✅

├── scrape_teamrankings.py          # Live data scraper

├── nfl_database_loader.py          # PostgreSQL data loader**Code Organization:**

├── dr.foster.md                    # This file- Clean separation of concerns

├── .env                            # Environment variables (secure)- Environment variables for security

├── .gitignore                      # Git ignore rules- Database connection pooling

│- Error handling and logging

├── frontend/                       # React Application- Modular code structure

│   ├── package.json                # Dependencies (1331 packages)

│   ├── public/**Version Control:**

│   │   └── index.html- All changes committed to GitHub

│   └── src/- `.gitignore` for sensitive files

│       ├── App.js                  # Main component with routing- Professional commit messages

│       ├── App.css                 # Global styles- Regular backups

│       ├── SideMenu.js             # Navigation sidebar

│       ├── Homepage.js             # Landing page**Testing Infrastructure:**

│       ├── TeamStats.js            # Team selection page- Created `testbed/` for safe experimentation

│       ├── HistoricalData.js       # 32-team grid (NEW!)- Test templates provided

│       ├── HistoricalData.css      # Grid styling (NEW!)- Experiments folder for API testing

│       ├── TeamDetail.js           # Team analysis page (NEW!)- Prototypes folder for UI testing

│       ├── TeamDetail.css          # Detail styling (NEW!)

│       └── index.js                # React entry point#### 6. Comprehensive Logging System ✅

│**Implementation Date:** October 8, 2025

├── logs/                           # Daily activity logs

│   └── hc_lombardo_YYYYMMDD.log**Purpose:** Complete activity tracking stored locally for analysis and debugging

│

├── backups/                        # Backup directory**Files Created:**

│   └── sprint7_complete_2025-10-27_1108/- `logging_config.py` - Central logging configuration with rotation

│- `log_viewer.py` - Interactive log analysis tool

├── testbed/                        # Development & testing zone- `quick_logs.py` - Simple command-line log viewer

│   ├── api_routes_hcl.py           # HCL API (moved to production)

│   ├── nflverse_data_loader.py     # Historical data loader**Enhanced Files:**

│   ├── test_api_endpoints.py       # API test suite- `app.py` - Logs all Flask activities, database queries, page views

│   ├── schema/- `scrape_teamrankings.py` - Logs all scraping activities and performance

│   │   └── hcl_schema.sql          # Database schema

│   └── validate_database.sql       # Validation queries**Features:**

│- Daily log files with automatic rotation (10MB max, keeps 5 files)

└── docs/                           # Documentation- Color-coded output (🟢 Info, 🟡 Warning, 🔴 Error)

    ├── HISTORICAL_DATA_STORAGE_PLAN.md- Component-based logging (app, database, scraper, api)

    ├── SPRINT_6_COMPLETE.md- Professional timestamping and structured format

    ├── SPRINT_7_COMPLETE.md- Built-in viewers requiring no external applications

    ├── PRODUCTION_DEPLOYMENT.md

    └── DATABASE_3NF_ANALYSIS.md**What Gets Logged:**

```- Application startup/shutdown events

- User page access and interactions

---- Database connection attempts and query results

- Data refresh cycles and performance metrics

## How to Run- TeamRankings.com scraping activities

- Error conditions with detailed context

### Quick Start (Both Servers)- System performance and component interactions

```bash

# Start everything**Usage:**

START.bat```bash

python quick_logs.py        # View recent activity

# Visit the apppython quick_logs.py 50     # View last 50 lines

# React UI: http://localhost:3000python quick_logs.py errors # View only errors

# Flask API: http://127.0.0.1:5000/healthpython log_viewer.py        # Interactive menu

```

# Stop everything

STOP.bat**Log Storage:** `logs/hc_lombardo_YYYYMMDD.log`

```

---

### Manual Start

```bash**What We Built:**

# Terminal 1: Flask APIProfessional-grade separation of concerns using industry-standard three-tier architecture:

cd "c:\IS330\H.C Lombardo App"- **Presentation Layer:** React frontend (modern UI framework)

python app.py- **Application Layer:** Flask REST API (business logic and routing)

# Runs on http://127.0.0.1:5000- **Data Layer:** PostgreSQL database (persistent storage)



# Terminal 2: React Frontend**Why This Matters:**

cd "c:\IS330\H.C Lombardo App\frontend"- Each tier can be scaled independently

npm start- Frontend and backend can be developed separately

# Runs on http://localhost:3000- Industry-standard approach used by major companies

```- Enables future mobile app development (same API)

- Better security (database never exposed to frontend)

### First Time Setup- Easier testing and maintenance

```bash

# 1. Install Python dependencies**Files Created:**

pip install flask flask-cors psycopg2-binary python-dotenv requests beautifulsoup4 nfl-data-py- `api_server.py` - Production Flask REST API server

- `frontend/` - Complete React application with npm dependencies

# 2. Install Node.js and npm- `frontend/package.json` - React configuration and dependencies

# Download from https://nodejs.org/- `frontend/src/App.js` - Main React component

- `frontend/src/App.css` - Production styling with gradients

# 3. Install React dependencies- `PRODUCTION_DEPLOYMENT.md` - Complete deployment documentation

cd frontend- `README.md` - Project overview and quick start guide

npm install

**Testing Methodology:**

# 4. Configure environment- Applied slow, step-by-step verification process

# Copy .env.example to .env- Each component tested before moving to next step

# Set DB_PASSWORD=your_postgres_password- 10 verification steps all passed before completion

- Same rigorous approach used in testbed environment

# 5. Load historical data (optional)

cd testbed**Production URLs:**

python nflverse_data_loader.py --season 2025 --weeks 1-7 --output database- Frontend: http://localhost:3000 (React UI)

```- API: http://127.0.0.1:5000 (Flask REST endpoints)

- Database: localhost:5432 (PostgreSQL)

---

### Current Architecture: Three-Tier Production System

## Features Demonstrated

```

### Sprint 5 (Database Design)                USER INTERFACE

✅ **Database Normalization**┌───────────────────────────────────────────────────┐

- Third Normal Form (3NF) schema design│         React Frontend (Port 3000)                │

- Eliminated data redundancy│         frontend/                                 │

- Proper foreign key relationships│  • Modern UI with React 18.2.0                    │

- Efficient view creation│  • Displays all 32 NFL teams                      │

│  • Real-time status monitoring                    │

✅ **SQL Skills**│  • Professional gradient styling                  │

- Complex CREATE TABLE statements│  • Responsive card-based layout                   │

- CREATE VIEW for dynamic aggregation└─────────────────┬─────────────────────────────────┘

- Multi-table JOINs in views                  │

- Aggregate functions (AVG, SUM, COUNT)                  │ HTTP Requests (fetch API)

- Window functions for rolling averages                  │ GET /api/teams

                  │ GET /health

✅ **Data Modeling**                  ▼

- Entity-relationship design┌───────────────────────────────────────────────────┐

- Schema documentation│         Flask REST API (Port 5000)                │

- Migration planning│         api_server.py                             │

- Testbed validation methodology│  • REST endpoints for data access                 │

│  • CORS enabled for React communication           │

### Sprint 6 (API Development)│  • Business logic and validation                  │

✅ **RESTful API Design**│  • Integrated logging system                      │

- Resource-based URLs (/api/teams, /api/teams/:id)│  • Error handling and status monitoring           │

- Proper HTTP methods (GET)│                                                    │

- JSON response format│  Endpoints:                                        │

- Status codes (200, 404, 400, 500)│    GET /              - Welcome message           │

│    GET /health        - System health check       │

✅ **Flask Development**│    GET /api/teams     - All teams data            │

- Blueprint pattern for modularity│    GET /api/teams/count - Team count              │

- Route parameters and query strings│    GET /api/teams/<abbr> - Single team            │

- Database integration with psycopg2└─────────────────┬─────────────────────────────────┘

- Error handling and validation                  │

- CORS configuration                  │ SQL Queries (psycopg2)

                  │ SELECT * FROM teams

✅ **Testing Methodology**                  ▼

- Automated test suite┌───────────────────────────────────────────────────┐

- Manual endpoint testing│      PostgreSQL Database (Port 5432)              │

- Response validation│      nfl_analytics database                       │

- Performance verification│  • 32 NFL teams with complete stats               │

│  • Real-time PPG and PA data                      │

### Sprint 7 (Frontend Integration)│  • Update metadata tracking                       │

✅ **React Development**│  • Persistent data storage                        │

- Functional components with Hooks│  • Enterprise-grade RDBMS                         │

- useState and useEffect for state management└───────────────────────────────────────────────────┘

- Component-based architecture                  ▲

- Props and event handling                  │

                  │ Data Updates

✅ **React Router**┌─────────────────┴─────────────────────────────────┐

- Client-side routing│      Data Refresh Layer (scrape_teamrankings)     │

- Dynamic routes with parameters│  • Scrapes TeamRankings.com                       │

- Link-based navigation│  • Combines PPG + PA data                         │

- useNavigate and useParams hooks│  • Updates PostgreSQL via SQL                     │

│  • Logs scraping performance and results          │

✅ **Data Visualization**└───────────────────────────────────────────────────┘

- Chart.js line charts

- Multi-dataset graphsSUPPORTING INFRASTRUCTURE

- Responsive chart sizing┌───────────────────────────────────────────────────┐

- Custom styling and colors│           Logging System (logs/)                  │

│  • Daily rotated log files                        │

✅ **API Integration**│  • Component-based activity tracking              │

- Fetch API for HTTP requests│  • Built-in viewers and analysis tools            │

- Async/await patterns│  • Complete audit trail of all operations         │

- Error handling└───────────────────────────────────────────────────┘

- Loading states```



✅ **Responsive Design****Communication Flow:**

- CSS Grid and Flexbox1. **User → React**: User opens browser at http://localhost:3000

- Media queries2. **React → Flask API**: `fetch('http://localhost:5000/api/teams')`

- Mobile-first approach3. **Flask → PostgreSQL**: `cursor.execute("SELECT * FROM teams")`

- Card-based layouts4. **PostgreSQL → Flask**: Returns 32 teams with all statistics

5. **Flask → React**: Sends JSON response `{"teams": [...]}`

✅ **Full-Stack Integration**6. **React → User**: Displays teams in beautiful card-based UI

- CORS configuration

- Frontend-backend communication**Key Benefits of This Architecture:**

- JSON data exchange- ✅ Separation of concerns (UI, logic, data)

- Production deployment- ✅ Scalable (can add more API servers)

- ✅ Testable (each tier tested independently)

---- ✅ Maintainable (changes in one tier don't affect others)

- ✅ Secure (database credentials only in API server)

## Key Learnings & Challenges- ✅ Future-ready (can add mobile apps using same API)



### Challenge 1: CORS Errors### Technical Stack

**Problem:** React couldn't access Flask API (CORS policy blocked requests)  

**Solution:** Added `flask-cors` package and `CORS(app)` to Flask  **Frontend (Presentation Layer):**

**Learning:** Cross-origin requests require explicit server permission- React 18.2.0 (Modern UI framework)

- JavaScript ES6+

### Challenge 2: Missing API Endpoints- CSS3 (Gradients, animations, responsive design)

**Problem:** TeamStats page got 404 errors, dropdown was empty  - React Hooks (useState, useEffect)

**Solution:** Added `/api/teams` and `/api/teams/<abbr>` endpoints  - Fetch API (HTTP client)

**Learning:** Frontend components need matching backend endpoints- npm package manager (1323 packages)



### Challenge 3: Data Structure Mismatch**Backend (Application Layer):**

**Problem:** TeamStats showed "N/A" for all fields despite receiving data  - Python 3.11

**Solution:** Updated component to extract nested `team` object from response  - Flask (REST API framework)

**Learning:** Frontend must match backend response structure exactly- Flask-CORS (Cross-origin resource sharing)

- psycopg2 (PostgreSQL driver)

### Challenge 4: Stale Timestamps- python-dotenv (Environment variables)

**Problem:** "Last Updated" showed 10:00 AM when servers weren't running then  - Custom logging system

**Solution:** Changed SQL query to use `NOW()` instead of stored timestamp  

**Learning:** Database vs. query-time timestamps serve different purposes**Database (Data Layer):**

- PostgreSQL 18 (Enterprise RDBMS)

### Challenge 5: Server Port Conflicts- SQL for queries and updates

**Problem:** Multiple terminals and server restarts caused port conflicts  - Connection pooling

**Solution:** Isolated servers in separate PowerShell windows  

**Learning:** Process management is critical in development**Data Collection:**

- BeautifulSoup4 (Web scraping)

---- Requests (HTTP client)

- TeamRankings.com (Data source)

## Next Steps: Sprint 8 Options- ESPN CDN (Logo images)



### Option 1: Full Historical Data Load 📊**Development Tools:**

- Load complete 2022-2024 seasons (~600 games)- Git version control

- Better trend charts with 3 years of data- Node.js runtime for React

- Enable momentum indicators- npm scripts for build automation

- More accurate projections  - PowerShell for deployment

**Timeline:** 2-3 days- VS Code IDE



### Option 2: Dashboard Week Selector 📅### Database Schema (PostgreSQL)

- Add dropdown to filter by week/season

- Display historical matchups```sql

- Show projections vs actual resultsCREATE TABLE teams (

- New endpoint: `GET /api/hcl/matchups?week=X`      id SERIAL PRIMARY KEY,

**Timeline:** 3-4 days    name TEXT NOT NULL,

    abbreviation TEXT,

### Option 3: Betting Analytics Features 💰    wins INTEGER,

- Add spread/total predictions to team pages    losses INTEGER,

- Calculate model accuracy (% correct ATS)    ppg REAL,              -- Points Per Game (offense)

- Display confidence levels    pa REAL,               -- Points Allowed (defense)

- Historical performance tracking      games_played INTEGER

**Timeline:** 4-5 days);



### Option 4: Live Data Integration ⚡CREATE TABLE update_metadata (

- Auto-refresh during game days    id SERIAL PRIMARY KEY,

- Real-time score updates    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP

- Live stat tracking);

- In-game notifications  ```

**Timeline:** 5-7 days

### Project Structure (Updated October 9, 2025)

### Option 5: Mobile Optimization 📱

- Progressive Web App (PWA) features```

- Touch-optimized controlsH.C Lombardo App/

- Offline support├── api_server.py                   # Production Flask REST API (NEW!)

- App-like experience  ├── app.py                          # Original Flask web application

**Timeline:** 3-4 days├── nfl_database_loader.py          # PostgreSQL data loader

├── scrape_teamrankings.py          # Live data scraper (with logging)

---├── espn_data_fetcher.py            # ESPN API (backup)

├── check_database.py               # Database verification

## Academic Significance├── db_config.py                    # Database configuration

├── logging_config.py               # Comprehensive logging system

This project demonstrates mastery of:├── log_viewer.py                   # Interactive log analysis tool

├── quick_logs.py                   # Simple command-line log viewer

**Database Design (Sprint 5)**├── test_apis.py                    # API testing utilities

- Third Normal Form normalization├── dr.foster.md                    # This assignment document

- View creation for performance├── PRODUCTION_DEPLOYMENT.md        # Full production documentation (NEW!)

- Schema documentation├── README.md                       # Project overview (NEW!)

- SQL proficiency├── .env                            # Environment variables (secure)

├── .env.example                    # Template for .env

**Backend Development (Sprint 6)**├── .gitignore                      # Git ignore rules

- RESTful API design├── frontend/                       # React application (NEW!)

- Flask framework expertise│   ├── package.json                # React dependencies (1323 packages)

- Blueprint pattern│   ├── package-lock.json           # Dependency lock file

- Testing methodology│   ├── public/

│   │   ├── index.html              # HTML template

**Frontend Development (Sprint 7)**│   │   └── favicon.ico

- Modern React development│   ├── src/

- Component architecture│   │   ├── App.js                  # Main React component

- State management│   │   ├── App.css                 # Production styling

- Client-side routing│   │   └── index.js                # React entry point

│   └── node_modules/               # npm packages (gitignored)

**Full-Stack Integration (Sprint 7)**├── templates/

- Three-tier architecture│   └── index.html                  # Original dashboard template

- CORS configuration├── logs/                           # Daily activity logs

- API integration│   ├── hc_lombardo_20251009.log    # Today's activity log

- Data visualization│   ├── hc_lombardo_20251008.log    # Yesterday's log

│   └── hc_lombardo_YYYYMMDD.log    # Historical logs (auto-rotated)

**Software Engineering Practices (All Sprints)**├── testbed/                        # Safe experimentation zone

- Version control with Git│   ├── README.md

- Testbed-first methodology│   ├── test_template.py

- Documentation│   ├── REACT_FLASK_POSTGRES_TEST_LOG.md  # Testing methodology

- Deployment procedures│   ├── METHODOLOGY.md              # Step-by-step approach

- Backup strategies│   ├── QUICK_REFERENCE.md          # Command reference

│   ├── experiments/

---│   │   └── test_espn_api.py

│   ├── prototypes/

## Production Metrics│   └── step_by_step/

│       └── step1_check_ports.py

**Current Data Coverage:**└── data/                           # (empty - using PostgreSQL)

- 2025 NFL Season: Weeks 1-7```

- Total Games: 108

- Team-Game Records: 216### How to Run

- Teams: 32

- Metrics per Game: 47**Prerequisites:**

```bash

**System Performance:**# Install Python dependencies

- API Response Time: <100mspip install flask flask-cors psycopg2-binary python-dotenv requests beautifulsoup4

- Database Queries: <50ms

- Frontend Load Time: <2s# Install Node.js and npm (for React frontend)

- Chart Rendering: <500ms# Download from https://nodejs.org/



**Code Statistics:**# PostgreSQL 18 must be installed and running

- React Components: 6```

- Flask Endpoints: 6

- Database Tables: 3**Option 1: Production System (Three-Tier Architecture)**

- Database Views: 3```bash

- Total Lines of Code: ~5,000+# Set up environment (first time only)

# Copy .env.example to .env and fill in PostgreSQL password

---

# Install React dependencies (first time only)

## Conclusioncd frontend

npm install

The H.C. Lombardo NFL Analytics Platform has evolved from a simple assignment into a comprehensive, production-ready full-stack application. Through Sprints 5, 6, and 7, we've built:cd ..



1. **Robust Database Foundation** - Properly normalized schema with efficient views# Terminal 1: Start Flask API server

2. **Professional REST API** - Clean, tested endpoints following industry standardspython api_server.py

3. **Modern React Frontend** - Interactive, responsive UI with data visualization# API runs on http://127.0.0.1:5000

4. **Full Integration** - Seamless communication between all tiers

# Terminal 2: Start React frontend

The platform is now ready for advanced features, additional data loading, and potential public deployment. All work follows rigorous testing methodologies and professional development practices suitable for real-world production environments.cd frontend

npm start

**Status:** Production Ready ✅  # Frontend runs on http://localhost:3000

**Next Phase:** Sprint 8 (Feature selection pending)  

**Recommendation:** Load full historical data (2022-2024) to maximize analytical capabilities# Visit the React app: http://localhost:3000

# API health check: http://127.0.0.1:5000/health

---```



**Last Updated:** October 27, 2025  **Option 2: Original Flask Application**

**Student:** April V  ```bash

**Course:** IS330 - Information Systems# Set up environment (first time only)

# Copy .env.example to .env and fill in PostgreSQL password

# Load initial data (if needed)
python scrape_teamrankings.py

# Run the web application
python app.py

# Visit: http://127.0.0.1:5000
```

**Updating Data:**
```bash
# Manual data refresh from TeamRankings.com
python scrape_teamrankings.py

# The production system automatically refreshes data every 24 hours
```

**Viewing Logs:**
```bash
# Quick log view
python quick_logs.py        # View recent activity
python quick_logs.py 50     # View last 50 lines
python quick_logs.py errors # View only errors

# Interactive log viewer
python log_viewer.py        # Menu-driven interface
```

### Features Demonstrated

✅ **Database Operations**
- PostgreSQL connection management
- CRUD operations (Create, Read, Update, Delete)
- Query optimization
- Transaction handling

✅ **Web Development**
- Flask routing and templates
- Dynamic content rendering
- Professional CSS styling
- Responsive design

✅ **Data Engineering**
- Web scraping with BeautifulSoup
- Data transformation and cleaning
- Automated data pipelines
- Error handling

✅ **DevOps Practices**
- Environment configuration
- Secret management
- Version control (Git/GitHub)
- Testing infrastructure

---
---

# Week 1: Initial Assignment (Original Requirements)

**Date:** September 2025  
**Student:** April V

### Assignment Requirements Completed ✅

#### 1. ML Model from HuggingFace ✅
**File:** `test_ml_model.py`
- Uses DistilBERT sentiment analysis model
- Tests on NFL-related text
- Demonstrates model loading and inference

**Run:** `python test_ml_model.py`

### 2. Database System ✅
**System:** SQLite
**File:** `assignment_solution.py`
- Creates database with NFL team statistics
- 32 teams with 2025 season data (Week 5)
- Schema: name, abbreviation, wins, losses, PPG, PA, games_played

### 3. Data Source ✅
**Source:** 2025 NFL Season Statistics
- Real team records and performance metrics
- Points Per Game (PPG) - offensive stat
- Points Allowed (PA) - defensive stat

### 4. Answer Questions ✅
**File:** `assignment_solution.py`

**1:** Top 10 Offensive Teams (Highest PPG)
- SQL Query: `SELECT * FROM teams ORDER BY ppg DESC LIMIT 10`
- Shows best scoring teams

**2** Top 10 Defensive Teams (Lowest PA)
- SQL Query: `SELECT * FROM teams ORDER BY pa ASC LIMIT 10`
- Shows best defensive teams

## How to Run

```bash
# Answer the assignment questions
python assignment_solution.py

# Test ML model
python test_ml_model.py
```

## Results

### Top 10 Offensive Teams
1. Detroit Lions - 29.5 PPG
2. Baltimore Ravens - 28.4 PPG
3. Washington Commanders - 28.2 PPG
4. Minnesota Vikings - 27.4 PPG
5. Buffalo Bills - 27.2 PPG
... (and 5 more)

### Top 10 Defensive Teams
1. Minnesota Vikings - 17.2 PA
2. Kansas City Chiefs - 17.8 PA
3. Denver Broncos - 18.6 PA
4. Houston Texans - 19.2 PA
5. Los Angeles Chargers - 19.8 PA
... (and 5 more)

## Database Schema

```sql
CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    abbreviation TEXT,
    wins INTEGER,
    losses INTEGER,
    ppg REAL,              -- Points Per Game (offense)
    pa REAL,               -- Points Allowed (defense)
    games_played INTEGER
);
```

## Project Structure

```
H.C Lombardo App/
├── assignment_solution.py    # Main assignment code
├── test_ml_model.py          # ML model test
├── data/
│   └── nfl_teams.db         # SQLite database
└── README.md                 # This file
```
