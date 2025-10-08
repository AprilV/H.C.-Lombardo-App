# H.C. Lombardo NFL Analytics - Assignment Solution

## Assignment Requirements Completed ✅

### 1. ML Model from HuggingFace ✅
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
