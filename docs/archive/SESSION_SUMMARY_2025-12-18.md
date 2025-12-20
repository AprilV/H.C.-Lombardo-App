# Session Summary - December 18, 2025

## What We Accomplished Today

### 1. Fixed Broken ML Predictions (100% Confidence Issue)

**Problem:** ML models were showing 100% confidence on all predictions, making them useless.

**Root Cause:** Models were missing Vegas betting lines (spread_line), which are 17-29% of feature importance. When missing, the default value of 0.0 caused massive home field advantage bias.

**Solution:**
- Created `scrape_vegas_lines.py` - Scrapes Vegas lines from ESPN API
- Vegas lines now available:
  - Weeks 1-14: 100% coverage (from nflverse)
  - Week 16: 88% coverage (14/16 games scraped)
  - Week 15, 17-18: Need to run scraper weekly

### 2. Automated Everything

**Created Auto-Update Pipeline:**

1. **`scrape_vegas_lines.py`** - Fetches current week's betting lines from ESPN
2. **`background_updater.py`** - Updated to run complete pipeline:
   - Scrape Vegas lines
   - Fetch game data from nflverse
   - Generate ML predictions
   - Update results tracking
3. **`scripts/data_loading/auto_update_service.py`** - Enhanced with 4-step pipeline
4. **`START_AUTO_UPDATE.bat`** - Windows service (runs every 15 minutes)
5. **`setup_auto_updates.sh`** - EC2 cron setup script
6. **`restart_ec2_server.sh`** - EC2 server restart utility

**How to Run:**
```bash
# Windows (local)
START_AUTO_UPDATE.bat

# EC2 (production) - Manual weekly run
source venv/bin/activate
python scrape_vegas_lines.py  # Get Vegas lines
python ml/predict_week.py      # Generate predictions
```

### 3. Fixed API Server Issues

**Problems:**
- Missing imports (logging_config, dashboard_api)
- Numpy float32 not JSON serializable
- Server not starting on EC2

**Fixes:**
- Made optional imports in `api_server.py`
- Fixed float32 → float conversion in `ml/predict_week.py`
- Created restart script for EC2 deployment

**Server Status:**
- Local: http://localhost:5000
- EC2: http://34.198.25.249:5000
- Both serving predictions with 46 comprehensive features

### 4. Fixed AWS Amplify Routing

**Problem:** Direct navigation to `/ml-predictions/` returned 404

**Solution:**
- Created `amplify.yml` - Build configuration
- Created `frontend/public/_redirects` - SPA routing rule
- All routes now redirect to index.html (React Router handles routing)

## Current System Architecture

### Machine Learning Pipeline

**Models:** XGBoost (replaced neural networks)
- **Winner Model:** 60.7% accuracy, 360KB
- **Spread Model:** 11.6 MAE, 555KB
- **Features:** 46 comprehensive NFL stats (EPA, success rate, yards, turnovers, etc.)
- **Training Data:** 2020-2025 seasons (modern NFL only)

**Feature Importance:**
- Vegas spread_line: 17-29% (CRITICAL - must be present)
- Team EPA metrics: 5-7%
- Success rates: 5-7%
- Recent performance: 3-5%

### Data Sources

1. **nflverse** (primary) - Historical game data, stats, EPA metrics
2. **ESPN API** - Vegas betting lines for upcoming games
3. **Database:** PostgreSQL `nfl_analytics`
   - Schema: `hcl` (production, 2020-2025 data)
   - Schema: `hcl_test` (testing, 2025 only, missing EPA)

### Automation Stack

**Local (Windows):**
- `START_AUTO_UPDATE.bat` → runs every 15 minutes
- Pipeline: Vegas → Games → Predictions → Results

**EC2 (Production):**
- Manual weekly: `python scrape_vegas_lines.py`
- Server: `api_server.py` (auto-restart script available)
- GitHub Actions: AWS SSM (replaced SSH after 15 days of timeouts)

### Deployment

**AWS Systems:**
- **EC2:** i-076502f470ab36343, Ubuntu 22.04, 34.198.25.249
- **SSM:** Used for GitHub Actions (100% success rate)
- **Amplify:** Frontend hosting (master.d2tamnlcbzo0d5.amplifyapp.com)

**GitHub:**
- Repo: AprilV/H.C.-Lombardo-App
- Latest commit: fe3a2150 (Amplify routing fix)

## Key Files Modified Today

```
scrape_vegas_lines.py          ← NEW: Vegas line scraper
background_updater.py          ← UPDATED: Complete pipeline
api_server.py                  ← FIXED: Optional imports
ml/predict_week.py             ← FIXED: JSON serialization
setup_auto_updates.sh          ← NEW: EC2 cron setup
restart_ec2_server.sh          ← NEW: Server restart
START_AUTO_UPDATE.bat          ← UPDATED: Full pipeline
amplify.yml                    ← NEW: Amplify config
frontend/public/_redirects     ← NEW: SPA routing
scripts/data_loading/auto_update_service.py  ← UPDATED: 4-step pipeline
```

## Critical Discoveries

### Why Predictions Were Broken

1. **Missing Vegas Lines:** Without spread_line, model defaults to 0.0 (even game)
2. **Home Field Bias:** With 0.0 spread, every home team gets 80-99% win probability
3. **Real-World Test:** Week 11 showed 33% accuracy (random with home bias)

### Research Findings

**Vegas Methodology:**
- Elo rating systems (FiveThirtyEight uses K=20, HFA=65)
- Power ratings updated after each game
- Adjustments: injuries, weather, rest, coaching, public/sharp money

