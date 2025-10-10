# H.C. Lombardo NFL Analytics Platform

## Project Overview

**What This App Is:**
The H.C. Lombardo NFL Analytics Platform is a comprehensive sports analytics application designed for professional NFL gambling analysis. Named after H.C. Lombardo, a professional gambler who is developing proprietary betting formulas, this platform serves as the technical infrastructure to support data-driven sports betting decisions.

**Core Purpose:**
This application collects, processes, and analyzes extensive NFL statistical data to generate "honest lines" for NFL games - mathematical predictions that can be compared against Vegas betting lines to identify value betting opportunities.

**Target User:**
Professional gamblers and serious sports bettors who need:
- Comprehensive historical and current NFL statistics
- Automated data collection and processing
- Custom formula implementation capabilities
- Line generation and value identification tools
- Performance tracking and analysis

**Key Features:**
1. **Comprehensive Database** - PostgreSQL-powered storage of NFL team statistics, game data, and betting information
2. **Automated Data Collection** - Web scraping from TeamRankings.com and other sources for daily stat updates
3. **Statistical Analysis Engine** - Framework for implementing custom betting formulas and mathematical models
4. **Line Generation System** - Tools to create weekly betting lines for all NFL games
5. **Value Detection** - Compare generated lines against Vegas lines to identify profitable betting opportunities
6. **Professional Logging** - Complete activity tracking for debugging and performance analysis
7. **Testbed Environment** - Safe development space for testing new features and data sources

**Technical Architecture:**
- **Backend:** Python Flask web framework
- **Database:** PostgreSQL 18 with advanced statistical schemas
- **Data Sources:** TeamRankings.com (primary), ESPN API (backup)
- **Frontend:** Bootstrap-responsive web interface
- **Infrastructure:** Automated refresh cycles, comprehensive logging, version control

**Development Philosophy:**
Built with professional gambling in mind - reliability, accuracy, and comprehensive data coverage are paramount. The platform is designed to handle the rigorous demands of daily betting analysis while providing the flexibility to implement and test new statistical approaches.

**Academic Context:**
Developed as part of IS330 coursework to demonstrate database design, web development, API integration, and data analysis capabilities in a real-world application scenario.

---

# H.C. Lombardo NFL Analytics - Dr. Foster Assignment

**Student:** April V  
**Course:** IS330  
**Date:** October 8, 2025  
**GitHub:** https://github.com/AprilV/H.C.-Lombardo-App

---

# Weeks 2-4: Database Migration & Live Data Integration

**Latest Update:** October 9, 2025  
**Student:** April V

### Major Upgrades Completed ✅

## October 9, 2025 - Production Three-Tier Architecture

#### 1. Production Three-Tier Architecture ✅
**Implementation Date:** October 9, 2025

**What We Built:**
Professional-grade separation of concerns using industry-standard three-tier architecture:
- **Presentation Layer:** React frontend (modern UI framework)
- **Application Layer:** Flask REST API (business logic and routing)
- **Data Layer:** PostgreSQL database (persistent storage)

**Why This Matters:**
- Each tier can be scaled independently
- Frontend and backend can be developed separately
- Industry-standard approach used by major companies
- Enables future mobile app development (same API)
- Better security (database never exposed to frontend)
- Easier testing and maintenance

**Files Created:**
- `api_server.py` - Production Flask REST API server
- `frontend/` - Complete React application with npm dependencies
- `frontend/package.json` - React configuration and dependencies
- `frontend/src/App.js` - Main React component
- `frontend/src/App.css` - Production styling with gradients
- `PRODUCTION_DEPLOYMENT.md` - Complete deployment documentation
- `README.md` - Project overview and quick start guide

**Testing Methodology:**
- Applied slow, step-by-step verification process
- Each component tested before moving to next step
- 10 verification steps all passed before completion
- Same rigorous approach used in testbed environment

**Production URLs:**
- Frontend: http://localhost:3000 (React UI)
- API: http://127.0.0.1:5000 (Flask REST endpoints)
- Database: localhost:5432 (PostgreSQL)

