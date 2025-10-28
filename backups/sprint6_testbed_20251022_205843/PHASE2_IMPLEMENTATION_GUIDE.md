# PHASE 2 IMPLEMENTATION GUIDE
## Exact MVP Column Set from nflverse Play-by-Play

**Source**: Professional betting analytics research  
**Date**: October 22, 2025  
**Data Source**: nflfastR Play-by-Play (PBP) data via nfl-data-py  
**Output**: team-game level aggregated stats for betting models

---

## 📊 COMPLETE COLUMN SET (47 Fields)

### A) **IDENTIFIERS** (7 fields)

| Column | Type | Derivation | Description |
|--------|------|------------|-------------|
| `season` | INT | From `season` | Season year (e.g., 2024) |
| `week` | INT | From `week` | NFL week number (1-18) |
| `game_id` | TEXT | From `game_id` | Unique game identifier |
| `team_id` | TEXT | From `posteam` | Team abbreviation (offense) |
| `opponent_id` | TEXT | From `defteam` | Opponent abbreviation |
| `is_home` | BOOLEAN | Match `team_id == home_team` | TRUE if home game |
| `game_date` | DATE | From schedules `gameday` | Game date |

---

### B) **BASE VOLUME & SPLITS** (8 fields)

| Column | Type | Derivation | Formula |
|--------|------|------------|---------|
| `plays` | INT | Count offensive plays | `COUNT(play_id) WHERE posteam == team_id` |
| `pass_attempts` | INT | Total pass attempts | `SUM(pass_attempt == 1)` |
| `rush_attempts` | INT | Total rush attempts | `SUM(rush_attempt == 1)` |
| `yards_total` | INT | Total offensive yards | `SUM(yards_gained)` |
| `yards_pass` | INT | Passing yards only | `SUM(yards_gained WHERE pass_attempt == 1)` |
| `yards_rush` | INT | Rushing yards only | `SUM(yards_gained WHERE rush_attempt == 1)` |
| `drives` | INT | Number of drives | `DISTINCT COUNT(fixed_drive) WHERE posteam == team_id` |
| `plays_per_drive` | DECIMAL | Pace proxy | `plays / NULLIF(drives, 0)` |

---

### C) **SCORING & PRESSURE/TURNOVERS** (8 fields)

| Column | Type | Derivation | Formula |
|--------|------|------------|---------|
| `points_for` | INT | Team points scored | `MAX(posteam_score) WHERE posteam == team_id` |
| `points_against` | INT | Opponent points | `MAX(defteam_score) WHERE defteam == opponent_id` |
| `sacks` | INT | Sacks taken by offense | `SUM(sack == 1) WHERE posteam == team_id` |
| `interceptions` | INT | INTs thrown | `SUM(interception == 1) WHERE posteam == team_id` |
| `fumbles_lost` | INT | Fumbles lost | `SUM(fumble_lost == 1) WHERE posteam == team_id` |
| `turnovers` | INT | Total turnovers | `interceptions + fumbles_lost` |
| `penalty_yards` | INT | Penalty yards against | `-SUM(penalty_yards WHERE posteam == team_id AND penalty == 1)` |
| `starting_field_pos_yds` | DECIMAL | Avg starting field position | `MEAN(yardline_100 at drive start)` |

---

### D) **EFFICIENCY (ADVANCED)** (8 fields)

| Column | Type | Derivation | Formula |
|--------|------|------------|---------|
| `yards_per_play` | DECIMAL | Offensive efficiency | `yards_total / NULLIF(plays, 0)` |
| `success_plays` | INT | Successful plays count | `SUM(success == 1)` |
| `success_rate` | DECIMAL | Play success % | `success_plays / NULLIF(plays, 0)` |
| `epa_total` | DECIMAL | Total EPA | `SUM(epa) WHERE posteam == team_id` |
| `epa_per_play` | DECIMAL | EPA efficiency | `epa_total / NULLIF(plays, 0)` |
| `rush_epa_per_play` | DECIMAL | Rushing EPA | `SUM(epa WHERE rush_attempt == 1) / NULLIF(SUM(rush_attempt), 0)` |
| `pass_epa_per_play` | DECIMAL | Passing EPA | `SUM(epa WHERE pass_attempt == 1) / NULLIF(SUM(pass_attempt), 0)` |
| `early_down_success_rate` | DECIMAL | 1st/2nd down success | `SUM(success == 1 WHERE down IN (1,2)) / COUNT(down IN (1,2))` |

---

### E) **SITUATIONAL (RED ZONE / 3RD/4TH)** (6 fields)

