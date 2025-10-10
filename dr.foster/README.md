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
- **Frontend:** React 18.2.0 responsive web interface
- **Infrastructure:** Automated refresh cycles, comprehensive logging, version control

**Development Philosophy:**
Built with professional gambling in mind - reliability, accuracy, and comprehensive data coverage are paramount. The platform is designed to handle the rigorous demands of daily betting analysis while providing the flexibility to implement and test new statistical approaches.

**Academic Context:**
Developed as part of IS330 coursework to demonstrate database design, web development, API integration, and data analysis capabilities in a real-world application scenario.

---

# H.C. Lombardo NFL Analytics - Dr. Foster Assignment

**Student:** April V  
**Course:** IS330  
**Date:** October 9, 2025  
**GitHub:** https://github.com/AprilV/H.C.-Lombardo-App

---

## Assignment Documents

📁 **Week 1: Initial Assignment**
- File: `week1.md`
- Topics: ML Model, SQLite Database, Initial Questions
- Date: September 2025

📁 **Weeks 2-4: Database Migration & Live Data**
- File: `weeks2-4.md`
- Topics: PostgreSQL Migration, React Frontend, Port Management, Logging
- Date: October 2025

---

## Quick Links

**Production System:**
- Frontend: http://localhost:3000 (React UI)
- API: http://127.0.0.1:5000 (Flask REST API)
- Database: PostgreSQL on localhost:5432

**GitHub Repository:**
https://github.com/AprilV/H.C.-Lombardo-App

**Key Files:**
- `api_server.py` - Production REST API
- `app.py` - Original Flask web app
- `scrape_teamrankings.py` - Live data scraper
- `frontend/` - React application
- `logs/` - Activity tracking
- `testbed/` - Testing environment

---

## Project Structure

```
H.C Lombardo App/
├── dr.foster/                      # Assignment documentation
│   ├── README.md                   # This overview file
│   ├── week1.md                    # Week 1 assignment
│   └── weeks2-4.md                 # Weeks 2-4 assignment
├── api_server.py                   # Production Flask REST API
├── app.py                          # Original Flask web application
├── port_manager.py                 # DHCP-inspired port management
├── nfl_database_loader.py          # PostgreSQL data loader
├── scrape_teamrankings.py          # Live data scraper
├── logging_config.py               # Logging system
├── frontend/                       # React application
│   ├── package.json
│   ├── src/
│   │   ├── App.js
│   │   └── App.css
│   └── public/
├── logs/                           # Activity logs
├── testbed/                        # Testing environment
└── docs/                           # Technical documentation
```

---

## How to Navigate This Documentation

1. **Start Here** - You're reading the overview (README.md)
2. **Week 1** - Read `week1.md` for initial assignment details
3. **Weeks 2-4** - Read `weeks2-4.md` for advanced features
4. **GitHub** - Visit repository for complete source code

---

**Last Updated:** October 9, 2025  
**Status:** ✅ All assignments complete, production system deployed
