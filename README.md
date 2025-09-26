# H.C. Lombardo App

This repository contains two main projects developed for IS330 coursework.

## 🚀 Quick Start

### Option 1: Use the Launcher (Recommended)
```bash
python launcher.py
# or double-click run_launcher.bat on Windows
```

### Option 2: Run Projects Directly
```bash
# Text Classification
cd text_classification
python minimal_example.py

# NFL Database
cd nfl_betting_database
python nfl_database_setup.py

# 🆕 REST APIs
cd apis
python text_classification_api.py  # Port 8000
python nfl_betting_api.py          # Port 8001

# 🔗 External API Integration  
cd external_apis
python nfl_data_integration.py     # Test API-SPORTS integration
```

## Project Structure

```
H.C. Lombardo App/
├── text_classification/          # 🤖 HuggingFace ML Projects
│   ├── minimal_example.py        #   Quick start (25 lines)
│   ├── step_by_step_classification.py #   Detailed tutorial
│   ├── bert_step_by_step.py      #   BERT implementation  
│   ├── text_classification.py    #   RoBERTa sentiment
│   └── [8 more examples]         #   Various implementations
│
├── nfl_betting_database/         # 🏈 NFL Database System
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