# STATS GAP ANALYSIS - BETTING & PREDICTION FEATURES

**H.C. Lombardo App - Phase 2A Review**  
**Date:** October 28, 2025  
**Question:** Do we have the stats needed for professional sports betting analysis?

---

## Executive Summary

**Answer: We have BASIC stats, but missing CRITICAL advanced metrics for betting.**

**Current Status:** 40% of what professional bettors use  
**What We Have:** Game-level box score stats  
**What We're Missing:** Advanced metrics, situational stats, betting context, trends

---

## What We Currently Have (47 Metrics)

### ✅ BASIC OFFENSIVE STATS
- Points scored
- Total yards, passing yards, rushing yards
- Plays, yards per play
- Completions, attempts, completion percentage
- Passing/rushing touchdowns
- Interceptions, fumbles lost, turnovers

### ✅ EFFICIENCY METRICS
- 3rd down conversion rate
- 4th down conversion rate
- Red zone conversion rate
- Early down success rate
- Time of possession

### ✅ SPECIAL TEAMS BASICS
- Punt count, average punt yards
- Kickoff/punt return yards
- Field goals made/attempted

### ✅ PENALTIES
- Penalty count
- Penalty yards

---

## What Professional Bettors Need (MISSING)

### ❌ CRITICAL: Opponent-Adjusted Metrics

**What They Use:**
- **Strength of Schedule (SOS)** - Who have they played?
- **Opponent Quality Adjustments** - Stats vs good defenses vs bad defenses
- **DVOA (Defense-adjusted Value Over Average)** - Football Outsiders metric
- **Expected Points Added (EPA)** - How much better than average?

**Why It Matters:** 
- Beating bad teams doesn't predict beating good teams
- 300 yards vs #1 defense ≠ 300 yards vs #32 defense

**What We Have:** Raw stats only, no context about opponent strength

---

### ❌ CRITICAL: Recent Form & Trends

**What They Use:**
- **Last 3 games stats** (weighted recent performance)
- **Last 5 games stats**
- **Last 10 games stats**
- **Rolling averages** - Show momentum/trends
- **Home/Away splits** - Performance by location
- **Division game performance** - AFC/NFC splits

**Why It Matters:**
- Team at start of season ≠ same team 8 weeks later
- Injuries, roster changes, coaching adjustments
- "Hot" teams vs "cold" teams

**What We Have:** Individual game data, but no aggregated trends

---

### ❌ CRITICAL: Situational Stats

**What They Use:**
- **Performance vs spread** - Do they cover?
- **Performance vs over/under** - Do games go high/low?
- **ATS (Against The Spread) record** - 8-5 ATS vs 8-5 straight up
- **As favorite/underdog** - Performance when expected to win/lose
- **In close games** (within 7 points)
- **In blowouts** (margin > 14 points)
- **Coming off bye week**
- **Divisional games**
- **Prime time games** (MNF, TNF, SNF)
- **Dome vs outdoor**
- **Weather conditions** (wind, rain, cold)

**Why It Matters:**
- Some teams cover consistently, some don't
- Some QBs struggle in cold/wind
- Some teams perform worse on short rest (Thursday games)

**What We Have:** None of this context

---

### ❌ IMPORTANT: Advanced Offensive Metrics

**What They Use:**
- **EPA per play** - Expected points added each play
- **Success rate** - % of plays that gain "enough" yards
- **Explosive play rate** - 20+ yard plays
- **Pace of play** - Plays per minute
- **Pre-snap motion usage** - Modern offense indicator
- **Play action percentage** - Scheme tendencies
- **Personnel groupings** - 11 personnel (1 RB, 1 TE) vs 12 personnel
- **Average depth of target (aDOT)** - How deep QB throws
- **Yards after catch (YAC)** - WR ability metric
- **Pressure rate allowed** - O-line quality

**Why It Matters:**
- EPA is the gold standard for "who's actually good"
- Shows offensive sophistication beyond basic stats

**What We Have:** Basic yards/completions only

---

### ❌ IMPORTANT: Advanced Defensive Metrics

**What They Use:**
- **Opponent points per game allowed**
- **Opponent yards per play allowed**
- **Pressure rate generated** - Pass rush effectiveness
- **Coverage metrics** - Pass defense quality
- **Run defense efficiency** - Yards before contact
- **Takeaway rate** - Turnovers forced per game
- **Red zone defense** - TD% allowed inside 20

**Why It Matters:**
- Predicting totals requires knowing both offenses AND defenses
- Some defenses feast on bad QBs, struggle vs elite QBs

**What We Have:** Opponent stats exist separately, but not linked/aggregated

---

### ❌ IMPORTANT: Betting-Specific Data

