# External API Integration

This folder contains integrations with external sports APIs, specifically the API-SPORTS NFL API.

## Files Overview

### Core Integration Files
- **`nfl_api_sports_client.py`** - Main client for API-SPORTS NFL API
- **`nfl_data_integration.py`** - Combines external API with local database
- **`api_config.py`** - Configuration and API key management

## Required Functions Implementation

### ✅ **`get_team_stats(season, team_id)`**
Fetches comprehensive team statistics from API-SPORTS:

```python
from nfl_data_integration import get_team_stats

# Get Kansas City Chiefs stats for 2024 season
stats = get_team_stats(2024, 1)

# Returns:
{
    "team_info": {
        "external_id": 1,
        "name": "Kansas City Chiefs", 
        "season": 2024,
        "data_source": "API-SPORTS"
    },
    "season_record": {
        "wins": 14,
        "losses": 3, 
        "win_percentage": 0.824
    },
    "offensive_performance": {
        "points_per_game": 28.5,
        "total_points": 484
    },
    "defensive_performance": {
        "points_allowed_per_game": 19.2,
        "total_points_allowed": 326
    }
}
```

### ✅ **`get_game_odds(game_id)`**
Fetches betting odds for specific games:

```python
from nfl_data_integration import get_game_odds

# Get odds for a specific game
odds = get_game_odds(12345)

# Returns:
{
    "game_info": {
        "external_game_id": 12345,
        "home_team": "Kansas City Chiefs",
        "away_team": "Buffalo Bills",
        "game_date": "2024-09-07T20:20:00"
    },
    "sportsbook": {
        "name": "DraftKings",
        "book_id": 8
    },
    "betting_markets": {
        "spread": {
            "home_spread": -2.5,
            "home_odds": "-110",
            "away_spread": 2.5, 
            "away_odds": "-110"
        },
        "total": {
            "points": 54.5,
            "over_odds": "-110",
            "under_odds": "-110"
        },
        "moneyline": {
            "home_odds": "-140",
            "away_odds": "+120"
        }
    }
}
```

## API Setup

### 1. Get API Key
1. Visit [RapidAPI - American Football](https://rapidapi.com/api-sports/api/american-football/)
2. Sign up for free account
3. Subscribe to the free tier (100 requests/day)
4. Copy your API key

### 2. Configure API Key

**Option A: Environment Variable (Recommended)**
```bash
# Windows Command Prompt
set API_SPORTS_NFL_KEY=your_actual_api_key_here

# Windows PowerShell  
$env:API_SPORTS_NFL_KEY="your_actual_api_key_here"

# Linux/Mac
export API_SPORTS_NFL_KEY=your_actual_api_key_here
```

**Option B: Direct Configuration**
Edit `api_config.py`:
```python
self.api_sports_nfl_key = "your_actual_api_key_here"
```

### 3. Install Dependencies
```bash
pip install requests
```

## Usage Examples

### Basic Team Stats
```python
from nfl_data_integration import get_team_stats

# Get team statistics
stats = get_team_stats(season=2024, team_id=1)
if "error" not in stats:
    print(f"Team: {stats['team_info']['name']}")
    print(f"Record: {stats['season_record']['wins']}-{stats['season_record']['losses']}")
    print(f"PPG: {stats['offensive_performance']['points_per_game']}")
```

### Game Betting Odds
```python
from nfl_data_integration import get_game_odds

# Get betting odds for a game
odds = get_game_odds(game_id=12345)
if "error" not in odds:
    game = odds['game_info']
    markets = odds['betting_markets']
    
    print(f"Game: {game['away_team']} @ {game['home_team']}")
    if markets['spread']:
        print(f"Spread: {markets['spread']['home_spread']}")
    if markets['total']:
        print(f"Total: {markets['total']['points']}")
```

### Complete Demo
```python
# Run the complete integration demo
python nfl_data_integration.py
```

## Features

### ✅ **Authentication**
- RapidAPI key authentication
- Environment variable support
- Key validation and error handling

### ✅ **Request Library Usage**
- Full `requests` library implementation
- Proper HTTP error handling
- Timeout and retry logic
- Rate limiting compliance

### ✅ **Data Parsing**
- Clean Python object returns
- JSON response parsing
- Error handling for malformed data
- Mock data fallback for testing

### ✅ **Error Handling**
- HTTP status code checking
- API-specific error parsing
- Network timeout handling
- Graceful degradation to mock data

### ✅ **Integration**
- Combines with local database
- Data normalization and cleaning
- Timestamp tracking
- Source attribution

## API Endpoints Used

1. **Teams Statistics**: `/teams/statistics`
   - Season-long team performance data
   - Offensive and defensive metrics
   - Win/loss records

2. **Game Odds**: `/odds`
   - Real-time betting lines
   - Multiple sportsbook data
   - Spread, total, and moneyline odds

## Rate Limits

- **Free Tier**: 100 requests/day
- **Rate Limiting**: 1 second between requests
- **Auto-retry**: On rate limit exceeded
- **Error Handling**: Fallback to cached/mock data

## Mock Data Mode

When no API key is configured, the system automatically switches to mock data mode:

- Realistic sample data for testing
- Same data structure as real API
- Allows development without API costs
- Seamless transition to live data

## Testing

```bash
# Test API configuration
python api_config.py

# Test full integration
python nfl_data_integration.py

# Test individual functions
python -c "from nfl_data_integration import get_team_stats; print(get_team_stats(2024, 1))"
```

## Production Considerations

1. **API Key Security**: Use environment variables, never commit keys
2. **Rate Limiting**: Respect API limits, implement backoff strategies
3. **Caching**: Cache responses to reduce API calls
4. **Error Handling**: Graceful degradation for API outages
5. **Monitoring**: Track API usage and error rates

## Cost Management

- Free tier provides 100 requests/day
- Cache frequently requested data
- Use mock data for development/testing
- Monitor usage through RapidAPI dashboard