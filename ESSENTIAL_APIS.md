# Essential APIs - H.C. Lombardo Assignment

## Core Assignment APIs (DO NOT DELETE)

### 1. Main Dashboard API
- **File**: `hc_lombardo_dashboard_official.py`
- **Port**: 8004
- **Purpose**: Primary assignment demo with GUI, navigation, NFL team pages, predictions
- **Status**: ✅ Running
- **Assignment Critical**: YES - Main demo for Professor Foster

### 2. Text Classification API  
- **File**: `text_classification_api.py`
- **Port**: 8003
- **Purpose**: Machine Learning component using HuggingFace models (DistilBERT, BERT, RoBERTa)
- **Status**: ✅ Running
- **Assignment Critical**: YES - ML requirement fulfillment

### 3. NFL Betting API
- **File**: `nfl_betting_api.py`
- **Purpose**: Core data API for NFL information
- **Status**: ✅ Integrated with main dashboard
- **Assignment Critical**: YES - Core functionality

## Supporting Files

### Status Monitoring
- **File**: `simple_status_dashboard.py`
- **Purpose**: Monitor API health and status
- **Status**: ✅ Updated to reflect clean architecture

### Data Collection
- **File**: `live_data_collector.py`
- **Purpose**: ESPN API integration for live NFL data
- **Status**: ✅ Populating database

## Removed Files (Cleanup Complete)
- `demo_server.py` - Demo file, not assignment related
- `fastapi_jinja2_demo.py` - Demo file, not assignment related  
- `launch_homepage_demo.py` - Demo file, not assignment related
- `nfl_api_demo.py` - Demo file, not assignment related
- `hc_lombardo_dashboard.py` - Duplicate of official dashboard
- `hc_lombardo_dashboard_clean.py` - Another duplicate

## Database
- **File**: `enhanced_nfl_betting.db` (106KB)
- **Status**: ✅ Populated with live ESPN data
- **Contents**: 32 teams, 14 games, audit logs

---
**Last Updated**: December 26, 2024  
**Status**: Clean codebase ready for assignment submission