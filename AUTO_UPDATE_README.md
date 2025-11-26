# Automated NFL Data Updates

## Overview
The H.C. Lombardo App now automatically updates NFL game data every 15 minutes during the season. This keeps predictions, scores, and statistics current without manual intervention.

## How It Works

### Auto-Update Service (`auto_update_service.py`)
- **Runs continuously** in background window
- **Updates every 15 minutes** by default (configurable)
- **Smart scheduling**: More active during NFL season and game days
- **Two-step process**:
  1. Fetches latest game data from nflverse
  2. Updates ML prediction results with actual scores

### What Gets Updated
1. **Game Scores**: Latest scores for all 2025 games
2. **Team Stats**: EPA, passing yards, rushing yards, etc.
3. **Prediction Results**: AI accuracy, spread coverage, actual winners
4. **Live Scores**: Current scores for in-progress games

## Usage

### Start Automatically with App
The auto-update service starts automatically when you run `startup.py`:
```bash
python startup.py
```

### Start Manually
```bash
# Run once (single update)
python auto_update_service.py

# Run continuously (every 15 minutes)
python auto_update_service.py --continuous

# Run continuously (custom interval)
python auto_update_service.py --continuous 5   # Every 5 minutes
```

### Using Batch File
Double-click `START_AUTO_UPDATE.bat` to start the service in a new window.

## Monitoring

### Service Window
The auto-update service runs in its own PowerShell window showing:
- Current update cycle number
- Data fetch status
- Prediction update status
- Next scheduled update time

### Logs
Activity is logged to both:
- Console output (in service window)
- `historical_data_load.log` (detailed nflverse operations)

## Stopping the Service
- **Close the auto-update window**, or
- **Press Ctrl+C** in the service window, or
- **Run `shutdown.py`** to stop all services

## Configuration

### Update Interval
Default: 15 minutes

Change by editing the interval parameter:
```python
python auto_update_service.py --continuous 30  # Every 30 minutes
```

### Game Day Detection
Service automatically detects:
- **NFL Season**: September through February
- **Game Days**: Thursday, Sunday, Monday (+ Tuesday for MNF catchup)
- **Off-season**: Reduced update frequency

## Integration with ML Predictions

The auto-update ensures your ML Predictions page always shows:
- ✅ Latest final scores
- ✅ Current AI prediction accuracy
- ✅ Real-time Vegas spread coverage
- ✅ Updated scorecard statistics

## Troubleshooting

### Service Not Updating
1. Check if service window is still open
2. Look for errors in service window
3. Verify internet connection (nflverse requires internet)
4. Check database connection

### Manual Update
If auto-update isn't working, manually update:
```bash
# Update game data
python ingest_historical_games.py --production --seasons 2025

# Update predictions
python update_prediction_results.py
```

### Performance
- Each update cycle takes ~10-20 seconds
- Minimal CPU/memory usage between updates
- Network usage: ~1-5 MB per update

## Architecture

```
Auto-Update Service
    ↓
1. Fetch nflverse data (nfl_data_py)
    ↓
2. Insert into hcl.games table
    ↓
3. Calculate team stats
    ↓
4. Update hcl.ml_predictions
    ↓
5. Frontend fetches via API
    ↓
6. User sees latest data
```

## Future Enhancements
- [ ] Email notifications on update failures
- [ ] Web dashboard for monitoring updates
- [ ] Webhook support for real-time updates
- [ ] Integration with ESPN live API
- [ ] Automatic retry on network failures

## Notes
- Service is designed for development/local use
- For production deployment, consider using:
  - Windows Task Scheduler (scheduled task)
  - Docker container with cron
  - Cloud-based scheduler (AWS EventBridge, Azure Functions)
- Updates are idempotent (safe to run multiple times)
- Database has unique constraints preventing duplicates