### Current Architecture: Three-Tier Production System

```
                USER INTERFACE
┌───────────────────────────────────────────────────┐
│         React Frontend (Port 3000)                │
│         frontend/                                 │
│  • Modern UI with React 18.2.0                    │
│  • Displays all 32 NFL teams                      │
│  • Real-time status monitoring                    │
│  • Professional gradient styling                  │
│  • Responsive card-based layout                   │
└─────────────────┬─────────────────────────────────┘
                  │
                  ↕ HTTP Request/Response (JSON)
                  │ Request: GET /api/teams
                  │ Response: {"teams": [...]}
                  │
┌─────────────────┴─────────────────────────────────┐
│         Flask REST API (Port 5000)                │
│         api_server.py                             │
│  • REST endpoints for data access                 │
│  • CORS enabled for React communication           │
│  • Business logic and validation                  │
│  • Integrated logging system                      │
│  • Error handling and status monitoring           │
│                                                    │
│  Endpoints:                                        │
│    GET /              - Welcome message           │
│    GET /health        - System health check       │
│    GET /api/teams     - All teams data            │
│    GET /api/teams/count - Team count              │
│    GET /api/teams/<abbr> - Single team            │
└─────────────────┬─────────────────────────────────┘
                  │
                  ↕ SQL Query/Result
                  │ Query: SELECT * FROM teams
                  │ Result: 32 rows returned
                  │
┌─────────────────┴─────────────────────────────────┐
│      PostgreSQL Database (Port 5432)              │
│      nfl_analytics database                       │
│  • 32 NFL teams with complete stats               │
│  • Real-time PPG and PA data                      │
│  • Update metadata tracking                       │
│  • Persistent data storage                        │
│  • Enterprise-grade RDBMS                         │
└───────────────────────────────────────────────────┘
                  ▲
                  │
                  │ Data Updates
┌─────────────────┴─────────────────────────────────┐
│      Data Refresh Layer (scrape_teamrankings)     │
│  • Scrapes TeamRankings.com                       │
│  • Combines PPG + PA data                         │
│  • Updates PostgreSQL via SQL                     │
│  • Logs scraping performance and results          │
└───────────────────────────────────────────────────┘

SUPPORTING INFRASTRUCTURE
┌───────────────────────────────────────────────────┐
│           Logging System (logs/)                  │
│  • Daily rotated log files                        │
│  • Component-based activity tracking              │
│  • Built-in viewers and analysis tools            │
│  • Complete audit trail of all operations         │
└───────────────────────────────────────────────────┘
```

**Communication Flow:**
1. **User → React**: User opens browser at http://localhost:3000
2. **React → Flask API**: `fetch('http://localhost:5000/api/teams')`
3. **Flask → PostgreSQL**: `cursor.execute("SELECT * FROM teams")`
4. **PostgreSQL → Flask**: Returns 32 teams with all statistics
5. **Flask → React**: Sends JSON response `{"teams": [...]}`
6. **React → User**: Displays teams in beautiful card-based UI

