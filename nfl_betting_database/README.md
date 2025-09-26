# NFL Betting Line Predictor Database

This folder contains a complete SQLite database system for NFL betting line prediction.

## Files Overview

### Core Database Files
- **`nfl_database_setup.py`** - Main database creation script
- **`nfl_database_utils.py`** - Database utility functions and CRUD operations
- **`sports_betting.db`** - SQLite database file (created after setup)

### Example Usage
- **`betting_predictor_example.py`** - Demonstrates betting prediction using database

## Database Schema

### Tables
1. **Teams** - NFL team information (32 teams)
2. **Games** - Game schedules and results
3. **TeamStats** - Detailed game statistics per team
4. **BettingLines** - Betting lines and predictions

### Key Features
- ✅ **Referential Integrity** - Foreign key constraints
- ✅ **Data Validation** - Check constraints
- ✅ **Performance** - Indexes on common queries
- ✅ **Sample Data** - Pre-populated for testing

## Quick Start

### 1. Create Database
```bash
python nfl_database_setup.py
```

### 2. Run Predictor Example
```bash
python betting_predictor_example.py
```

### 3. Use Database Utilities
```python
from nfl_database_utils import NFLDatabaseManager

db = NFLDatabaseManager()
teams = db.get_teams()
games = db.get_games_by_week(2024, 1)
```

## Database Operations

### Adding Data
```python
# Add team
team_id = db.add_team("Tampa Bay Buccaneers", "TB", "NFC South", "NFC")

# Add game
game_id = db.add_game(week=1, season=2024, home_team_id=1, away_team_id=2, 
                     game_date="2024-09-08")

# Add betting line
line_id = db.add_betting_line(game_id=1, spread=-3.5, total=47.5)
```

### Querying Data
```python
# Get team performance
stats = predictor.analyze_team_performance(team_id=1, season=2024)

# Predict game outcome
prediction = predictor.predict_spread(home_team_id=1, away_team_id=2, season=2024)
```

## Example Output

```
NFL Betting Line Predictor Demo
Available teams: 6
Predicting: Buffalo Bills @ Kansas City Chiefs
  Spread: KC +1.5, Total: 86.5, Confidence: 75.0%
Team Analysis:
  Kansas City Chiefs: Avg Offense: 350.0 yards
  Buffalo Bills: Avg Offense: 320.0 yards
Existing Betting Lines:
  BUF @ KC: Spread -3.5, Total 47.5
```

## Database Location

The SQLite database is created at:
```
./sports_betting.db
```

## Requirements

- Python 3.7+
- sqlite3 (built-in with Python)
- No external dependencies required

## Extending the System

The database and utilities are designed to be easily extended:
- Add more team statistics
- Implement advanced prediction algorithms  
- Add historical betting line tracking
- Include weather data or other factors