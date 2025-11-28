# Automated NFL Data Updates

## Overview
The H.C. Lombardo App now has **automated weekly updates** for the 2025 NFL season using GitHub Actions.

## How It Works

### Data Structure
- **Historical Data (1999-2024)**: Static, loaded once, never changes
- **Current Season (2025)**: Updates weekly with latest games and EPA calculations

### Update Schedule
- **Automatic**: Every Monday at 2 AM UTC (after weekend games)
- **Manual**: Can be triggered anytime from GitHub Actions tab

### What Gets Updated
1. **New 2025 games** from nflverse (schedules, scores, betting lines)
2. **EPA statistics** calculated from play-by-play data:
   - epa_per_play (offensive efficiency)
   - pass_epa / rush_epa (split by play type)
   - success_rate (down/distance context)
   - explosive_play_pct
   - And 10+ other advanced metrics

3. **Team performance stats**:
   - Points, yards, turnovers
   - Third down conversions
   - Red zone efficiency
   - Time of possession

## Setup Instructions

### 1. Add Secrets to GitHub Repository

Go to your repository: **Settings → Secrets and variables → Actions → New repository secret**

Add these 4 secrets:

| Secret Name | Value |
|------------|-------|
| `RENDER_DB_HOST` | `dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com` |
| `RENDER_DB_NAME` | `nfl_analytics` |
| `RENDER_DB_USER` | `nfl_user` |
| `RENDER_DB_PASSWORD` | `rzkKyzQq9pTas14pXDJU3fm8cCZObAh5` |

### 2. Enable GitHub Actions

1. Go to **Actions** tab in your GitHub repository
2. If disabled, click **"I understand my workflows, go ahead and enable them"**
3. You should see the workflow: **"Update NFL 2025 Season Data"**

### 3. Test Manual Run

1. Go to **Actions** → **Update NFL 2025 Season Data**
2. Click **"Run workflow"** dropdown
3. Click green **"Run workflow"** button
4. Watch it run (~5-10 minutes)

## Manual Updates (If Needed)

If you need to update data immediately (not wait for Monday):

### Option A: Use GitHub Actions UI
1. Go to Actions tab
2. Select "Update NFL 2025 Season Data"
3. Click "Run workflow"

### Option B: Run Locally
```bash
# Set environment variables to point to Render
export DB_HOST=dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com
export DB_NAME=nfl_analytics
export DB_USER=nfl_user
export DB_PASSWORD=rzkKyzQq9pTas14pXDJU3fm8cCZObAh5
export DB_PORT=5432

# Run the update
python ingest_historical_games.py --production --seasons 2025
```

Or use the wrapper script:
```bash
python load_2025_to_render_with_epa.py
```

## Monitoring Updates

### Check Last Update Time
Visit your app and check:
- **ML Predictions page**: Should show latest week predictions
- **Game Statistics**: Dropdowns should have all 32 teams
- **Analytics**: Should show recent games

### View Update Logs
1. Go to **Actions** tab
2. Click on latest **"Update NFL 2025 Season Data"** run
3. Expand **"Update 2025 season data"** step
4. See detailed logs of what was updated

### Verify Database
Run this to check what's in Render database:
```bash
python -c "
import psycopg2
conn = psycopg2.connect('postgresql://nfl_user:rzkKyzQq9pTas14pXDJU3fm8cCZObAh5@dpg-d4j30ah5pdvs739551m0-a.oregon-postgres.render.com/nfl_analytics')
cur = conn.cursor()
cur.execute('SELECT COUNT(*), MAX(week) FROM hcl.games WHERE season = 2025 AND home_score IS NOT NULL')
count, max_week = cur.fetchone()
print(f'2025 Season: {count} completed games through Week {max_week}')
conn.close()
"
```

## Troubleshooting

### Update Failed
1. Check GitHub Actions logs for errors
2. Verify secrets are set correctly
3. Make sure Render database is accessible
4. Try manual run: `python load_2025_to_render_with_epa.py`

### Website Not Showing New Data
1. Hard refresh browser (Ctrl+Shift+R)
2. Check Render logs: https://dashboard.render.com → h-c-lombardo-app → Logs
3. Verify API working: https://h-c-lombardo-app.onrender.com/api/teams
4. Restart Render service if needed

### Missing EPA Stats
If team_game_stats has games but no EPA data:
- The update script calculates EPA from play-by-play data
- If nflverse doesn't have play-by-play yet, EPA will be NULL
- Usually available 24-48 hours after game completion

## Cost & Limits

### GitHub Actions
- **Free tier**: 2,000 minutes/month
- **This workflow uses**: ~10 minutes/week = 40 min/month
- **Plenty of headroom!**

### Render Database
- **Free tier**: Expires after 90 days (Feb 24, 2026)
- **Workaround**: Export data before expiration, create new free database
- **Or upgrade**: $7/month for permanent database

## Future Enhancements

1. **Notifications**: Add Slack/Discord webhook when updates complete
2. **Error alerts**: Email if update fails
3. **Multi-season**: Extend to update current season dynamically (2026, 2027, etc.)
4. **Backup automation**: Weekly database exports to GitHub
5. **Performance tracking**: Log how long updates take

## Questions?

Check the logs or run manual update to debug issues.