**Model Architecture Insights:**
- Simpler is better: 10-15 features > 46 features
- 1,506 games insufficient for 46 features (overfitting)
- Vegas spread itself is THE most important feature (crowd wisdom)

### Data Leakage Issues (Fixed)

**Original Problem:** 97-98% accuracy in training
**Cause:** Using cumulative stats that included future games
**Fix:** Rewrote queries to use only prior games for each prediction

## What's Working Now

✅ Vegas lines scraping from ESPN  
✅ ML predictions with 46 features  
✅ API server on EC2 (http://34.198.25.249:5000)  
✅ Automated update pipeline  
✅ AWS Amplify routing  
✅ GitHub Actions via AWS SSM  

## What Needs Weekly Maintenance

1. **Scrape Vegas Lines:** Run before each week starts
   ```bash
   python scrape_vegas_lines.py
   ```

2. **Regenerate Predictions:** After scraping lines
   ```bash
   python ml/predict_week.py
   ```

3. **Optional:** Check prediction accuracy
   ```bash
   python update_prediction_results.py
   ```

## Known Issues & Future Improvements

### Current Limitations

- **Week 15, 17-18:** No Vegas lines yet (need to scrape weekly)
- **Model Accuracy:** 60% in training, but needs real-world validation
- **Overfitting:** 46 features may be too many for 1,506 training games

### Recommended Next Steps

1. **Implement Elo System:** FiveThirtyEye's proven approach (simpler, more robust)
2. **Reduce Features:** 10-15 key features instead of 46
3. **Weekly Validation:** Track real-world accuracy vs Vegas
4. **Automate More:** Cron job on EC2 for weekly scraping
5. **Add Monitoring:** Alert if predictions show 80%+ confidence consistently

## Environment Setup

### Local Development

**Python Virtual Environment:**
```bash
.venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

**Required Packages:**
- flask, flask-cors
- psycopg2
- pandas, numpy
- xgboost
- requests
- nfl_data_py

**Database Config:**
- Host: localhost (local) / RDS endpoint (production)
- Database: nfl_analytics
- User: postgres
- Schema: hcl (production data)

### EC2 Setup

**Location:** /home/ubuntu/H.C.-Lombardo-App

**Python:** Python 3 venv with xgboost 2.1.2

**Git Ownership Fix:**
```bash
git config --global --add safe.directory /home/ubuntu/H.C.-Lombardo-App
```

**Start Server:**
```bash
cd /home/ubuntu/H.C.-Lombardo-App
source venv/bin/activate
nohup python api_server.py > logs/api.log 2>&1 &
```

**Or use restart script:**
```bash
./restart_ec2_server.sh
```

## Testing Endpoints

**Health Check:**
```bash
curl http://34.198.25.249:5000/health
```

**Predictions (Current Week):**
```bash
curl http://34.198.25.249:5000/api/ml/predict-upcoming
```

**Predictions (Specific Week):**
```bash
curl http://34.198.25.249:5000/api/ml/predict-week/2025/16
```

**Season Stats:**
```bash
curl http://34.198.25.249:5000/api/ml/season-ai-vs-vegas/2025
```

## Database Queries

**Check Vegas Line Coverage:**
```sql
SELECT week, 
       COUNT(*) as games, 
       SUM(CASE WHEN spread_line IS NOT NULL THEN 1 ELSE 0 END) as has_spread
FROM hcl.games 
WHERE season = 2025 
GROUP BY week 
ORDER BY week;
```

**View Recent Predictions:**
```sql
SELECT week, home_team, away_team, 
       predicted_winner, win_confidence, 
       vegas_spread, ai_spread
FROM hcl.ml_predictions 
WHERE season = 2025 
ORDER BY week DESC, game_date DESC 
LIMIT 20;
```

**Check Prediction Accuracy:**
```sql
SELECT 
    COUNT(*) as total_predictions,
    SUM(CASE WHEN predicted_winner = actual_winner THEN 1 ELSE 0 END) as correct,
    ROUND(100.0 * SUM(CASE WHEN predicted_winner = actual_winner THEN 1 ELSE 0 END) / COUNT(*), 1) as accuracy
FROM hcl.ml_predictions 
WHERE season = 2025 
  AND actual_winner IS NOT NULL;
```

## Contact & Resources

**AWS Resources:**
- EC2 Instance ID: i-076502f470ab36343
- Region: us-east-1
- Amplify: master.d2tamnlcbzo0d5.amplifyapp.com

**GitHub:**
- Repository: https://github.com/AprilV/H.C.-Lombardo-App
- Branch: master (production)

**Documentation:**
- `AUTOMATED_UPDATES.md` - Update process details
- `AWS_SSM_MIGRATION_PLAN.md` - GitHub Actions migration
- `PREDICTION_TRACKING_SYSTEM.md` - ML prediction tracking
- `NFL_SPREAD_BETTING_GUIDE.md` - Vegas methodology research

## Session Timeline

1. User returned after chat reboot, discovered broken predictions
2. Diagnosed: Missing Vegas lines causing 100% confidence bias
3. Researched: NFL data sources, Vegas methodology, Elo systems
4. Built: Vegas line scraper pulling from ESPN API
5. Tested: Week 16 now has 14/16 games with betting lines
6. Automated: Complete pipeline (Vegas → Games → Predictions → Results)
7. Fixed: API server imports and JSON serialization
8. Deployed: EC2 server restarted with updated code
9. Fixed: AWS Amplify routing for SPA
10. Documented: This file for continuity

---

**Status as of December 18, 2025:**
- ✅ All systems operational
- ✅ EC2 server running
- ✅ Predictions generating with Vegas lines
- ✅ AWS Amplify building with routing fix
- ⚠️ Need weekly Vegas line scraping for upcoming weeks
