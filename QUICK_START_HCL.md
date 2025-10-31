# QUICK START GUIDE - HCL Schema Testbed Testing

**H.C. Lombardo App - Phase 2A Database Expansion**  
**One-Page Reference - Keep This Open While Testing**

---

## 🚀 Quick Start (3 Steps)

### Step 1: Load Test Data (5 minutes)
```powershell
cd "c:\IS330\H.C Lombardo App"
.\LOAD_TESTBED_DATA.bat
```
- Choose option **[1]** (2024 season only)
- Wait 3-5 minutes
- Should see: "SUCCESS! 2024 season loaded into testbed"

### Step 2: Verify in pgAdmin (2 minutes)
Open pgAdmin → Query Tool → Run:
```sql
-- Quick verification
SELECT 
  (SELECT COUNT(*) FROM hcl_test.games) as games,
  (SELECT COUNT(*) FROM hcl_test.team_game_stats) as stats;

-- Expected: games: 270, stats: 540
```

### Step 3: Test Matchup View (1 minute)
```sql
SELECT game_id, home_team, away_team, home_score, away_score, winner
FROM hcl_test.v_game_matchup_display
WHERE season = 2024 AND week = 1
ORDER BY game_date;

-- Expected: 16 rows (Week 1 games)
```

✅ **If all 3 steps pass → Proceed to full load** (Option 2 in batch script)

---

## 📁 Files Created

| File | Purpose | Size |
|------|---------|------|
| `testbed_hcl_schema.sql` | Schema definition | 358 lines |
| `ingest_historical_games.py` | Data loader | 671 lines |
| `TEST_HCL_SCHEMA.md` | Testing guide | 462 lines |
| `LOAD_TESTBED_DATA.bat` | Interactive script | 196 lines |
| `PHASE2A_IMPLEMENTATION_COMPLETE.md` | Summary doc | 715 lines |

---

## 🔍 Essential Verification Queries

### Check Table Counts
```sql
SELECT 'games' AS table_name, COUNT(*) FROM hcl_test.games
UNION ALL
SELECT 'team_game_stats', COUNT(*) FROM hcl_test.team_game_stats;
```

### Check Season Breakdown
```sql
SELECT season, COUNT(*) as game_count 
FROM hcl_test.games 
GROUP BY season 
ORDER BY season DESC;
```

### Check Data Quality
```sql
-- Should return 0 rows (no NULLs in critical stats)
SELECT COUNT(*) as problem_records
FROM hcl_test.team_game_stats
WHERE points IS NULL OR total_yards IS NULL;
```

### Spot Check Known Game
```sql
-- 2024 Week 1: KC @ BAL (should show actual scores)
SELECT home_team, away_team, home_score, away_score, winner
FROM hcl_test.v_game_matchup_display
WHERE game_id LIKE '2024_01_%_KC_%_BAL%' OR game_id LIKE '2024_01_%_BAL_%_KC%';
```

---

## ⚙️ Command Line Quick Reference

### Load Test Data (2024 Only)
```powershell
python ingest_historical_games.py --testbed --seasons 2024
```

### Load Full Data (2022-2025)
```powershell
python ingest_historical_games.py --testbed --seasons 2022 2023 2024 2025
```

### Load Production (AFTER Testbed Validation)
```powershell
python ingest_historical_games.py --production --seasons 2022 2023 2024 2025
```

---

## ✅ Success Criteria Checklist

**Schema Created:**
- [ ] 5 tables exist in `hcl_test` schema
- [ ] 1 materialized view (`v_game_matchup_display`)
- [ ] All indexes created

**Data Loaded:**
- [ ] 2024 season: ~270 games
- [ ] Full history: ~1100 games (after full load)
- [ ] Team-game stats: 2× games count

**Data Quality:**
- [ ] No NULL critical stats (points, yards)
- [ ] No negative values
- [ ] Averages reasonable (22-24 PPG, 320-350 YPG)
- [ ] Win/loss results match scores

**View Performance:**
- [ ] Queries execute < 50ms
- [ ] View refresh succeeds

---

## 🚨 Troubleshooting (Most Common Issues)

### "Module 'nfl_data_py' not found"
```powershell
pip install nfl_data_py
```

### "Permission denied" or "Schema exists"
```sql
-- Drop and recreate
DROP SCHEMA IF EXISTS hcl_test CASCADE;
-- Then re-run testbed_hcl_schema.sql
```

### "Connection refused"
Check `.env` file:
```powershell
cat .env | Select-String "DB_"
```

### Data loader hangs
- **Normal!** First run downloads ~500MB per season
- Be patient (5-10 minutes)
- Data is cached for subsequent runs

---

## 📊 Expected Data Volumes

| Season | Games | Team-Game Records | Status |
|--------|-------|-------------------|--------|
| 2024 | ~270 | ~540 | Complete season |
| 2023 | ~270 | ~540 | Complete season |
| 2022 | ~270 | ~540 | Complete season |
| 2025 | ~140 | ~280 | Current (Week 8) |
| **Total** | **~950** | **~1900** | - |

---

## 🔄 After Successful Testing → Production Migration

### 1. Backup Production Database
```powershell
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
pg_dump -U postgres -d nfl_analytics > "backups/nfl_analytics_before_hcl_$timestamp.sql"
```

### 2. Create Production Schema
```sql
-- Replace hcl_test with hcl in testbed_hcl_schema.sql
-- Or just run production loader (creates schema automatically)
```

### 3. Load Production Data
```powershell
python ingest_historical_games.py --production --seasons 2022 2023 2024 2025
```

### 4. Update API Endpoints
Change Flask routes to use `hcl.v_game_matchup_display` instead of testbed

---

## 📝 Log Files

- `historical_data_load.log` - Detailed execution log (check for errors)

---

## 🎯 Why Are We Doing This?

**Goal:** Add ML predictive analytics to H.C. Lombardo App
- Game outcome predictions
- Score predictions  
- Team performance analysis
- Betting line recommendations

**Problem:** Current database only has ~140 games (insufficient for ML)

**Solution:** Load 2022-2025 historical data (~1100 games)
- Enough data for training/validation
- 47+ performance metrics per team per game
- Foundation for feature engineering

**Next Steps After This:**
- Sprint 9: Feature engineering views
- Sprint 10+: Build ML models

---

## 📞 Support

- **Detailed Testing:** See `TEST_HCL_SCHEMA.md`
- **Full Documentation:** See `PHASE2A_IMPLEMENTATION_COMPLETE.md`
- **Original Plan:** See `PHASE2_IMPLEMENTATION_PLAN.md`

---

**Last Updated:** October 28, 2025  
**Status:** Ready for Testing  
**Estimated Testing Time:** 30-45 minutes total