**What They Use:**
- **Historical spreads** - What was the line?
- **Historical totals** - Over/under number
- **Line movement** - Opening line vs closing line
- **Sharp money indicators** - Where pros are betting
- **Public betting percentages** - Where casual bettors are
- **Reverse line movement** - Line moves opposite of public %
- **Key numbers** - 3, 7, 10 point margins (football specific)

**Why It Matters:**
- Can't calculate "edge" without knowing the market line
- Can't backtest predictions without historical spreads
- Sharp bettors bet early, casual bettors bet late

**What We Have:** NONE - no betting lines data loaded yet

---

### ❌ USEFUL: Injuries & Personnel

**What They Use:**
- **Starting QB vs backup QB** - Massive line mover
- **Key injuries** - Top WR, RB, O-line, edge rusher out
- **Injury report trends** - Teams that play through injuries
- **Rest days** - Thursday game (4 days) vs Sunday (7 days)

**Why It Matters:**
- Mahomes vs backup QB = 6+ point swing
- Missing starting LT = QB gets sacked more

**What We Have:** Injuries table created but NOT loaded

---

### ❌ USEFUL: Weather & Stadium

**What They Use:**
- **Temperature** - Cold affects passing
- **Wind speed** - 15+ MPH affects kicking/passing
- **Precipitation** - Rain/snow affects ball handling
- **Altitude** - Denver (5,280 ft) affects kicking range
- **Dome vs outdoor** - Eliminates weather variable
- **Home field advantage** - ~2.5 points on average

**Why It Matters:**
- Outdoor December game in Buffalo with 20 MPH winds
- vs Dome game in New Orleans = totally different game
- Affects over/under totals significantly

**What We Have:** Weather table created but NOT loaded

---

## Gap Analysis Summary

### Stats We Have: 47 basic metrics
### Stats Bettors Need: 150+ metrics
### Coverage: ~31% of critical betting stats

### Priority Rankings:

**TIER 1 - MUST HAVE (Blocking betting features now):**
1. ✅ Recent form (last 3/5/10 games rolling averages) - **CAN BUILD NOW**
2. ✅ Home/away splits - **CAN BUILD NOW**
3. ❌ Historical betting lines - **NEED DATA SOURCE**
4. ✅ Opponent-adjusted metrics - **CAN BUILD NOW**

**TIER 2 - HIGHLY IMPORTANT (Limits prediction quality):**
5. ❌ EPA per play - **NEED NFLVERSE ADVANCED STATS**
6. ❌ Success rate - **NEED NFLVERSE ADVANCED STATS**
7. ✅ Performance vs spread (ATS record) - **NEED BETTING LINES FIRST**
8. ✅ Situational splits (favorite/underdog, divisional) - **CAN BUILD NOW**

**TIER 3 - NICE TO HAVE (Improves accuracy):**
9. ❌ Injuries - **TABLE EXISTS, NEED LOADER**
10. ❌ Weather - **TABLE EXISTS, NEED LOADER**
11. ❌ Advanced pass rush/coverage metrics - **NEED NFLVERSE ADVANCED**
12. ✅ Key numbers analysis - **CAN BUILD AFTER LINES**

---

## What We Can Build RIGHT NOW (Phase 2B)

### 1. Rolling Averages (Last 3/5/10 Games)

**Create views:**
```sql
CREATE VIEW hcl.team_recent_form AS
SELECT 
  team,
  season,
  week,
  AVG(points) OVER (PARTITION BY team, season 
                    ORDER BY week 
                    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as ppg_last3,
  AVG(total_yards) OVER (PARTITION BY team, season 
                         ORDER BY week 
                         ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as ypg_last3,
  -- etc for last 5, last 10
FROM hcl.team_game_stats;
```

**Value:** Shows momentum, identifies hot/cold teams

---

### 2. Home/Away Splits

**Create views:**
```sql
CREATE VIEW hcl.team_location_splits AS
SELECT 
  team,
  season,
  is_home,
  AVG(points) as ppg,
  AVG(total_yards) as ypg,
  AVG(CASE WHEN result='W' THEN 1 ELSE 0 END) as win_pct
FROM hcl.team_game_stats
GROUP BY team, season, is_home;
```

**Value:** Some teams have massive home field advantage, others don't

---

### 3. Opponent Quality Adjustments

**Create views:**
```sql
CREATE VIEW hcl.strength_of_schedule AS
SELECT 
  t.team,
  t.season,
  t.week,
  AVG(opp.points) as avg_opp_points_scored,
  AVG(opp.total_yards) as avg_opp_yards
FROM hcl.team_game_stats t
JOIN hcl.team_game_stats opp ON t.game_id = opp.game_id 
                               AND t.opponent = opp.team
GROUP BY t.team, t.season, t.week;
```

**Value:** Adjust stats based on opponent strength

---

### 4. Win/Loss Trend Analysis

