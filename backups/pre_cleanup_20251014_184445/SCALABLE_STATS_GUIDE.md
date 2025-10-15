# Scalable Stats System - Implementation Guide

## 🎯 Problem Solved

**Before**: Adding new stats required:
- Altering database schema (ADD COLUMN for each stat)
- Updating data fetcher code
- Modifying API responses
- Changing frontend displays
- **Result**: Manual work for EVERY new stat

**After**: Adding new stats requires:
- Fetch the data from API/scraping
- Merge into `stats` JSONB column
- Add to `stats_metadata` table
- **Result**: NO schema changes, seamless scaling to 100+ stats

---

## 📊 Database Architecture

### Teams Table (Hybrid Approach)
```sql
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name TEXT,
    abbreviation TEXT UNIQUE,
    
    -- Legacy columns (for backward compatibility)
    wins INTEGER,
    losses INTEGER,
    ppg REAL,
    pa REAL,
    games_played INTEGER,
    
    -- NEW: Extensible stats storage
    stats JSONB DEFAULT '{}'::jsonb
);
```

### Stats Metadata Table (Tracks Available Stats)
```sql
CREATE TABLE stats_metadata (
    stat_key VARCHAR(100) PRIMARY KEY,      -- e.g., 'offense.passing_yards_per_game'
    stat_name VARCHAR(200),                  -- e.g., 'Passing Yards Per Game'
    category VARCHAR(50),                    -- e.g., 'offense', 'defense', 'special_teams'
    data_type VARCHAR(20),                   -- e.g., 'float', 'integer', 'percentage'
    description TEXT,                        -- Human-readable description
    source VARCHAR(100),                     -- e.g., 'ESPN', 'TeamRankings', 'SportsDataIO'
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🏗️ JSONB Structure

```json
{
  "record": {
    "wins": 5,
    "losses": 2,
    "games_played": 7,
    "win_percentage": 0.714
  },
  "offense": {
    "points_per_game": 28.5,
    "total_points": 200,
    "yards_per_game": 385.2,
    "passing_yards_per_game": 265.3,
    "rushing_yards_per_game": 119.9,
    "turnovers": 5,
    "third_down_conversions": 45,
    "third_down_attempts": 92,
    "red_zone_efficiency": 0.625,
    "time_of_possession": "32:15"
  },
  "defense": {
    "points_allowed_per_game": 18.2,
    "total_points_allowed": 127,
    "yards_allowed_per_game": 315.8,
    "takeaways": 12,
    "sacks": 22,
    "interceptions": 8,
    "forced_fumbles": 4
  },
  "special_teams": {
    "field_goal_percentage": 0.857,
    "punt_average": 45.3,
    "kickoff_return_average": 23.8
  },
  "betting": {
    "spread_record_ats": "4-3",
    "over_under_record": "5-2",
    "money_line_wins": 5
  }
}
```

---

## 📝 How to Add New Stats (Step-by-Step)

### Example: Adding Passing Stats

#### Step 1: Fetch the Data
```python
def fetch_passing_stats():
    """Fetch passing stats from TeamRankings or API"""
    stats = {}
    
    # Option A: Web scraping
    response = requests.get("https://www.teamrankings.com/nfl/stat/passing-yards-per-game")
    soup = BeautifulSoup(response.text, 'html.parser')
    # ... parse table ...
    
    # Option B: API call (SportsDataIO, RapidAPI, etc.)
    response = requests.get("https://api.sportsdata.io/v3/nfl/stats/TeamSeasonStats/2025")
    data = response.json()
    
    for team in data:
        stats[team['abbreviation']] = {
            'passing_yards_per_game': team['PassingYardsPerGame'],
            'completions': team['PassingCompletions'],
            'attempts': team['PassingAttempts'],
            'completion_percentage': team['PassingCompletions'] / team['PassingAttempts'],
            'touchdowns': team['PassingTouchdowns'],
            'interceptions': team['PassingInterceptions'],
            'qb_rating': team['PasserRating']
        }
    
    return stats
