# H.C. Lombardo NFL Analytics Dashboard
**IS330 - Week 1 & Week 2 Assignment Submission**

**Student**: April V. Sykes  
**Professor**: Stephen Foster  
**Course**: IS330 - Database and Machine Learning Systems  
**Assignment**: Week 1-2 Foundation Project  
**Date Submitted**: September 26, 2025  
**Technical Implementation**: GitHub Copilot (AI-Assisted Development)

---

## 📝 **ASSIGNMENT COMPLETION STATUS**

### **✅ WEEK 1 ASSIGNMENT - COMPLETED**
**Due Date**: Week 1 of Class  
**Completion Date**: September 26, 2025  
**Status**: ✅ SUBMITTED

### **✅ WEEK 2 ASSIGNMENT - COMPLETED** 
**Due Date**: Week 2 of Class  
**Completion Date**: September 26, 2025  
**Status**: ✅ SUBMITTED 

---

## 🎯 **PROFESSOR FOSTER - QUICK REVIEW CHECKLIST**

### **Required Elements** ✅ **ALL COMPLETED**
- ✅ **AI Development Environment**: VSCode + GitHub Copilot + Claude Sonnet
- ✅ **GitHub Repository**: [H.C.-Lombardo-App](https://github.com/AprilV/H.C.-Lombardo-App)
- ✅ **Machine Learning Models**: Text classification + NFL predictions
- ✅ **Database System**: SQLite with NFL team data
- ✅ **Data Source**: NFL statistics and team information
- ✅ **Working Prototype**: Full web application with database integration

### **Bonus Achievements** 🌟 
- 🌟 **Full-Stack Web Application**: Professional FastAPI dashboard
- 🌟 **All 32 NFL Teams**: Complete database with official logos
- 🌟 **Interactive UI**: Responsive design with navigation
- 🌟 **API Documentation**: Auto-generated Swagger docs
- 🌟 **Educational Compliance**: Proper copyright attribution

---

## 🚀 **DEMO THE APPLICATION**

**Professor Foster - To test the application:**

```bash
# Navigate to the project
cd "c:\IS330\H.C. Lombardo App\apis"

# Run the dashboard
python hc_lombardo_dashboard_official.py

# Open in browser
http://localhost:8004
```

**Live Application Features:**
- **Dashboard Home**: Top NFL team rankings with official logos
- **Teams Page**: All 32 NFL teams with statistics  
- **Predictions**: Mock betting analysis
- **API Docs**: Interactive documentation at `/docs`
- **API-First Architecture** - RESTful endpoints with Swagger documentation
- **Educational Compliance** - Copyright attribution and fair use documentation

---

## 🏗️ **Technical Architecture**

### **Backend Framework**
- **FastAPI** - Modern, high-performance Python web framework
- **Uvicorn ASGI Server** - Production-ready async server implementation
- **SQLite Database** - Lightweight, embedded database for development
- **Pydantic Models** - Type-safe data validation and serialization

### **Frontend Implementation**
- **Embedded HTML/CSS/JavaScript** - Self-contained responsive design
- **Professional Styling** - Modern UI with gradient backgrounds and animations
- **Mobile-Responsive** - Adaptive layout for all device sizes
- **Interactive Navigation** - Hamburger menu with smooth sidebar transitions

### **Data Integration**
- **ESPN CDN Integration** - Official NFL team logos via `a.espncdn.com`
- **Structured Data Schema** - Normalized team statistics and metadata
- **Error Handling** - Graceful fallback for missing images and data
- **Real-time Updates** - Dynamic timestamp tracking for data freshness

---

## 📁 **Project Structure**

```
H.C. Lombardo App/
├── apis/                              # FastAPI Applications
│   ├── hc_lombardo_dashboard_official.py    # Main dashboard (PRODUCTION)
│   ├── hc_lombardo_dashboard_clean.py       # Clean version backup
│   ├── fastapi_template_inheritance.py      # Template experiments
│   ├── nfl_betting_api.py                   # Betting API endpoints
│   └── comprehensive_test.py                # Testing utilities
├── nfl_betting_database/              # ML Prediction Models
│   ├── betting_predictor_example.py         # Betting algorithms
│   ├── nfl_analysis_tool.py                 # Data analysis tools
│   └── nfl_betting_database.db              # SQLite database
├── text_classification/               # NLP & Text Analysis
│   ├── [various ML text models]
│   └── [classification algorithms]
├── scripts/                           # Utility Scripts
│   ├── launcher.py                          # Application launcher
│   └── [additional utilities]
├── templates/                         # HTML Templates
│   └── base.html                            # Base template structure
├── organized_project/                 # Archive & Backups
└── README.md                          # This documentation
```

---

## 🎨 **Key Achievements**

### **Professional Development Practices**
- **AI-First Development** - Extensive use of GitHub Copilot throughout
- **Version Control** - Proper Git workflow with meaningful commits
- **Code Organization** - Logical project structure and modular design
- **Documentation** - Comprehensive README and inline code comments

### **Technical Excellence**
- **Full-Stack Implementation** - Complete web application from database to frontend
- **Official NFL Integration** - All 32 teams with authentic logos and branding
- **Educational Compliance** - Proper copyright attribution and fair use
- **Production Ready** - Error handling, health monitoring, and API documentation

### **Advanced Features**
- **Interactive Dashboard** - Professional UI with smooth animations
- **Responsive Design** - Mobile-friendly layout and navigation
- **API-First Architecture** - RESTful endpoints with auto-generated documentation
- **Real-time Data** - Dynamic updates with timestamp tracking

---

## 🔧 **Installation & Setup**

### **Prerequisites**
- Python 3.11+
- Git for version control
- VSCode with GitHub Copilot (recommended)

### **Quick Start**
```bash
# Clone the repository
git clone https://github.com/AprilV/H.C.-Lombardo-App.git
cd "H.C. Lombardo App"

# Install dependencies
pip install fastapi uvicorn sqlite3

# Launch the application
cd apis
python hc_lombardo_dashboard_official.py

# Access the dashboard
# Open browser to: http://localhost:8004
```

### **API Documentation**
- **Interactive Docs**: `http://localhost:8004/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8004/redoc` (ReDoc)
- **Health Check**: `http://localhost:8004/health`

---

## 📊 **Data Analytics Capabilities**

### **NFL Team Statistics**
- **Offensive Rankings** - Points per game (PPG) for all 32 teams
- **Defensive Rankings** - Points allowed per game (PA/G) analysis
- **Division Analysis** - AFC/NFC divisional performance comparisons
- **Season Records** - Win-loss records with current standings

### **Machine Learning Integration**
- **Predictive Modeling** - Game outcome forecasting algorithms
- **Text Classification** - NLP analysis for sports commentary
- **Betting Analytics** - Statistical models for wagering insights
- **Performance Metrics** - Advanced team and player analytics

---

## 🎓 **Educational Value**

### **Database Concepts Demonstrated**
- **Schema Design** - Proper normalization and relationship modeling
- **Data Integrity** - Constraints and validation rules
- **Query Optimization** - Efficient data retrieval patterns
- **CRUD Operations** - Complete Create, Read, Update, Delete functionality

### **Machine Learning Applications**
- **Supervised Learning** - Classification and regression models
- **Feature Engineering** - Sports statistics transformation
- **Model Evaluation** - Performance metrics and validation
- **Real-world Integration** - ML models serving web applications

### **Software Engineering Practices**
- **AI-Assisted Development** - Modern development workflow with GitHub Copilot
- **API Design** - RESTful architecture principles
- **Frontend Integration** - Full-stack web development
- **Documentation** - Professional project documentation standards

---

## 🔮 **Future Development Roadmap**

### **Weeks 3-12 Planned Enhancements**
- **PostgreSQL Migration** - Production-scale database upgrade
- **Real-time Data APIs** - Live NFL statistics integration
- **Advanced ML Models** - Deep learning for complex predictions  
- **Cloud Deployment** - AWS/Azure production deployment
- **User Authentication** - Secure user management system
- **Advanced Visualizations** - Interactive charts and graphs

---

## 📚 **Academic Compliance**

### **Educational Fair Use**
- **Official NFL Logos** used under educational fair use doctrine
- **Proper Attribution** - ESPN CDN sources credited appropriately  
- **Educational Purpose** - Clear documentation of academic intent
- **Copyright Compliance** - Respect for intellectual property rights

### **AI Development Transparency**
- **GitHub Copilot Integration** - Extensive AI assistance acknowledged
- **Human-AI Collaboration** - Clear delineation of AI-assisted development
- **Learning Enhancement** - AI tools used to accelerate educational outcomes
- **Professional Standards** - Industry-standard development practices

---

## 👤 **Developer Information**

**April V. Sykes**  
*Owner & Primary Developer*  
- Project conception and requirements definition
- Database schema design and implementation
- UI/UX design and user experience optimization
- Project management and academic compliance

**GitHub Copilot (AI Assistant)**  
*Technical Implementation Partner*  
- Code generation and optimization
- FastAPI framework implementation  
- Frontend styling and responsive design
- Documentation and testing assistance

---

## 📞 **Contact & Support**

**Academic Inquiries**: Professor Stephen Foster  
**Technical Questions**: April V. Sykes  
**Repository**: [H.C.-Lombardo-App](https://github.com/AprilV/H.C.-Lombardo-App)  

---

## 📜 **License & Attribution**

**Educational Use Only**  
This project is developed for academic purposes in IS330 coursework. Official NFL team logos are used under educational fair use doctrine with proper attribution to ESPN and the National Football League.

**AI Development Acknowledgment**  
This project extensively utilized GitHub Copilot and Claude Sonnet 4 for technical implementation, demonstrating modern AI-assisted software development practices as encouraged in IS330 curriculum.

---

*Last Updated: September 26, 2025*  
*Project Status: Week 2 Complete - Foundation Established*  
*Next Milestone: Week 3 Advanced Features*
│   ├── nfl_database_setup.py     #   Create database
│   ├── betting_predictor_example.py # Prediction demo
│   ├── nfl_database_utils.py     #   Database utilities
│   └── sports_betting.db         #   SQLite database
├── external_apis/               # 🔗 External API Integration (NEW!)
│   ├── nfl_api_sports_client.py #   API-SPORTS NFL client
│   ├── nfl_data_integration.py  #   External + local data integration
│   └── api_config.py            #   API key management
│
│   ├── text_classification_api.py #   FastAPI for text classification
│   ├── nfl_betting_api.py        #   FastAPI for NFL predictions
│   ├── api_client_examples.py    #   Client usage examples
│   └── start_apis.py             #   Launch both APIs
│
│   ├── README.md                 #   Text classification docs
│   └── DATABASE_README.md        #   Database documentation
│
├── launcher.py                   # 🎯 Project launcher menu
├── run_launcher.bat              # 🪟 Windows launcher
├── requirements.txt              # 📦 Dependencies
└── README.md                     # 📖 This file
```

## Projects

### 1. Text Classification with HuggingFace Transformers
**Location**: `text_classification/`

A comprehensive collection of text classification examples using HuggingFace Transformers library:
- Multiple model implementations (DistilBERT, BERT, RoBERTa)
- Step-by-step tutorials showing tokenization, inference, and result processing
- Simple to advanced examples for different use cases
- Sentiment analysis and text classification demos

**Key Features**:
- ✅ Pre-trained models from HuggingFace
- ✅ Manual tokenization examples
- ✅ Raw logit extraction and processing
- ✅ Multiple difficulty levels (minimal to detailed)

### 2. NFL Betting Line Predictor Database
**Location**: `nfl_betting_database/`

A complete SQLite database system for NFL betting line prediction:
- Comprehensive database schema for teams, games, statistics, and betting lines
- Database utilities for easy data management
- Example betting predictor with basic algorithms
- Full CRUD operations and query helpers

**Key Features**:
- ✅ SQLite database with proper constraints
- ✅ NFL teams, games, and statistics tracking
- ✅ Betting lines storage and prediction
- ✅ Sample data and working examples

### 🆕 3. REST APIs
**Location**: `apis/`

Professional REST APIs built with FastAPI:
- **Text Classification API**: Sentiment analysis via HTTP endpoints
- **NFL Betting API**: Database operations and predictions via REST
- Interactive API documentation with Swagger UI
- Client examples and usage demonstrations

**Key Features**:
- ✅ FastAPI framework with automatic documentation
- ✅ Multiple model support (DistilBERT, BERT, RoBERTa)
- ✅ Batch processing capabilities
- ✅ NFL database integration via API
### 🆕 4. External API Integration
**Location**: `external_apis/`

Integration with external sports data APIs (API-SPORTS NFL):
- Real-time team statistics and performance data
- Live betting odds from multiple sportsbooks  
- Data integration with local database
- Mock data fallback for testing without API costs

**Key Features**:
- ✅ API-SPORTS NFL API client with authentication
- ✅ `get_team_stats(season, team_id)` function
- ✅ `get_game_odds(game_id)` function  
- ✅ Clean Python object returns
- ✅ Rate limiting and error handling

## Getting Started

### Prerequisites
```bash
pip install -r requirements.txt
```

### Text Classification
```bash
cd text_classification
python minimal_example.py          # Quick start
python step_by_step_classification.py  # Detailed tutorial
```

### NFL Database
```bash
cd nfl_betting_database
python nfl_database_setup.py       # Create database
python betting_predictor_example.py  # Run predictor
```

## Documentation

Detailed documentation for each project can be found in the `docs/` folder:
- `README.md` - Text classification documentation
- `DATABASE_README.md` - NFL database documentation

## Requirements

- Python 3.7+
- transformers
- torch
- numpy
- sqlite3 (built-in)
- **🆕 API dependencies**: fastapi, uvicorn, pydantic, requests

## Author

AprilV - IS330 Course Projects

## Repository

- **Name**: H.C.-Lombardo-App
- **Owner**: AprilV
- **Branch**: master