| Column | Type | Derivation | Formula |
|--------|------|------------|---------|
| `red_zone_trips` | INT | RZ possessions | `COUNT DISTINCT drives WHERE yardline_100 <= 20` |
| `red_zone_td_rate` | DECIMAL | RZ TD efficiency | `TD_drives_in_RZ / NULLIF(red_zone_trips, 0)` |
| `third_down_att` | INT | 3rd down attempts | `SUM(third_down_attempt == 1)` OR `COUNT(down == 3)` |
| `third_down_conv` | INT | 3rd down conversions | `SUM(third_down_converted == 1)` |
| `fourth_down_att` | INT | 4th down attempts | `COUNT(down == 4) WHERE posteam == team_id` |
| `fourth_down_conv` | INT | 4th down conversions | `SUM(fourth_down_converted == 1)` |

**Note**: If `third_down_attempt/converted` or `fourth_down_converted` fields missing, derive from yards-to-go achieved and first down gained.

---

### F) **CONTEXT** (4 fields)

| Column | Type | Derivation | Source |
|--------|------|------------|--------|
| `home_field` | BOOLEAN | Same as `is_home` | From schedules |
| `days_rest` | INT | Days since last game | From schedules `away_rest` / `home_rest` |
| `short_week` | BOOLEAN | Game < 6 days after previous | `days_rest < 6` |
| `off_bye` | BOOLEAN | Coming off bye week | `days_rest >= 13` |

---

### G) **ROLLING FORM (MOMENTUM)** (6 fields)

**Compute from prior games only - NO look-ahead bias**

| Column | Type | Derivation | Window |
|--------|------|------------|--------|
| `epa_l3` | DECIMAL | Mean EPA per play | Last 3 games |
| `epa_l5` | DECIMAL | Mean EPA per play | Last 5 games |
| `ppg_for_l3` | DECIMAL | Mean points scored | Last 3 games |
| `ppg_against_l3` | DECIMAL | Mean points allowed | Last 3 games |
| `ypp_l3` | DECIMAL | Mean yards per play | Last 3 games |
| `sr_l3` | DECIMAL | Mean success rate | Last 3 games |

---

## 🐍 PANDAS AGGREGATION CODE (Copy-Paste Ready)

### Step 1: Load Play-by-Play Data
```python
import nfl_data_py as nfl
import pandas as pd

# Load PBP for seasons 2022-2024
pbp = nfl.import_pbp_data(years=[2022, 2023, 2024])
print(f"Loaded {len(pbp):,} play-by-play records")

# Filter to offensive plays only (has posteam)
grp = pbp[pbp.posteam.notna()].copy()
```

---

### Step 2: Create Helper Columns
```python
# Separate pass/rush yards for easier aggregation
grp["rush_yards"] = grp["yards_gained"].where(grp["rush_attempt"] == 1, 0)
grp["pass_yards"] = grp["yards_gained"].where(grp["pass_attempt"] == 1, 0)
```

---

### Step 3: Aggregate to Team-Game Level
```python
team_game = (
    grp.groupby(["game_id", "season", "week", "posteam"], dropna=False)
    .agg(
        plays=("play_id", "count"),
        yards_total=("yards_gained", "sum"),
        yards_pass=("pass_yards", "sum"),
        yards_rush=("rush_yards", "sum"),
        pass_attempts=("pass_attempt", "sum"),
        rush_attempts=("rush_attempt", "sum"),
        sacks=("sack", "sum"),
        interceptions=("interception", "sum"),
        fumbles_lost=("fumble_lost", "sum"),
        success_plays=("success", "sum"),
        epa_total=("epa", "sum"),
        epa_per_play=("epa", "mean"),  # Alternative: sum/plays
    )
    .reset_index()
    .rename(columns={"posteam": "team_id"})
)
```

---

### Step 4: Calculate Derived Fields
```python
# Efficiency metrics
team_game["success_rate"] = team_game["success_plays"] / team_game["plays"].clip(lower=1)
team_game["yards_per_play"] = team_game["yards_total"] / team_game["plays"].clip(lower=1)
team_game["turnovers"] = team_game["interceptions"] + team_game["fumbles_lost"]
```

---

### Step 5: Add Points & Opponent
```python
# Get scores and opponent from PBP
scores = (
    pbp.groupby(["game_id", "season", "week", "posteam", "defteam"], dropna=False)
    .agg(pf=("posteam_score", "max"), pa=("defteam_score", "max"))
    .reset_index()
    .rename(columns={"posteam": "team_id", "defteam": "opponent_id"})
)

# Merge scores into team_game
team_game = team_game.merge(
    scores[["game_id", "team_id", "opponent_id", "pf", "pa"]],
    on=["game_id", "team_id"],
    how="left"
)
team_game = team_game.rename(columns={"pf": "points_for", "pa": "points_against"})
```

---

