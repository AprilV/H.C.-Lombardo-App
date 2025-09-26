# NFL Betting Line Predictor Database

This project sets up a comprehensive SQLite database for an NFL betting line predictor application.

## Database Schema

### Tables Created

#### 1. **Teams**
Stores NFL team information:
- `team_id` (PRIMARY KEY) - Unique team identifier
- `name` - Full team name (e.g., "Kansas City Chiefs")
- `abbreviation` - Team abbreviation (e.g., "KC") 
- `division` - Division name (e.g., "AFC West")
- `conference` - Conference ("AFC" or "NFC")
- `city` - Team city
- `created_at` - Timestamp

#### 2. **Games**
Stores game information:
- `game_id` (PRIMARY KEY) - Unique game identifier
- `week` - NFL week (1-22)
- `season` - NFL season year
- `home_team_id` - Foreign key to Teams table
- `away_team_id` - Foreign key to Teams table
- `game_date` - Game date
- `game_time` - Game time
- `home_score` - Home team final score
- `away_score` - Away team final score
- `game_status` - Game status ("Scheduled", "Final", etc.)
- `created_at` - Timestamp

#### 3. **TeamStats**
Stores detailed team statistics per game:
- `stat_id` (PRIMARY KEY) - Unique stat identifier
- `game_id` - Foreign key to Games table
- `team_id` - Foreign key to Teams table
- `offense_yards` - Total offensive yards
- `defense_yards` - Total yards allowed
- `turnovers` - Number of turnovers
- `passing_yards` - Passing yards
- `rushing_yards` - Rushing yards
- `first_downs` - First downs
- `third_down_conversions` - 3rd down conversions
- `third_down_attempts` - 3rd down attempts
- `red_zone_conversions` - Red zone conversions
- `red_zone_attempts` - Red zone attempts
- `penalties` - Number of penalties
- `penalty_yards` - Penalty yards
- `time_of_possession` - Time of possession
- `created_at` - Timestamp

#### 4. **BettingLines**
Stores betting lines and predictions:
- `line_id` (PRIMARY KEY) - Unique line identifier
- `game_id` - Foreign key to Games table
- `spread` - Point spread
- `total` - Over/under total points
- `home_moneyline` - Home team moneyline
- `away_moneyline` - Away team moneyline
- `user_formula_applied` - Boolean flag for custom predictions
- `prediction_confidence` - Confidence level (0.0-1.0)
- `sportsbook` - Source sportsbook
- `line_date` - When line was set
- `created_at` - Timestamp

## Files

### Core Database Files
- **`nfl_database_setup.py`** - Main database setup script
- **`nfl_database_utils.py`** - Database utility functions and operations
- **`sports_betting.db`** - SQLite database file (created after running setup)

### Example Usage
- **`betting_predictor_example.py`** - Demonstrates betting line prediction using database

## Usage

### 1. Create Database
```bash
python nfl_database_setup.py
```

This will:
- Create SQLite database (`sports_betting.db`)
- Create all required tables with proper constraints
- Insert sample data for testing
- Display database information

### 2. Use Database Utilities
```python
from nfl_database_utils import NFLDatabaseManager

db_manager = NFLDatabaseManager()

# Add a team
team_id = db_manager.add_team("Tampa Bay Buccaneers", "TB", "NFC South", "NFC", "Tampa Bay")

# Add a game
game_id = db_manager.add_game(week=1, season=2024, home_team_id=1, away_team_id=2, game_date="2024-09-08")

# Add betting line
line_id = db_manager.add_betting_line(game_id=1, spread=-3.5, total=47.5, sportsbook="DraftKings")

# Get teams
teams = db_manager.get_teams()

# Get games for a week
games = db_manager.get_games_by_week(2024, 1)
```

### 3. Run Betting Predictor
```bash
python betting_predictor_example.py
```

## Features

### Database Features
- ✅ **ACID Compliance** - Full SQLite transaction support
- ✅ **Referential Integrity** - Foreign key constraints
- ✅ **Data Validation** - Check constraints for valid data
- ✅ **Indexes** - Performance optimization for common queries
- ✅ **Sample Data** - Pre-populated with NFL teams and example data

### Utility Features
- ✅ **Easy CRUD Operations** - Simple functions for database operations
- ✅ **Connection Management** - Automatic connection handling
- ✅ **Error Handling** - Comprehensive error management
- ✅ **Query Helpers** - Pre-built queries for common operations

### Predictor Features
- ✅ **Team Analysis** - Statistical team performance analysis
- ✅ **Spread Prediction** - Basic spread prediction algorithm
- ✅ **Total Prediction** - Over/under total prediction
- ✅ **Confidence Scoring** - Prediction confidence levels

## Database Statistics

After running the setup:
- **Teams**: 6 NFL teams (sample data)
- **Games**: 2 sample games
- **TeamStats**: 4 stat records (2 teams × 2 games)
- **BettingLines**: 2 betting lines

## Requirements

- Python 3.7+
- SQLite3 (included with Python)
- No external dependencies required

## Database Location

The SQLite database file is created at:
```
C:\IS330\H.C. Lombardo App\sports_betting.db
```

You can connect to this database using any SQLite client or the provided Python utilities.