```

#### Step 2: Merge Into Database
```python
def update_passing_stats(passing_stats):
    """Add passing stats to teams' JSONB column"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for team_abbr, stats in passing_stats.items():
        # Merge into existing stats using || operator
        cursor.execute("""
            UPDATE teams
            SET stats = jsonb_set(
                stats, 
                '{offense,passing}',
                %s::jsonb,
                true
            )
            WHERE abbreviation = %s
        """, (json.dumps(stats), team_abbr))
    
    conn.commit()
    conn.close()
```

#### Step 3: Add to Metadata
```python
def register_passing_stats():
    """Register new stats in metadata table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    new_stats = [
        ('offense.passing.yards_per_game', 'Passing Yards Per Game', 'offense', 'float', 'Average passing yards per game', 'SportsDataIO'),
        ('offense.passing.completions', 'Completions', 'offense', 'integer', 'Total completions', 'SportsDataIO'),
        ('offense.passing.attempts', 'Attempts', 'offense', 'integer', 'Total pass attempts', 'SportsDataIO'),
        ('offense.passing.completion_percentage', 'Completion %', 'offense', 'percentage', 'Completion percentage', 'Calculated'),
        ('offense.passing.touchdowns', 'Passing TDs', 'offense', 'integer', 'Passing touchdowns', 'SportsDataIO'),
        ('offense.passing.interceptions', 'Interceptions', 'offense', 'integer', 'Interceptions thrown', 'SportsDataIO'),
        ('offense.passing.qb_rating', 'QB Rating', 'offense', 'float', 'Passer rating', 'SportsDataIO')
    ]
    
    for stat_key, stat_name, category, data_type, description, source in new_stats:
        cursor.execute("""
            INSERT INTO stats_metadata (stat_key, stat_name, category, data_type, description, source)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (stat_key) DO UPDATE 
            SET stat_name = EXCLUDED.stat_name;
        """, (stat_key, stat_name, category, data_type, description, source))
    
    conn.commit()
    conn.close()
```

---

## 🔍 Querying JSONB Stats

### Get Specific Stat
```sql
-- Get PPG for all teams
SELECT name, stats->'offense'->>'points_per_game' as ppg
FROM teams
ORDER BY (stats->'offense'->>'points_per_game')::float DESC;
```

### Filter by Stat Value
```sql
-- Get teams with PPG > 25
SELECT name, stats->'offense'->>'points_per_game' as ppg
FROM teams
WHERE (stats->'offense'->>'points_per_game')::float > 25;
```

### Calculate from Multiple Stats
```sql
-- Get turnover differential
SELECT 
    name,
    (stats->'defense'->>'takeaways')::int as takeaways,
    (stats->'offense'->>'turnovers')::int as turnovers,
    (stats->'defense'->>'takeaways')::int - (stats->'offense'->>'turnovers')::int as differential
FROM teams
ORDER BY differential DESC;
```

### Check if Stat Exists
```sql
-- Find teams with passing stats
SELECT name
FROM teams
WHERE stats->'offense'->'passing' IS NOT NULL;
```

### Get All Stats for a Team
```sql
-- Get all stats for Kansas City Chiefs
SELECT jsonb_pretty(stats)
FROM teams
WHERE abbreviation = 'KC';
```

---

## 🚀 API Integration Examples

### Option A: SportsDataIO (Recommended)
- **Free Trial**: 1,000 API calls
- **Comprehensive Stats**: 100+ team stats, player stats, game stats
- **Documentation**: https://sportsdata.io/developers/api-documentation/nfl

```python
import requests

def fetch_sportsdata_stats(api_key):
    headers = {'Ocp-Apim-Subscription-Key': api_key}
    url = "https://api.sportsdata.io/v3/nfl/stats/json/TeamSeasonStats/2025REG"
    
    response = requests.get(url, headers=headers)
    teams_data = response.json()
    
    # Returns 32 teams with 100+ stats each!
    return teams_data
```

### Option B: RapidAPI NFL Stats
- **Free Tier**: 100 requests/day
- **Multiple Providers**: Tank01, API-NFL, ESPN API

```python
def fetch_rapidapi_stats(api_key):
    headers = {
        'X-RapidAPI-Key': api_key,
        'X-RapidAPI-Host': 'tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com'
    }
    url = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLTeamStats"
    
    response = requests.get(url, headers=headers)
    return response.json()
```

### Option C: Enhanced ESPN API
- **Free**: No API key needed
- **Limited Stats**: Basic team stats, scores, standings

```python
def fetch_espn_extended_stats():
    # Team stats endpoint
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}/statistics"
    response = requests.get(url)
    return response.json()