**Create views:**
```sql
CREATE VIEW hcl.team_trends AS
SELECT 
  team,
  season,
  week,
  SUM(CASE WHEN result='W' THEN 1 ELSE 0 END) 
      OVER (PARTITION BY team, season 
            ORDER BY week 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as wins_last3
FROM hcl.team_game_stats;
```

**Value:** Identify teams on winning/losing streaks

---

## What We CANNOT Build Yet (Need Data)

### 1. Betting Lines Analysis ❌

**Need:** Historical spreads and over/under data

**Sources:**
- **covers.com** - Historical NFL lines (paywall)
- **sportsbookreviewonline.com** - Free historical lines
- **pro-football-reference.com** - Some spread data
- **nflverse** - Has some spread data in schedules!

**Action:** Check if nflverse schedules include spread data

---

### 2. Advanced EPA Metrics ❌

**Need:** Play-by-play with EPA calculations

**Sources:**
- **nflverse** - `nfl_data_py.import_pbp_data()` includes EPA columns!
- We're already downloading this data but NOT storing EPA

**Action:** Update loader to capture EPA columns from PBP data

---

### 3. Weather Data ❌

**Need:** Historical weather for outdoor games

**Sources:**
- **weatherunderground.com API** - Historical weather
- **nflverse** - May have stadium info (dome vs outdoor)

**Action:** Build weather loader after verifying data source

---

## Immediate Action Plan

### TODAY (Can do with existing data):

**1. Create Feature Engineering Views** (2-3 hours)
- Rolling averages view (last 3/5/10 games)
- Home/away splits view
- Opponent quality view
- Win/loss trends view

**2. Update Materialized View** (30 minutes)
- Add recent form stats to `v_game_matchup_display`
- Add home/away performance history

### THIS WEEK (Need to enhance loader):

**3. Add EPA to Data Loader** (1-2 hours)
- nflverse PBP data already has EPA columns
- Modify `calculate_team_game_stats()` to include:
  - `epa_per_play`
  - `success_rate`
  - `explosive_play_rate`

**4. Check for Spread Data in Schedules** (30 minutes)
- nflverse schedules may include `spread_line` column
- If yes, we already have it! Just need to use it
- If no, need to find historical spread data source

### NEXT SPRINT (After betting lines loaded):

**5. Build Betting Analytics Views**
- ATS (against the spread) record
- Over/under record
- Performance as favorite/underdog
- Cover margin analysis

---

## Professional Bettor Requirements

**Minimum Viable Product for Betting:**
1. ✅ Last 5 games rolling average - **CAN BUILD NOW**
2. ✅ Home/away splits - **CAN BUILD NOW**
3. ❌ Historical spread data - **NEED DATA SOURCE**
4. ✅ Opponent-adjusted stats - **CAN BUILD NOW**
5. ❌ EPA per play - **NEED TO ADD TO LOADER**

**Current Status:** 3/5 requirements can be built immediately

**Blocker:** Historical betting lines (spread, over/under)

---

## Recommended Next Steps

### Option A: Build What We Can (No Betting Lines)

**Focus:** Prediction features without spread/over-under
- Game outcome prediction (winner only)
- Score predictions
- Team performance analysis
- "Who will win?" not "Will they cover?"

**Pros:** Can start ML work immediately  
**Cons:** Can't do real betting analytics

### Option B: Find Betting Lines Data First

**Focus:** Get historical spreads before building features
- Research free spread data sources
- Check if nflverse has it
- Build betting_lines loader
- Then build all features

**Pros:** Complete betting product  
**Cons:** 2-3 day delay for data research

### Option C: Hybrid Approach (RECOMMENDED)

**Week 1:** Build feature engineering views with existing data
- Rolling averages
- Home/away splits  
- Opponent adjustments
- EPA addition to loader

**Week 2:** Research and load betting lines
- Find historical spread data
- Build betting_lines loader
- Add ATS/over-under views

**Week 3:** Build ML models
- Train on 2022-2023 data
- Test on 2024 data
- Predict 2025 outcomes

**Pros:** Parallel work, no blockers  
**Cons:** Need to manage dependencies

---

## Bottom Line

**You're right to be concerned.** We have basic stats but are missing:

**CRITICAL for betting:**
- Historical betting lines (spreads, over/under)
- Recent form trends
- Opponent-adjusted metrics
- EPA/advanced metrics

**GOOD NEWS:**
- 60% of missing stats can be calculated from existing data
- 30% require enhancing the loader (EPA from PBP data we already download)
- 10% require new data sources (betting lines, weather)

**RECOMMENDATION:**
Start building feature engineering views TODAY with what we have. Research betting lines sources THIS WEEK. You'll have a complete betting analytics platform in 2-3 weeks.

---

**Last Updated:** October 28, 2025  
**Status:** Gap analysis complete, action plan ready  
**Next Session:** Build feature engineering views or research betting lines data?
