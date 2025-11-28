# Live Score System Setup

## Overview
This system automatically saves live NFL scores to the database and locks Vegas spreads before kickoff.

## Components

### 1. Database Schema Update
Run this SQL to add the closing_spread column:
```bash
psql -d nfl_analytics -U nfl_user -f add_closing_spread_column.sql
```

### 2. Live Score Saver (`save_live_scores.py`)
Fetches scores from ESPN API and saves to database every 5-10 minutes.

**Features:**
- ✅ Saves live scores to `hcl.games` table
- 🔒 Locks Vegas spread 1 hour before kickoff into `closing_spread` column
- 🔄 Updates as games progress

**Run Once:**
```bash
python save_live_scores.py
```

**Run Continuous (every 5 minutes):**
```bash
python save_live_scores.py --continuous 5
```

**Run on Game Days:**
On Thursdays/Sundays/Mondays during NFL season, run this in the background:
```bash
python save_live_scores.py --continuous 5 &
```

### 3. What Gets Saved

**Live Scores:**
- `home_score` - Updated every 5 minutes during games
- `away_score` - Updated every 5 minutes during games

**Spread Locking:**
- `closing_spread` - Locked 1 hour before kickoff
- Uses the last available `spread_line` value from ESPN
- Once locked, never changes (this is the "closing line" for betting analysis)

### 4. How ML Predictions Use It

**Before:**
- Used `spread_line` which could change
- Vegas spread was inconsistent

**After:**
- Uses `COALESCE(closing_spread, spread_line)` 
- Falls back to current spread_line if closing not locked yet
- Ensures all historical analysis uses the actual closing lines

### 5. AI vs Vegas Tracking

New endpoint: `/api/ml/season-ai-vs-vegas/<season>`

**Returns:**
```json
{
  "ai_wins": 45,
  "vegas_wins": 38,
  "ties": 17,
  "total_games": 100,
  "ai_percentage": 54.2,
  "vegas_percentage": 45.8
}
```

Shows season-to-date performance comparing AI spread predictions vs Vegas spreads.

## Deployment

### On EC2 (Production)

1. **Add column to database:**
```bash
ssh ubuntu@api.aprilsykes.dev
cd /path/to/app
psql -d nfl_analytics -U nfl_user -f add_closing_spread_column.sql
```

2. **Set up cron job for game days:**
```bash
crontab -e
```

Add this line (runs every 5 minutes on Thu/Sun/Mon):
```
*/5 * * * 4,0,1 cd /path/to/app && python3 save_live_scores.py >> /var/log/live_scores.log 2>&1
```

Or use systemd service for continuous running.

### Testing Locally

```bash
# Test once
python save_live_scores.py

# Watch continuous (Ctrl+C to stop)
python save_live_scores.py --continuous 5
```

## How Spread Locking Works

1. **Before Kickoff (>1 hour):**
   - `spread_line` updates from ESPN as odds change
   - `closing_spread` is NULL

2. **1 Hour Before Kickoff:**
   - Script detects kickoff approaching
   - Copies current `spread_line` → `closing_spread`
   - Logs: "🔒 Locked spread for CHI@PHI: -3.5"

3. **During/After Game:**
   - `closing_spread` never changes (locked)
   - `home_score`/`away_score` update live
   - ML predictions calculate against locked `closing_spread`

## Monitoring

Check if it's working:
```sql
-- See locked spreads
SELECT game_id, home_team, away_team, spread_line, closing_spread 
FROM hcl.games 
WHERE season = 2025 AND week = 13;

-- See live scores
SELECT game_id, home_team, home_score, away_team, away_score, updated_at
FROM hcl.games 
WHERE season = 2025 AND week = 13 AND home_score IS NOT NULL
ORDER BY updated_at DESC;
```

## Troubleshooting

**Spreads not locking:**
- Check kickoff_time_utc is set correctly in database
- Script only locks within 1 hour of kickoff

**Scores not updating:**
- Verify ESPN API is accessible: `curl "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"`
- Check team abbreviations match (WSH vs WAS issue)

**Season stats not showing:**
- Ensure ml_predictions table has data
- Check `/api/ml/season-ai-vs-vegas/2025` endpoint returns data
