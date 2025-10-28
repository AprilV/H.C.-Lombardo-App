# 🏈 H.C. Lombardo NFL Analytics - Dr. Foster

**Student:** April V. Sykes  
**Course:** IS330  
**School Week:** 6 (of Weeks 5-6 assignment period)  
**Sprint Status:** Sprints 5-7 Complete ✅ | Preparing for Sprint 8 🚀  
**NFL Week:** 9 (Week 8 Complete)  
**Latest Update:** October 27, 2025

---

## 🚀 **CURRENT STATUS: Sprints 5-7 Complete, Sprint 8 Next!**

### **Weeks 5-6: nflverse Integration & Team Detail Pages - October 21-27, 2025**
The application now features a **complete historical data system** with:
- ✅ **Sprints 5-7 COMPLETE** (Database, API, Frontend)
- ✅ HCL Schema (3NF normalized database)
- ✅ nflverse Python package integration
- ✅ 3 base tables + 3 materialized views
- ✅ Team Detail Pages with Chart.js visualizations
- ✅ REST API with 3 endpoints (/api/hcl/*)
- ✅ 47 statistical metrics per team
- ✅ Season 2025 data through Week 8 (120+ games)
- 🚀 **Sprint 8 Coming:** Advanced analytics & betting projections

**📄 [View Interactive Dr. Foster Dashboard](index.html)** - Complete 3D visualization with 10 tabs

---

## 📚 **Assignment Documentation**

### View by Week:

1. **[Weeks 1-2: ML Model & SQLite Database](week1-2.md)**
   - Machine learning predictions
   - SQLite database creation
   - Assignment questions answered

2. **[Weeks 3-4: React & PostgreSQL Migration](weeks2-4.md)**
   - Three-tier architecture
   - PostgreSQL production database
   - Port management system
   - Logging infrastructure

3. **[Weeks 5-6: HCL Schema & Historical Data System](index.html)** ⭐ NEW
   - nflverse data integration
   - 3NF normalized database design
   - Team Detail Pages with Chart.js
   - REST API endpoints
   - Interactive 3D architecture visualization
   - Mermaid database diagrams
   - Complete technical documentation (10 tabs)

---

## 🎯 **Quick Start Guide**

### View Dr. Foster Dashboard
```
Open in browser:
file:///C:/IS330/H.C%20Lombardo%20App/dr.foster/index.html
```
- 📊 Interactive 3D Architecture
- 📈 10 tabs of documentation
- 🎨 Mermaid database diagrams
- 📱 Responsive design

### Start Application Server
```batch
cd "C:\IS330\H.C Lombardo App"
python app.py
```
- Flask API: http://localhost:5000
- Team Details: http://localhost:5000/team/BAL

### Stop Everything
```batch
STOP.bat
```

---

## 🌟 **Current Application Features**

### HCL Historical Data System (Weeks 5-6)
- **nflverse Integration** - Python package for NFL historical data
- **3NF Database** - Normalized schema with 3 tables + 3 views
- **47 Metrics** - Comprehensive team statistics
- **120+ Games** - 2025 Season through Week 8 (Week 9 in progress)

### Team Detail Pages
- **Season Overview** - 6 key stat cards
- **Interactive Charts** - Chart.js line/bar visualizations
- **Stat Selector** - Choose from 8 different metrics
- **Game History** - Week-by-week breakdown
- **Performance Trends** - Visual analytics over time

### Database Architecture
- **HCL_TEAMS** - 32 NFL teams
- **HCL_WEEKLY_STATS** - Week-by-week performance
- **HCL_GAME_RESULTS** - Individual game outcomes
- **3 Views** - Materialized views for efficient queries

### REST API Endpoints
```
GET /api/hcl/teams              # All teams
GET /api/hcl/teams/:id          # Team season stats
GET /api/hcl/teams/:id/weekly   # Weekly breakdown
GET /api/hcl/games              # Game results
```

---

## 📊 **Dr. Foster Dashboard**

### 10 Interactive Tabs
1. **📊 Overview** - Project summary and key metrics
2. **🏗️ 3D Architecture** - Interactive Three.js visualization
3. **📝 Weeks 1-2** - ML model and SQLite foundation
4. **🚀 Weeks 3-4** - React and PostgreSQL migration
5. **📱 Weeks 5-6 PWA** - HCL schema and nflverse integration
6. **� Database** - Complete schema documentation
7. **📈 Analytics** - Live data and statistics
8. **📊 DB Diagrams** - Mermaid database visualizations
9. **🎯 Milestones** - Sprint tracking and achievements
10. **🔗 GitHub** - Repository and deployment info

### Visual Features
- **3D Architecture** - Interactive node-based system diagram with Three.js
- **Mermaid Diagrams** - Database ER diagrams showing evolution from SQLite → PostgreSQL → HCL
- **Chart.js Integration** - Performance trend visualizations on team detail pages
- **Responsive Design** - Works on all screen sizes
- **Dark Theme** - Professional blue/teal color scheme

---

## 💾 **Database Status**

```sql
Database: nfl_analytics_test (HCL Schema)
Host: localhost:5432
Teams: 32
Data: 2025 Season Weeks 1-8 Complete (Week 9 in progress)
Games: 120+ games loaded
Status: ✅ 100% Complete
```

**HCL Schema Structure:**
- **HCL_TEAMS** - 32 NFL teams with metadata
- **HCL_WEEKLY_STATS** - Week-by-week performance (Weeks 1-8)
- **HCL_GAME_RESULTS** - Individual game outcomes (120+ games)
- **3 Views** - v_team_season_summary, v_weekly_performance, v_game_analysis

---

## 🎓 **Technical Skills Demonstrated**

### Frontend
- React.js (components, hooks, routing)
- Three.js (3D visualization)
- Chart.js (data visualization)
- Mermaid.js (database diagrams)
- Responsive CSS
- Client-side state management

### Backend
- Flask REST API
- PostgreSQL with 3NF normalization
- nflverse Python package
- Database view optimization
- CORS configuration
- Jinja2 templating

### Database Design
- 3NF normalized schema
- Materialized views
- Foreign key relationships
- Query optimization
- Historical data management

### DevOps
- Version control (Git/GitHub)
- Documentation (Markdown)
- Project structure organization
- Sprint-based development

---

## 📦 **Project Structure**

```
H.C Lombardo App/
├── app.py                       # Flask application server
├── db_config.py                 # PostgreSQL connection
├── espn_data_fetcher.py         # Legacy ESPN API (unused - replaced by nflverse)
├── nfl_database_loader.py       # nflverse data loader
├── api_routes_hcl.py            # HCL API endpoints
├── frontend/                    # React PWA application
│   ├── public/
│   │   ├── manifest.json        # PWA configuration
│   │   └── images/              # Local assets (1.69 MB)
│   └── src/
│       ├── App.js               # Main router
│       └── components/          # React components
├── templates/
│   ├── index.html               # React dashboard
│   └── team_detail.html         # Team pages with Chart.js
├── dr.foster/                   # 📚 Assignment documentation
│   ├── README.md                # This file
│   ├── index.html               # Interactive dashboard (10 tabs)
│   ├── week1-2.md               # ML & SQLite
│   └── weeks2-4.md              # React & PostgreSQL
├── testbed/                     # Development/testing
└── backups/                     # Automated backups
```

---

## 📈 **Progress Summary**

### Weeks 1-2: Foundation ✅
- Machine learning model (85% accuracy)
- SQLite database (3 tables)
- Basic Flask API
- Python data fetching

### Weeks 3-4: Architecture ✅
- React frontend (SPA)
- PostgreSQL migration (11-column schema)
- Three-tier architecture
- Port management (5000-5009)
- Comprehensive logging

### Weeks 5-6: Historical Data System ✅
- HCL 3NF schema design
- nflverse Python integration
- 3 base tables + 3 materialized views
- Team Detail Pages with Chart.js
- REST API (3 endpoints)
- 47 statistical metrics
- 120+ games loaded (2025 Season Weeks 1-8)
- Interactive Dr. Foster Dashboard (10 tabs)
- 3D Three.js architecture visualization
- Mermaid database diagrams
- Complete technical documentation

---

## 🔗 **Important Links**

- **GitHub:** https://github.com/AprilV/H.C.-Lombardo-App
- **Interactive Dashboard:** [dr.foster/index.html](index.html)
- **Latest Update:** October 27, 2025 (Week 9 of NFL season)

---

## 📞 **Contact**

**Student:** April V. Sykes  
**Course:** IS330  
**Semester:** Fall 2025  
**Current Week:** 9 (NFL Season)

---

**📄 For complete technical details, see:**
- **[Interactive Dr. Foster Dashboard](index.html)** ⭐ RECOMMENDED - 10 tabs with full documentation
  - 3D Architecture visualization
  - Database ER diagrams (Mermaid)
  - Complete Sprint 5-7 documentation
  - Live data analytics

**Status:** ✅ WEEKS 5-6 COMPLETE | � HCL SCHEMA LIVE | 🏈 WEEK 9 DATA READY