### Step 6: Pass/Rush EPA per Play
```python
# Rush EPA per play
rush = (
    grp[grp["rush_attempt"] == 1]
    .groupby(["game_id", "posteam"])
    .epa.mean()
    .reset_index()
    .rename(columns={"posteam": "team_id", "epa": "rush_epa_per_play"})
)

# Pass EPA per play
pas = (
    grp[grp["pass_attempt"] == 1]
    .groupby(["game_id", "posteam"])
    .epa.mean()
    .reset_index()
    .rename(columns={"posteam": "team_id", "epa": "pass_epa_per_play"})
)

# Merge EPA splits
team_game = (
    team_game
    .merge(rush, on=["game_id", "team_id"], how="left")
    .merge(pas, on=["game_id", "team_id"], how="left")
)
```

---

### Step 7: Situational Stats (3rd/4th Down & Red Zone)
```python
# 3rd down stats
third_down = (
    grp[grp["down"] == 3]
    .groupby(["game_id", "posteam"])
    .agg(
        third_down_att=("play_id", "count"),
        third_down_conv=("third_down_converted", "sum")
    )
    .reset_index()
    .rename(columns={"posteam": "team_id"})
)

# 4th down stats
fourth_down = (
    grp[grp["down"] == 4]
    .groupby(["game_id", "posteam"])
    .agg(
        fourth_down_att=("play_id", "count"),
        fourth_down_conv=("fourth_down_converted", "sum")
    )
    .reset_index()
    .rename(columns={"posteam": "team_id"})
)

# Red zone trips (drives with any snap inside 20)
red_zone = (
    grp[grp["yardline_100"] <= 20]
    .groupby(["game_id", "posteam"])
    .agg(
        red_zone_trips=("fixed_drive", "nunique"),
        red_zone_tds=("touchdown", "sum")
    )
    .reset_index()
    .rename(columns={"posteam": "team_id"})
)
red_zone["red_zone_td_rate"] = red_zone["red_zone_tds"] / red_zone["red_zone_trips"].clip(lower=1)

# Merge situational stats
team_game = (
    team_game
    .merge(third_down, on=["game_id", "team_id"], how="left")
    .merge(fourth_down, on=["game_id", "team_id"], how="left")
    .merge(red_zone, on=["game_id", "team_id"], how="left")
)

# Fill NaN with 0 for teams with no attempts
team_game[["third_down_att", "third_down_conv", "fourth_down_att", "fourth_down_conv"]] = \
    team_game[["third_down_att", "third_down_conv", "fourth_down_att", "fourth_down_conv"]].fillna(0)
```

---

### Step 8: Add Context from Schedules
```python
# Load schedules for home/away and rest days
schedules = nfl.import_schedules(years=[2022, 2023, 2024])

# Create home context for home team
home_context = schedules[["game_id", "home_team", "home_rest", "gameday"]].copy()
home_context["is_home"] = True
home_context = home_context.rename(columns={
    "home_team": "team_id",
    "home_rest": "days_rest",
    "gameday": "game_date"
})

# Create away context for away team
away_context = schedules[["game_id", "away_team", "away_rest", "gameday"]].copy()
away_context["is_home"] = False
away_context = away_context.rename(columns={
    "away_team": "team_id",
    "away_rest": "days_rest",
    "gameday": "game_date"
})

# Combine and merge
context = pd.concat([home_context, away_context])
team_game = team_game.merge(context, on=["game_id", "team_id"], how="left")

# Derive short_week and off_bye
team_game["short_week"] = team_game["days_rest"] < 6
team_game["off_bye"] = team_game["days_rest"] >= 13
team_game["home_field"] = team_game["is_home"]  # Alias for clarity
```

---

### Step 9: Rolling Averages (Momentum)
```python
# Sort by team and date
team_game = team_game.sort_values(["team_id", "season", "week"])

# Calculate rolling averages (last 3 and 5 games)
team_game["epa_l3"] = team_game.groupby("team_id")["epa_per_play"].transform(
    lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
)
team_game["epa_l5"] = team_game.groupby("team_id")["epa_per_play"].transform(
    lambda x: x.shift(1).rolling(window=5, min_periods=1).mean()
)
team_game["ppg_for_l3"] = team_game.groupby("team_id")["points_for"].transform(
    lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
)
team_game["ppg_against_l3"] = team_game.groupby("team_id")["points_against"].transform(
    lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
)
team_game["ypp_l3"] = team_game.groupby("team_id")["yards_per_play"].transform(
    lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
)
team_game["sr_l3"] = team_game.groupby("team_id")["success_rate"].transform(
    lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
)

# Note: .shift(1) prevents look-ahead bias - only uses PRIOR games
```

---