**Key Benefits of This Architecture:**
- ✅ Separation of concerns (UI, logic, data)
- ✅ Scalable (can add more API servers)
- ✅ Testable (each tier tested independently)
- ✅ Maintainable (changes in one tier don't affect others)
- ✅ Secure (database credentials only in API server)
- ✅ Future-ready (can add mobile apps using same API)

---

## October 8, 2025 - Database & Logging Infrastructure

#### 2. PostgreSQL Migration ✅
**Previous:** SQLite (single-file database)  
**Current:** PostgreSQL 18 (enterprise-grade RDBMS)

**Why the upgrade:**
- Better scalability for large datasets
- Concurrent access support
- Industry-standard database system
- Advanced features and performance

**Implementation:**
- Installed PostgreSQL 18 locally
- Created `nfl_analytics` database
- Migrated all team data
- Updated all database connections
- Secured credentials with `.env` file

#### 3. Live Data Integration ✅
**Data Source:** TeamRankings.com (Web Scraping)

**Features:**
- Automatic 24-hour refresh cycle
- Scrapes real-time PPG (Points Per Game)
- Scrapes real-time PA (Points Allowed)
- Updates PostgreSQL automatically
- Metadata tracking for last update time

**Files:**
- `scrape_teamrankings.py` - Live data scraper
- `espn_data_fetcher.py` - Backup ESPN API option
- `app.py` - Auto-refresh logic

#### 4. Professional Web Dashboard ✅
**Technology:** Flask web framework

**Features:**
- Displays all 32 NFL teams (not just top 10)
- Scrollable lists with custom styling
- Official NFL and team logos from ESPN CDN
- Top 5 teams highlighted in gold
- Professional color scheme (NFL blue gradient)
- Glassmorphism design effects
- Responsive layout

**Visual Enhancements:**
- Gold gradient title text
- NFL shield logo in header
- Individual team logos next to each team
- Hover effects with animations
- Custom gold-themed scrollbars

#### 5. Development Best Practices ✅

**Code Organization:**
- Clean separation of concerns
- Environment variables for security
- Database connection pooling
- Error handling and logging
- Modular code structure

**Version Control:**
- All changes committed to GitHub
- `.gitignore` for sensitive files
- Professional commit messages
- Regular backups

**Testing Infrastructure:**
- Created `testbed/` for safe experimentation
- Test templates provided
- Experiments folder for API testing
- Prototypes folder for UI testing

#### 6. Comprehensive Logging System ✅
**Implementation Date:** October 8, 2025

**Purpose:** Complete activity tracking stored locally for analysis and debugging

**Files Created:**
- `logging_config.py` - Central logging configuration with rotation
- `log_viewer.py` - Interactive log analysis tool
- `quick_logs.py` - Simple command-line log viewer

**Enhanced Files:**
- `app.py` - Logs all Flask activities, database queries, page views
- `scrape_teamrankings.py` - Logs all scraping activities and performance

**Features:**
- Daily log files with automatic rotation (10MB max, keeps 5 files)
- Color-coded output (🟢 Info, 🟡 Warning, 🔴 Error)
- Component-based logging (app, database, scraper, api)
- Professional timestamping and structured format
- Built-in viewers requiring no external applications

**What Gets Logged:**
- Application startup/shutdown events
- User page access and interactions
- Database connection attempts and query results
- Data refresh cycles and performance metrics
- TeamRankings.com scraping activities
- Error conditions with detailed context
- System performance and component interactions

**Usage:**
```bash
python quick_logs.py        # View recent activity
python quick_logs.py 50     # View last 50 lines
python quick_logs.py errors # View only errors
python log_viewer.py        # Interactive menu
```

**Log Storage:** `logs/hc_lombardo_YYYYMMDD.log`

---

**What We Built:**
Professional-grade separation of concerns using industry-standard three-tier architecture:
- **Presentation Layer:** React frontend (modern UI framework)
- **Application Layer:** Flask REST API (business logic and routing)
- **Data Layer:** PostgreSQL database (persistent storage)

**Why This Matters:**
- Each tier can be scaled independently
- Frontend and backend can be developed separately
- Industry-standard approach used by major companies
- Enables future mobile app development (same API)
- Better security (database never exposed to frontend)
- Easier testing and maintenance

**Files Created:**
- `api_server.py` - Production Flask REST API server
- `frontend/` - Complete React application with npm dependencies
- `frontend/package.json` - React configuration and dependencies
- `frontend/src/App.js` - Main React component
- `frontend/src/App.css` - Production styling with gradients
- `PRODUCTION_DEPLOYMENT.md` - Complete deployment documentation
- `README.md` - Project overview and quick start guide

**Testing Methodology:**
- Applied slow, step-by-step verification process
- Each component tested before moving to next step
- 10 verification steps all passed before completion
- Same rigorous approach used in testbed environment

**Production URLs:**
- Frontend: http://localhost:3000 (React UI)
- API: http://127.0.0.1:5000 (Flask REST endpoints)
- Database: localhost:5432 (PostgreSQL)

### Current Architecture: Three-Tier Production System

```
                USER INTERFACE
┌───────────────────────────────────────────────────┐
│         React Frontend (Port 3000)                │
│         frontend/                                 │
│  • Modern UI with React 18.2.0                    │
│  • Displays all 32 NFL teams                      │
│  • Real-time status monitoring                    │
│  • Professional gradient styling                  │
│  • Responsive card-based layout                   │
└─────────────────┬─────────────────────────────────┘
                  │
                  │ HTTP Requests (fetch API)
                  │ GET /api/teams
                  │ GET /health
                  ▼
┌───────────────────────────────────────────────────┐
│         Flask REST API (Port 5000)                │
│         api_server.py                             │
│  • REST endpoints for data access                 │
│  • CORS enabled for React communication           │
│  • Business logic and validation                  │
│  • Integrated logging system                      │
│  • Error handling and status monitoring           │
│                                                    │
│  Endpoints:                                        │
│    GET /              - Welcome message           │
│    GET /health        - System health check       │
│    GET /api/teams     - All teams data            │
│    GET /api/teams/count - Team count              │
│    GET /api/teams/<abbr> - Single team            │
└─────────────────┬─────────────────────────────────┘
                  │
                  │ SQL Queries (psycopg2)
                  │ SELECT * FROM teams
                  ▼
┌───────────────────────────────────────────────────┐
│      PostgreSQL Database (Port 5432)              │
│      nfl_analytics database                       │
│  • 32 NFL teams with complete stats               │
│  • Real-time PPG and PA data                      │
│  • Update metadata tracking                       │
│  • Persistent data storage                        │
│  • Enterprise-grade RDBMS                         │
└───────────────────────────────────────────────────┘
                  ▲
                  │
                  │ Data Updates
┌─────────────────┴─────────────────────────────────┐
│      Data Refresh Layer (scrape_teamrankings)     │
│  • Scrapes TeamRankings.com                       │
│  • Combines PPG + PA data                         │
│  • Updates PostgreSQL via SQL                     │
│  • Logs scraping performance and results          │
└───────────────────────────────────────────────────┘

SUPPORTING INFRASTRUCTURE
┌───────────────────────────────────────────────────┐
│           Logging System (logs/)                  │
│  • Daily rotated log files                        │
│  • Component-based activity tracking              │
│  • Built-in viewers and analysis tools            │
│  • Complete audit trail of all operations         │
└───────────────────────────────────────────────────┘
```

**Communication Flow:**
1. **User → React**: User opens browser at http://localhost:3000
2. **React → Flask API**: `fetch('http://localhost:5000/api/teams')`
3. **Flask → PostgreSQL**: `cursor.execute("SELECT * FROM teams")`
4. **PostgreSQL → Flask**: Returns 32 teams with all statistics
5. **Flask → React**: Sends JSON response `{"teams": [...]}`
6. **React → User**: Displays teams in beautiful card-based UI

**Key Benefits of This Architecture:**
- ✅ Separation of concerns (UI, logic, data)
- ✅ Scalable (can add more API servers)
- ✅ Testable (each tier tested independently)
- ✅ Maintainable (changes in one tier don't affect others)
- ✅ Secure (database credentials only in API server)
- ✅ Future-ready (can add mobile apps using same API)

### Technical Stack

**Frontend (Presentation Layer):**
- React 18.2.0 (Modern UI framework)
- JavaScript ES6+
- CSS3 (Gradients, animations, responsive design)
- React Hooks (useState, useEffect)
- Fetch API (HTTP client)
- npm package manager (1323 packages)

**Backend (Application Layer):**
- Python 3.11
- Flask (REST API framework)
- Flask-CORS (Cross-origin resource sharing)
- psycopg2 (PostgreSQL driver)
- python-dotenv (Environment variables)
- Custom logging system

**Database (Data Layer):**
- PostgreSQL 18 (Enterprise RDBMS)
- SQL for queries and updates
- Connection pooling

**Data Collection:**
- BeautifulSoup4 (Web scraping)
- Requests (HTTP client)
- TeamRankings.com (Data source)
- ESPN CDN (Logo images)

**Development Tools:**
- Git version control
- Node.js runtime for React
- npm scripts for build automation
- PowerShell for deployment
- VS Code IDE

### Database Schema (PostgreSQL)

```sql
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    abbreviation TEXT,
    wins INTEGER,
    losses INTEGER,
    ppg REAL,              -- Points Per Game (offense)
    pa REAL,               -- Points Allowed (defense)
    games_played INTEGER
);

CREATE TABLE update_metadata (
    id SERIAL PRIMARY KEY,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Project Structure (Updated October 9, 2025)

```
H.C Lombardo App/
├── api_server.py                   # Production Flask REST API (NEW!)
├── app.py                          # Original Flask web application
├── nfl_database_loader.py          # PostgreSQL data loader
├── scrape_teamrankings.py          # Live data scraper (with logging)
├── espn_data_fetcher.py            # ESPN API (backup)
├── check_database.py               # Database verification
├── db_config.py                    # Database configuration
├── logging_config.py               # Comprehensive logging system
├── log_viewer.py                   # Interactive log analysis tool
├── quick_logs.py                   # Simple command-line log viewer
├── test_apis.py                    # API testing utilities
├── dr.foster.md                    # This assignment document
├── PRODUCTION_DEPLOYMENT.md        # Full production documentation (NEW!)
├── README.md                       # Project overview (NEW!)
├── .env                            # Environment variables (secure)
├── .env.example                    # Template for .env
├── .gitignore                      # Git ignore rules
├── frontend/                       # React application (NEW!)
│   ├── package.json                # React dependencies (1323 packages)
│   ├── package-lock.json           # Dependency lock file
│   ├── public/
│   │   ├── index.html              # HTML template
│   │   └── favicon.ico
│   ├── src/
│   │   ├── App.js                  # Main React component
│   │   ├── App.css                 # Production styling
│   │   └── index.js                # React entry point
│   └── node_modules/               # npm packages (gitignored)
├── templates/
│   └── index.html                  # Original dashboard template
├── logs/                           # Daily activity logs
│   ├── hc_lombardo_20251009.log    # Today's activity log
│   ├── hc_lombardo_20251008.log    # Yesterday's log
│   └── hc_lombardo_YYYYMMDD.log    # Historical logs (auto-rotated)
├── testbed/                        # Safe experimentation zone
│   ├── README.md
│   ├── test_template.py
│   ├── REACT_FLASK_POSTGRES_TEST_LOG.md  # Testing methodology
│   ├── METHODOLOGY.md              # Step-by-step approach
│   ├── QUICK_REFERENCE.md          # Command reference
│   ├── experiments/
│   │   └── test_espn_api.py
│   ├── prototypes/
│   └── step_by_step/
│       └── step1_check_ports.py
└── data/                           # (empty - using PostgreSQL)
```

### How to Run

**Prerequisites:**
```bash
# Install Python dependencies
pip install flask flask-cors psycopg2-binary python-dotenv requests beautifulsoup4

# Install Node.js and npm (for React frontend)
# Download from https://nodejs.org/

# PostgreSQL 18 must be installed and running
```

**Option 1: Production System (Three-Tier Architecture)**
```bash
# Set up environment (first time only)
# Copy .env.example to .env and fill in PostgreSQL password

# Install React dependencies (first time only)
cd frontend
npm install
cd ..

# Terminal 1: Start Flask API server
python api_server.py
# API runs on http://127.0.0.1:5000

# Terminal 2: Start React frontend
cd frontend
npm start
# Frontend runs on http://localhost:3000

# Visit the React app: http://localhost:3000
# API health check: http://127.0.0.1:5000/health
```

**Option 2: Original Flask Application**
```bash
# Set up environment (first time only)
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
