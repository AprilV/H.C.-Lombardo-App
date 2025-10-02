# H.C. Lombardo NFL Analytics Dashboard
**IS330 - Database and Machine Learning Systems**

**Student**: April V. Sykes  
**Professor**: Stephen Foster  
**Date**: October 1, 2025  
**Status**: ✅ **LIVE DATA INTEGRATION COMPLETE**

---

## 🎯 **PROFESSOR FOSTER - ASSIGNMENT REVIEW**

### **✅ REQUIREMENTS COMPLETED**
- ✅ **AI Development Environment**: VSCode + GitHub Copilot 
- ✅ **Database System**: SQLite with **live NFL data** (not mock)
- ✅ **Machine Learning**: Text classification models
- ✅ **Working Application**: Full-stack web dashboard
- ✅ **GitHub Repository**: [H.C.-Lombardo-App](https://github.com/AprilV/H.C.-Lombardo-App)

---

## 🚀 **QUICK DEMO - 30 SECONDS**

```bash
# Navigate to project
cd "C:\IS330\H.C. Lombardo App\apis"

# Start dashboard  
python hc_lombardo_dashboard_official.py

# Open browser
http://localhost:8004
```

**What you'll see**: Live NFL dashboard with 32 teams, real ESPN data, interactive UI

---

## 🗄️ **DATABASE - LIVE DATA (NO MOCK)**

### **Location**: `nfl_betting_database/enhanced_nfl_betting.db`
### **Data Source**: ESPN API (live data collection)
### **Size**: 106 KB with real NFL data

### **Tables with Data**
| Table | Records | Content |
|-------|---------|---------|
| **Teams** | 32 | All NFL teams, logos, divisions |
| **Games** | 14 | Week 5 schedule from ESPN |
| **data_collection_log** | 7 | API collection history |

### **Python Access**
```python
import sqlite3

# Connect to database
conn = sqlite3.connect('nfl_betting_database/enhanced_nfl_betting.db')
cursor = conn.cursor()

# View teams (32 NFL teams)
cursor.execute("SELECT name, abbreviation, conference FROM Teams LIMIT 5")
print(cursor.fetchall())

# View games (14 current week games)  
cursor.execute("SELECT home_team_id, away_team_id, date FROM Games LIMIT 3")
print(cursor.fetchall())

conn.close()
```

### **GUI Database Viewer**
- **Installed**: DB Browser for SQLite
- **Quick Access**: Double-click `open_database.bat`
- **Manual**: Open DB Browser → Load `enhanced_nfl_betting.db`

---

## 🤖 **MACHINE LEARNING COMPONENTS**

### **Text Classification**
- **Location**: `text_classification/`
- **Models**: DistilBERT, BERT, RoBERTa
- **Purpose**: Sports commentary analysis

### **NFL Predictions** 
- **Location**: `nfl_betting_database/`
- **Purpose**: Game outcome forecasting
- **Integration**: Database-driven predictions

---

## 🏗️ **TECHNICAL STACK**

- **Backend**: FastAPI (Python)
- **Database**: SQLite with live ESPN data
- **Frontend**: Embedded HTML/CSS/JS
- **AI Tools**: GitHub Copilot, HuggingFace Transformers
- **Data Sources**: ESPN API (32 teams, current games)

---

## 📁 **PROJECT STRUCTURE**

```
H.C. Lombardo App/
├── apis/
│   ├── hc_lombardo_dashboard_official.py  # Main dashboard
│   └── live_data_collector.py             # ESPN data collection
├── nfl_betting_database/
│   └── enhanced_nfl_betting.db            # Live NFL data
├── text_classification/                   # ML models
└── README.md                              # This file
```

---

## 🎓 **ACADEMIC VALUE**

### **Database Concepts**
- **Live API Integration**: ESPN data collection
- **Schema Design**: Normalized NFL database
- **CRUD Operations**: Full database functionality

### **Machine Learning**
- **Text Classification**: Multiple transformer models
- **Predictive Analytics**: Sports forecasting
- **Real-world Application**: Database-driven ML

### **Software Engineering**
- **AI-Assisted Development**: GitHub Copilot workflow
- **Full-Stack Development**: API to frontend
- **Professional Standards**: Documentation, testing

---

## 🔧 **INSTALLATION & TESTING**

```bash
# Clone repository
git clone https://github.com/AprilV/H.C.-Lombardo-App.git
cd "H.C. Lombardo App"

# Install dependencies
pip install fastapi uvicorn sqlite3 transformers torch

# Run application
cd apis
python hc_lombardo_dashboard_official.py

# Test database
python ../view_database.py
```

---

## 📊 **KEY ACHIEVEMENTS**

- ✅ **Live Data Integration**: Transitioned from mock to real ESPN data
- ✅ **Professional UI**: Modern, responsive dashboard
- ✅ **Database Population**: 32 teams + current games via API
- ✅ **Full-Stack Application**: Backend API + Frontend dashboard
- ✅ **Educational Compliance**: Proper attribution and fair use

---

**Repository**: [https://github.com/AprilV/H.C.-Lombardo-App](https://github.com/AprilV/H.C.-Lombardo-App)  
**Live Demo**: Start application → http://localhost:8004  
**Database Access**: See Python code above or use DB Browser