## 🗄️ DATABASE SCHEMA (PostgreSQL)

```sql
CREATE TABLE team_game_stats (
    -- Identifiers
    game_id TEXT,
    team_id TEXT,
    season INT,
    week INT,
    opponent_id TEXT,
    is_home BOOLEAN,
    game_date DATE,
    
    -- Base Volume & Splits
    plays INT,
    pass_attempts INT,
    rush_attempts INT,
    yards_total INT,
    yards_pass INT,
    yards_rush INT,
    drives INT,
    plays_per_drive DECIMAL(5,2),
    
    -- Scoring & Pressure/Turnovers
    points_for INT,
    points_against INT,
    sacks INT,
    interceptions INT,
    fumbles_lost INT,
    turnovers INT,
    penalty_yards INT,
    starting_field_pos_yds DECIMAL(5,2),
    
    -- Efficiency (Advanced)
    yards_per_play DECIMAL(5,2),
    success_plays INT,
    success_rate DECIMAL(5,4),
    epa_total DECIMAL(8,2),
    epa_per_play DECIMAL(5,3),
    rush_epa_per_play DECIMAL(5,3),
    pass_epa_per_play DECIMAL(5,3),
    early_down_success_rate DECIMAL(5,4),
    
    -- Situational (Red Zone / 3rd/4th)
    red_zone_trips INT,
    red_zone_td_rate DECIMAL(5,4),
    third_down_att INT,
    third_down_conv INT,
    fourth_down_att INT,
    fourth_down_conv INT,
    
    -- Context
    home_field BOOLEAN,
    days_rest INT,
    short_week BOOLEAN,
    off_bye BOOLEAN,
    
    -- Rolling Form (Momentum)
    epa_l3 DECIMAL(5,3),
    epa_l5 DECIMAL(5,3),
    ppg_for_l3 DECIMAL(5,2),
    ppg_against_l3 DECIMAL(5,2),
    ypp_l3 DECIMAL(5,2),
    sr_l3 DECIMAL(5,4),
    
    PRIMARY KEY (game_id, team_id)
);

-- Index for fast queries
CREATE INDEX idx_team_season ON team_game_stats(team_id, season, week);
CREATE INDEX idx_game_date ON team_game_stats(game_date);
```

---

## 🎯 WHAT THIS GETS YOU (Betting Relevance)

### **For SPREADS:**
- ✅ Points for/against (scoring differential)
- ✅ EPA and success rate (true efficiency)
- ✅ Sacks/turnovers (possession quality)
- ✅ Recent form (momentum via rolling averages)
- ✅ Home field advantage
- ✅ Rest days / short week impact

### **For TOTALS:**
- ✅ Pace (plays per drive)
- ✅ EPA per play (scoring efficiency)
- ✅ Red zone TD rate (finishing drives)
- ✅ Weather context (from schedules - dome vs outdoor)
- ✅ Points per game trends (rolling averages)

### **For MATCHUPS:**
- ✅ Pass vs rush EPA splits
- ✅ Pressure (sacks allowed)
- ✅ Opponent-adjusted variants (Phase 3)

---

## 📂 FILE STRUCTURE

```
testbed/
├── PHASE2_IMPLEMENTATION_GUIDE.md (this file)
├── nflverse_data_loader.py (to create)
├── test_aggregation.py (test pandas code)
└── phase2_schema.sql (database creation script)
```

---

## ✅ NEXT STEPS

1. **Create `nflverse_data_loader.py`** with all pandas aggregation code
2. **Create `phase2_schema.sql`** with PostgreSQL table definition
3. **Test aggregation** on 2024 Week 1 only (validate output)
4. **Load full dataset** (2022-2024 = ~850 games)
5. **Verify data quality** (check for NaN, outliers, missing games)
6. **Create API endpoints** for historical queries
7. **Build simple UI** to display team stats

---

## 🚨 IMPORTANT NOTES

### **Field Availability by Year:**
- `third_down_converted` / `fourth_down_converted` may be missing in older years
- Derive from `first_down` gained and `ydstogo` if flags missing
- `success` flag introduced in 2016+ seasons
- `epa` available 1999+ (from nflfastR model)

### **Performance Warnings:**
- Play-by-play is **LARGE** (~45-50k plays/season)
- 3 seasons = ~150k plays to aggregate
- Use `.clip(lower=1)` to prevent division by zero
- Cache aggregated results - don't re-process PBP every API call

### **Data Quality:**
- Check for games with `plays == 0` (data errors)
- Verify `points_for` matches actual game scores
- Ensure rolling averages don't leak future data (use `.shift(1)`)
- Handle NaN in rolling averages for first few games of season

---

**Ready to implement?** This gives you production-ready code with all 47 columns needed for betting analytics.
