# 🏈 Complete nflverse Free Data Inventory

**Everything We Can Get (100% FREE)** - Generated: October 28, 2025

---

## 📦 **24 Total Datasets Available**

All data from [nflverse](https://github.com/nflverse) is **completely free**, crowd-sourced by the NFL analytics community.

---

## 🎯 **TIER 1: Already Downloaded, Just Need to Store**

### **From Schedules** (We already have this data!)
✅ **Betting Lines** (10 columns):
   - `spread_line` - Opening/consensus point spread (e.g., -3.0)
   - `total_line` - Opening/consensus over/under (e.g., 46.0)
   - `home_moneyline` - Home team moneyline odds (e.g., -148)
   - `away_moneyline` - Away team moneyline odds (e.g., +124)
   - `home_spread_odds` - Home spread odds (e.g., -110)
   - `away_spread_odds` - Away spread odds (e.g., -110)
   - `over_odds` - Over bet odds (e.g., -110)
   - `under_odds` - Under bet odds (e.g., -110)
   - `total` - Final total score (calculated)
   - `overtime` - Overtime flag (0/1)

✅ **Weather Conditions** (4 columns):
   - `roof` - Stadium type (outdoors/closed/retractable/dome)
   - `surface` - Playing surface (grass/turf type)
   - `temp` - Temperature in Fahrenheit (e.g., 67.0)
   - `wind` - Wind speed in MPH (e.g., 8.0)

✅ **Game Context** (9 columns):
   - `away_rest` - Days since away team's last game
   - `home_rest` - Days since home team's last game
   - `div_game` - Division game flag (0/1)
   - `referee` - Head referee name
   - `away_coach` - Away team head coach
   - `home_coach` - Home team head coach
   - `away_qb_name` - Starting away QB
   - `home_qb_name` - Starting home QB
   - `stadium` - Stadium name

**💰 Value**: These 23 columns are in the data we **already download**. Zero extra API calls needed!

---

### **From Play-by-Play** (We already download this for stats!)
✅ **Advanced Analytics** (EPA, WPA, Success):
   - `epa` - Expected Points Added per play
   - `wpa` - Win Probability Added per play
   - `success` - Success rate (EPA > 0)
   - `cpoe` - Completion Percentage Over Expected
   - `air_yards` - Air yards (passing)
   - `yards_after_catch` - YAC
   - `qb_hit` - QB pressure/hit flags
   - `sack` - Sack flags
   - Plus 100+ other play-level columns

**💰 Value**: Calculate team EPA/play, success rate, explosive play rate, etc. for game-level metrics.

---

## 🏈 **TIER 2: Separate Downloads (Still Free)**

### **Injuries** ✅ Tested: 6,215 records
```
Columns: season, game_type, team, week, gsis_id, position, full_name, 
         report_primary_injury, report_secondary_injury, report_status,
         practice_primary_injury, practice_secondary_injury, practice_status, 
         date_modified
```
- Weekly injury reports (Out/Questionable/Doubtful)
- Primary/secondary injuries
- Practice participation status
- Historical injury data back to ~2009

**Use Case**: Model impact of key injuries on team performance.

---

### **Depth Charts** ✅ Tested: 37,312 records
```
Columns: season, club_code, week, game_type, depth_team, last_name, first_name,
         formation, gsis_id, jersey_number, position, depth_position, full_name
```
- Weekly depth chart positions
- Formation-specific rankings (base, nickel, dime)
- Starter identification

**Use Case**: Identify backup QBs, rookie starts, position changes.

---

### **Next Gen Stats (NGS)** ✅ Tested: 614 passing records
**4 Categories**: Passing, Rushing, Receiving, Defense

**Passing NGS** (26 columns):
```
avg_time_to_throw, avg_completed_air_yards, avg_intended_air_yards, 
avg_air_yards_differential, aggressiveness, max_completed_air_distance,
avg_air_yards_to_sticks, completion_percentage_above_expectation, etc.
```

**Use Case**: Advanced QB metrics (time to throw, aggressive throws, CPOE).

---

### **QBR** (ESPN Quarterback Rating)
```
import_qbr([2024])
```
- Weekly ESPN QBR ratings
- More context-aware than traditional passer rating

---

### **Snap Counts**
```
import_snap_counts([2024])
```
- Player snap counts per game
- Snap percentage by position

**Use Case**: Playing time analysis, workload distribution.

---

### **Officials**
```
import_officials([2024])
```
- Full officiating crews per game
- Referee tendencies (penalty rates, challenges, etc.)

**Use Case**: Referee bias analysis (home/away penalty differentials).

---

### **Contract Data**
```
import_contracts()
```
- Player salaries
- Contract terms
- Cap hits

**Use Case**: Value analysis (performance vs. salary).

---

### **Draft Data**
```
import_draft_picks([2024])
import_draft_values()
```
- Draft pick history
- Draft pick trade value chart

---

### **Combine Data**
```
import_combine_data()
```
- NFL Combine results (40-yard dash, bench press, etc.)
- Pre-draft measurements

---

### **Player Rosters**
```
import_seasonal_rosters([2024])
import_weekly_rosters([2024])
```
- Player demographic info (height, weight, college, etc.)
- Weekly active/inactive status

---

### **Player Season/Weekly Stats**
```
import_seasonal_data([2024])
import_weekly_data([2024])
```
- Season-long player stats
- Weekly player stats

---

### **Pro Football Reference Stats**
```
import_seasonal_pfr('pass', [2024])
import_weekly_pfr('pass', [2024])
```
- Categories: pass, rush, rec, def
- Alternative to standard stats

---

### **Team Descriptions**
```
import_team_desc()
```
- Team names, abbreviations
- Team colors (hex codes)
- Logo URLs
- Conference/division

---

### **Win Totals**
```
import_win_totals([2024])
```
- Season win totals (final records)

---

### **SC Lines** (Unknown - needs investigation)
```
import_sc_lines([2024])
```
- May be alternative betting lines source

---

## 📊 **What We Currently Store vs. What's Available**

### **Currently Storing** (47 metrics):
- Basic box score stats (points, yards, turnovers, etc.)
- Calculated from play-by-play aggregation

### **Available But NOT Stored** (200+ metrics):
- ❌ Betting lines (spread, total, moneylines, odds)
- ❌ Weather (roof, surface, temp, wind)
- ❌ Rest days, coaches, referees
- ❌ EPA, WPA, success rate (play-level)
- ❌ Injuries
- ❌ Depth charts
- ❌ Next Gen Stats
- ❌ QBR
- ❌ Snap counts
- ❌ And 15+ more datasets...

---

## ✅ **RECOMMENDED ACTION PLAN**

### **Phase 1: Low-Hanging Fruit** (ZERO extra downloads)
**Effort**: 1-2 hours | **Value**: High

Update `ingest_historical_games.py` to store:
1. ✅ Betting lines (10 columns from schedules)
2. ✅ Weather (4 columns from schedules)  
3. ✅ Context (9 columns from schedules)

**Result**: Add 23 columns with ZERO extra API calls!

---

### **Phase 2: EPA Metrics** (Already downloaded)
**Effort**: 2-3 hours | **Value**: High

Add to `calculate_team_game_stats()`:
1. ✅ EPA per play (offense/defense)
2. ✅ Success rate (offense/defense)
3. ✅ Explosive play rate (plays > 10 yards)
4. ✅ CPOE (completion % over expected)

**Result**: Add 10-15 advanced analytics metrics.

---

### **Phase 3: Separate Downloads** (Still free)
**Effort**: 3-5 hours | **Value**: Medium-High

Add new loader functions:
1. ⏳ `load_injuries()` - 6,215 records
2. ⏳ `load_depth_charts()` - 37,312 records
3. ⏳ `load_ngs_stats()` - 614+ records
4. ⏳ `load_qbr()` - Weekly QBR
5. ⏳ `load_snap_counts()` - Playing time

**Result**: Add 5 new tables, 50+ columns.

---

## 🎯 **Betting Analytics Impact**

### **Before** (Current State):
- 1 consensus betting line source (unknown origin)
- Basic box score stats only
- 40% coverage of betting requirements

### **After Phase 1+2**:
- 1 consensus betting line (nflverse aggregate)
- Weather, rest, context data
- EPA, success rate, explosive plays
- **~70% coverage** of betting requirements

### **After Phase 3**:
- Injury impact modeling
- Depth chart analysis (backup QB situations)
- Advanced QB metrics (NGS, QBR)
- **~85% coverage** of betting requirements

---

## 💡 **Key Insights**

1. **We Already Have 23 Betting/Weather Columns**
   - In schedules data we download anyway
   - Just need to store them!

2. **nflverse Betting Lines Are "Consensus"**
   - Not from 3 specific sportsbooks (DraftKings/FanDuel/Caesars)
   - Likely averaged from multiple sources
   - Good for historical analysis
   - Not ideal for real-time line shopping

3. **EPA/Advanced Metrics Already Available**
   - Play-by-play data includes EPA, WPA, success
   - Just need to aggregate to game level

4. **24 Datasets = Endless Possibilities**
   - Injuries × Depth Charts = Backup QB models
   - NGS × Weather = Passing difficulty scores
   - Rest × Betting Lines = Schedule advantage analysis

---

## 🔗 **Resources**

- **nflverse GitHub**: https://github.com/nflverse
- **nfl_data_py Docs**: https://github.com/nflverse/nfl_data_py
- **Data Dictionary**: https://nflverse.github.io/nflverse-data/

---

## 🚀 **Next Steps**

**Immediate** (Today):
```bash
# Update ingest_historical_games.py to store betting/weather/context
# Estimated time: 1-2 hours
# Estimated value: $$$$ (23 new columns, zero extra downloads)
```

**Short-term** (This Week):
```bash
# Add EPA metrics from play-by-play
# Estimated time: 2-3 hours
# Estimated value: $$$$ (10-15 advanced metrics)
```

**Long-term** (Next Sprint):
```bash
# Add injuries, depth charts, NGS
# Estimated time: 5-10 hours
# Estimated value: $$$ (50+ new columns, 5 new tables)
```

---

**Bottom Line**: nflverse gives us **WAY MORE** than we're currently using. Let's capture it! 🚀
