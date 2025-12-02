# Automated NFL Data Updates

## Overview
The H.C. Lombardo App has **automated weekly updates** for the 2025 NFL season using GitHub Actions.

## Architecture

### Database Location
- **Production**: PostgreSQL 14 on AWS EC2 (localhost)
- **Host**: localhost (internal to EC2)
- **External IP**: 34.198.25.249 (SSH only)
- **Database**: nfl_analytics
- **Schema**: hcl
- **User**: nfl_user / nfl2024

### Update Mechanism
GitHub Actions workflow:
1. SSH into EC2 instance (ubuntu@34.198.25.249)
2. Navigate to `~/H.C.-Lombardo-App`
3. Activate Python virtual environment
4. Run `python ingest_historical_games.py --production --seasons 2025`
5. Script connects to localhost PostgreSQL
6. Downloads latest nflverse data
7. Updates hcl.games and hcl.team_game_stats tables

## Update Schedule
- **Automatic**: Every Monday at 2 AM UTC (after weekend games)
- **Manual**: Can be triggered anytime from GitHub Actions tab

## What Gets Updated
1. **New 2025 games** from nflverse (schedules, scores, betting lines)
2. **EPA statistics** calculated from play-by-play data:
   - epa_per_play (offensive efficiency)
   - pass_epa / rush_epa (split by play type)
   - success_rate (down/distance context)
   - explosive_play_pct
   - And 10+ other advanced metrics
3. **Team performance stats**: Points, yards, turnovers, third down conversions, etc.

## Setup Instructions

### 1. Add SSH Key to GitHub Secrets

Go to your repository: **Settings → Secrets and variables → Actions → New repository secret**

Add secret:

| Secret Name | Value |
|------------|-------|
| `EC2_SSH_KEY` | Contents of `hc-lombardo-key.pem` private key file |

### 2. Enable GitHub Actions

1. Go to **Actions** tab in your GitHub repository
2. If disabled, click **"I understand my workflows, go ahead and enable them"**
3. You should see the workflow: **"NFL 2025 Data Update"**

### 3. Test Manual Run

1. Go to **Actions** → **NFL 2025 Data Update**
2. Click **"Run workflow"** dropdown
3. Click green **"Run workflow"** button
4. Watch it run (~5-10 minutes)

## Manual Updates

### Option A: Use GitHub Actions UI
1. Go to Actions tab
2. Select "NFL 2025 Data Update"
3. Click "Run workflow"

### Option B: SSH to EC2 and Run Manually
```bash
# SSH to EC2
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249

# Navigate to app directory
cd ~/H.C.-Lombardo-App

# Activate virtual environment
source venv/bin/activate

# Run update script
python ingest_historical_games.py --production --seasons 2025
```

### Option C: Run Locally (for testing)
```bash
# Make sure .env file has correct local credentials:
# DB_HOST=localhost
# DB_NAME=nfl_analytics
# DB_USER=postgres
# DB_PASSWORD=aprilv120

# Run the update
python ingest_historical_games.py --production --seasons 2025
```

## Monitoring Updates

### Check Last Update Time
Visit your app and check:
- **ML Predictions page**: Should show latest week predictions
- **Game Statistics**: Dropdowns should have all 32 teams
- **Analytics**: Should show recent games

### View Update Logs
1. Go to **Actions** tab
2. Click on latest **"NFL 2025 Data Update"** run
3. Expand steps to see detailed logs

### Verify Database (from EC2)
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249
psql -U nfl_user -h localhost -d nfl_analytics << 'EOF'
SELECT COUNT(*), MAX(week), MAX(game_date) 
FROM hcl.games 
WHERE season = 2025 AND home_score IS NOT NULL;
EOF
```

## Troubleshooting

### Update Failed
1. Check GitHub Actions logs for errors
2. Verify EC2_SSH_KEY secret is set correctly
3. Test SSH connection: `ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249`
4. Try manual run from EC2

### Website Not Showing New Data
1. Hard refresh browser (Ctrl+Shift+R)
2. Check API health: https://api.aprilsykes.dev/health
3. Verify database on EC2 has latest data
4. Restart Gunicorn: `pkill -9 gunicorn && cd ~/H.C.-Lombardo-App && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 api_server:app > gunicorn.log 2>&1 &`

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

### AWS EC2
- **Instance**: t3.micro (free tier eligible)
- **Cost**: ~$8/month if not on free tier
- **Storage**: Standard EBS volume

## Future Enhancements

1. **Notifications**: Add Slack/Discord webhook when updates complete
2. **Error alerts**: Email if update fails
3. **Multi-season**: Extend to update current season dynamically (2026, 2027, etc.)
4. **Backup automation**: Weekly database exports to S3
5. **Performance tracking**: Log how long updates take