```

---

## 📈 Frontend Integration

### React Component (Dynamic Stats Display)
```javascript
function TeamStatsDisplay({ team }) {
  const stats = team.stats;
  
  return (
    <div className="team-stats">
      <h2>{team.name}</h2>
      
      {/* Dynamically render all available stats */}
      {Object.entries(stats).map(([category, categoryStats]) => (
        <div key={category} className="stat-category">
          <h3>{category.charAt(0).toUpperCase() + category.slice(1)}</h3>
          
          <div className="stat-grid">
            {Object.entries(categoryStats).map(([statKey, statValue]) => (
              <div key={statKey} className="stat-item">
                <label>{formatStatName(statKey)}</label>
                <value>{formatStatValue(statValue)}</value>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// Utility to format stat names
function formatStatName(key) {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase());
}
```

### API Endpoint (Return Full Stats)
```python
@app.route('/api/teams/<abbreviation>')
def get_team(abbreviation):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name, abbreviation, wins, losses, games_played, stats
        FROM teams
        WHERE abbreviation = %s
    """, (abbreviation,))
    
    team = cursor.fetchone()
    conn.close()
    
    if team:
        return jsonify({
            'name': team[0],
            'abbreviation': team[1],
            'wins': team[2],
            'losses': team[3],
            'games_played': team[4],
            'stats': team[5]  # PostgreSQL returns JSONB as dict automatically
        })
    else:
        return jsonify({'error': 'Team not found'}), 404
```

---

## ✅ Benefits of This Approach

### 1. **Zero Schema Changes**
- Add 10 stats or 1,000 stats → same database schema
- No `ALTER TABLE` migrations needed
- No downtime for schema changes

### 2. **Flexible Data Sources**
- Combine ESPN + TeamRankings + SportsDataIO
- Some teams can have different stats
- Easy to add new data sources

### 3. **Future-Proof**
- Prepare for player stats (100+ stats per player)
- Prepare for game stats (200+ stats per game)
- Prepare for betting odds (50+ betting markets)

### 4. **Query Flexibility**
- Filter by any stat using JSONB operators
- Create calculated stats on the fly
- Index specific stats for performance

### 5. **API-Friendly**
- Return full stats object to frontend
- Frontend decides what to display
- No API changes when adding stats

---

## 🎯 Next Steps

### Immediate (This Week)
1. ✅ **Done**: Migrate to JSONB schema
2. ✅ **Done**: Demo adding turnover stats
3. **TODO**: Choose API provider (SportsDataIO recommended)
4. **TODO**: Get API key for comprehensive stats

### Short-Term (This Month)
1. Update `extensible_data_fetcher.py` to use chosen API
2. Add 20-30 core stats (offense, defense, special teams)
3. Update React frontend to dynamically display stats
4. Test with live data during games

### Long-Term (Next Month)
1. Add player stats system (same JSONB approach)
2. Add game stats system (detailed play-by-play)
3. Add betting odds integration
4. Build prediction models using all stats

---

## 📚 Resources

- **PostgreSQL JSONB Docs**: https://www.postgresql.org/docs/current/datatype-json.html
- **SportsDataIO NFL API**: https://sportsdata.io/developers/api-documentation/nfl
- **RapidAPI NFL Stats**: https://rapidapi.com/collection/sports-apis
- **ESPN Hidden APIs**: https://gist.github.com/nntrn/ee26cb2a0716de0947a0a4e9a157bc1c

---

## 🔧 Migration Files Created

1. **migrate_to_scalable_schema.py**: Adds JSONB column and metadata table
2. **extensible_data_fetcher.py**: Template for multi-source data fetching
3. **demo_scalable_stats.py**: Demonstrates JSONB capabilities
4. **THIS FILE**: Complete implementation guide

---

## ❓ FAQ

**Q: Won't JSONB be slower than regular columns?**
A: PostgreSQL JSONB is highly optimized and supports indexing. For analytics (not transactional), performance is excellent.

**Q: How do I index JSONB stats for faster queries?**
A: Create GIN index: `CREATE INDEX idx_stats ON teams USING GIN (stats);`
   Or index specific path: `CREATE INDEX idx_ppg ON teams ((stats->'offense'->>'points_per_game'));`

**Q: Can I still use SQL WHERE clauses?**
A: Yes! `WHERE (stats->'offense'->>'points_per_game')::float > 25`

**Q: What if API returns different team names?**
A: Use `TEAM_NAME_MAPPINGS` dict to normalize names before merging.

**Q: How do I handle missing stats?**
A: JSONB allows NULL values or missing keys. Query with `COALESCE` or check `IS NOT NULL`.

---

**🎉 You're now ready to scale to 100+ stats without breaking a sweat!**
