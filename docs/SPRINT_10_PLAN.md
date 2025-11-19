# Sprint 10 Plan: Custom Query Builder

**Sprint Duration:** November 14-20, 2025 (Week 8)  
**Phase:** 3B - Interactive Analytics  
**Sprint Goal:** Transform Custom Builder tab from "Coming Soon" to fully functional stat selection tool  
**Status:** 📋 Planned (Starts after Sprint 9)  
**Prerequisites:** Sprint 9 ML predictions complete

---

## 🎯 Sprint Objectives

### Primary Goal
Enable users to build custom queries by selecting specific stats, filters, and display options to create personalized analytics views from 950+ historical games.

### Success Criteria
- ✅ Multi-select stat picker (checkboxes for 35 available metrics)
- ✅ Team filter (single team, multiple teams, or all teams)
- ✅ Season/week filter with range selection
- ✅ Results display in sortable table
- ✅ Export results to CSV
- ✅ Save/load custom queries (localStorage)
- ✅ Query templates (e.g., "Top Offenses", "Best Defenses")

---

## 📋 Sprint Backlog

### Task 1: Backend - Custom Query API Endpoint
**Estimated Time:** 3-4 hours  
**Priority:** HIGH  
**Dependencies:** None

**Subtasks:**
1. Create new endpoint: `POST /api/hcl/custom-query`
2. Accept dynamic stat selection in request body
3. Build dynamic SQL query based on user selections
4. Support filtering by team, season, week range
5. Support sorting by any selected stat
6. Return results in standardized JSON format
7. Add error handling for invalid stat combinations
8. Write API tests (8+ test cases)

**Request Format:**
```json
POST /api/hcl/custom-query
{
  "stats": ["points_scored", "epa_per_play", "success_rate", "yards_per_play"],
  "teams": ["DAL", "PHI"],  // Optional, empty = all teams
  "season": 2024,
  "week_range": [1, 8],  // Optional, empty = all weeks
  "sort_by": "points_scored",
  "sort_order": "DESC",
  "limit": 100  // Optional
}
```

**Response Format:**
```json
{
  "results": [
    {
      "team": "DAL",
      "opponent": "NYG",
      "week": 1,
      "points_scored": 35,
      "epa_per_play": 0.23,
      "success_rate": 0.52,
      "yards_per_play": 6.8
    }
  ],
  "count": 42,
  "query_info": {
    "stats_selected": 4,
    "teams_filtered": 2,
    "games_found": 42
  }
}
```

**Files to Create/Modify:**
- `api_routes_hcl.py` - Add custom query endpoint (MODIFY)
- `testbed/test_custom_query_api.py` - API tests (NEW)

---

### Task 2: Frontend - Stat Selection Interface
**Estimated Time:** 4-5 hours  
**Priority:** HIGH  
**Dependencies:** Task 1

**Subtasks:**
1. Replace "Coming Soon" message in CustomBuilder.js
2. Create stat category groups (Offense, Defense, Efficiency, Situational)
3. Build checkbox interface for stat selection
4. Add "Select All" / "Clear All" buttons per category
5. Implement team multi-select dropdown
6. Add season selector
7. Add week range slider (Week 1-18)
8. Add sort controls (stat to sort by, ascending/descending)
9. Add result limit selector (10, 25, 50, 100, All)

**Stat Categories:**
```javascript
const STAT_CATEGORIES = {
  offense: {
    label: "Offensive Stats",
    stats: [
      { id: "points_scored", label: "Points Scored", abbr: "PTS" },
      { id: "total_yards", label: "Total Yards", abbr: "YDS" },
      { id: "pass_yards", label: "Passing Yards", abbr: "PASS" },
      { id: "rush_yards", label: "Rushing Yards", abbr: "RUSH" },
      { id: "turnovers_lost", label: "Turnovers", abbr: "TO" }
    ]
  },
  defense: {
    label: "Defensive Stats",
    stats: [
      { id: "points_allowed", label: "Points Allowed", abbr: "PA" },
      { id: "sacks", label: "Sacks", abbr: "SACK" },
      { id: "interceptions", label: "Interceptions", abbr: "INT" }
    ]
  },
  efficiency: {
    label: "Efficiency Stats",
    stats: [
      { id: "epa_per_play", label: "EPA per Play", abbr: "EPA" },
      { id: "success_rate", label: "Success Rate", abbr: "SR%" },
      { id: "yards_per_play", label: "Yards per Play", abbr: "YPP" },
      { id: "third_down_rate", label: "3rd Down %", abbr: "3RD%" },
      { id: "red_zone_efficiency", label: "Red Zone %", abbr: "RZ%" }
    ]
  },
  situational: {
    label: "Situational Stats",
    stats: [
      { id: "time_of_possession", label: "Time of Possession", abbr: "TOP" },
      { id: "first_downs", label: "First Downs", abbr: "1ST" },
      { id: "penalties", label: "Penalties", abbr: "PEN" }
    ]
  }
};
```

**Files to Create/Modify:**
- `frontend/src/CustomBuilder.js` - Complete rewrite (MODIFY)
- `frontend/src/CustomBuilder.css` - Styling for builder interface (NEW)
- `frontend/src/components/StatSelector.js` - Stat checkbox component (NEW)
- `frontend/src/components/FilterPanel.js` - Filter controls (NEW)

---

### Task 3: Frontend - Results Display & Export
**Estimated Time:** 3-4 hours  
**Priority:** MEDIUM  
**Dependencies:** Task 1, Task 2

**Subtasks:**
1. Create sortable results table component
2. Implement click-to-sort column headers
3. Add CSV export button
4. Format numbers properly (decimals, percentages)
5. Add "No results" empty state
6. Add loading spinner during API calls
7. Add pagination for large result sets
8. Color-code high/low values (green for good, red for bad)

**Features:**
- Sortable columns (click header to sort)
- CSV export with filename: `hcl_custom_query_YYYYMMDD_HHMMSS.csv`
- Responsive table (horizontal scroll on mobile)
- Visual indicators (🟢 top 25%, 🔴 bottom 25%)
- Pagination controls (if >100 results)

**CSV Export Format:**
```csv
Team,Opponent,Week,Season,Points Scored,EPA per Play,Success Rate,Yards per Play
DAL,NYG,1,2024,35,0.23,0.52,6.8
PHI,WAS,2,2024,31,0.19,0.48,6.2
```

**Files to Create/Modify:**
- `frontend/src/components/ResultsTable.js` - Results display (NEW)
- `frontend/src/components/ResultsTable.css` - Table styling (NEW)
- `frontend/src/utils/exportCSV.js` - CSV export utility (NEW)
- `frontend/src/utils/formatStats.js` - Number formatting (NEW)

---

### Task 4: Query Management (Save/Load)
**Estimated Time:** 2-3 hours  
**Priority:** LOW  
**Dependencies:** Task 2, Task 3

**Subtasks:**
1. Implement save query functionality (localStorage)
2. Display saved queries in dropdown
3. Load saved query on selection
4. Delete saved queries
5. Rename saved queries
6. Export/import query configurations (JSON)

**Storage Format:**
```javascript
{
  "saved_queries": [
    {
      "id": "uuid-1",
      "name": "Top Offenses 2024",
      "config": {
        "stats": ["points_scored", "total_yards", "epa_per_play"],
        "teams": [],
        "season": 2024,
        "week_range": [1, 18],
        "sort_by": "points_scored",
        "sort_order": "DESC"
      },
      "created_at": "2024-11-14T10:30:00"
    }
  ]
}
```

**Features:**
- Save current query with custom name
- Quick load from saved queries dropdown
- Delete unwanted queries
- Rename existing queries
- Share query (copy as JSON)

**Files to Create/Modify:**
- `frontend/src/components/QueryManager.js` - Save/load UI (NEW)
- `frontend/src/utils/queryStorage.js` - localStorage utilities (NEW)

---

### Task 5: Query Templates
**Estimated Time:** 2 hours  
**Priority:** LOW  
**Dependencies:** Task 2, Task 3

**Subtasks:**
1. Create pre-built query templates
2. Add "Load Template" dropdown
3. Implement template configurations

**Pre-Built Templates:**
```javascript
const QUERY_TEMPLATES = {
  topOffenses: {
    name: "Top Offenses",
    description: "Highest scoring teams by PPG",
    config: {
      stats: ["points_scored", "total_yards", "epa_per_play", "success_rate"],
      teams: [],
      season: 2024,
      sort_by: "points_scored",
      sort_order: "DESC",
      limit: 10
    }
  },
  bestDefenses: {
    name: "Best Defenses",
    description: "Lowest points allowed",
    config: {
      stats: ["points_allowed", "sacks", "interceptions", "yards_per_play"],
      teams: [],
      season: 2024,
      sort_by: "points_allowed",
      sort_order: "ASC",
      limit: 10
    }
  },
  efficiencyLeaders: {
    name: "Efficiency Leaders",
    description: "Best EPA and success rate",
    config: {
      stats: ["epa_per_play", "success_rate", "yards_per_play", "third_down_rate"],
      teams: [],
      season: 2024,
      sort_by: "epa_per_play",
      sort_order: "DESC",
      limit: 10
    }
  },
  redZoneElite: {
    name: "Red Zone Elite",
    description: "Best red zone scoring",
    config: {
      stats: ["red_zone_efficiency", "red_zone_att", "red_zone_scores"],
      teams: [],
      season: 2024,
      sort_by: "red_zone_efficiency",
      sort_order: "DESC",
      limit: 10
    }
  },
  turnoverBattle: {
    name: "Turnover Battle",
    description: "Turnovers created vs lost",
    config: {
      stats: ["turnovers_lost", "interceptions", "fumbles_recovered"],
      teams: [],
      season: 2024,
      sort_by: "turnovers_lost",
      sort_order: "ASC",
      limit: 10
    }
  }
};
```

**Files to Create:**
- `frontend/src/data/queryTemplates.js` - Template definitions (NEW)

---

### Task 6: Testing & Documentation
**Estimated Time:** 2 hours  
**Priority:** MEDIUM  
**Dependencies:** All above tasks

**Subtasks:**
1. Manual testing of all stat combinations
2. Test edge cases (no stats selected, invalid teams)
3. Test CSV export with various data sizes
4. Test query save/load persistence
5. Update API documentation
6. Add user guide section to dr.foster.md

**Test Scenarios:**
- [ ] Select 1 stat, 1 team → Simple query works
- [ ] Select 10 stats, all teams → Large dataset displays
- [ ] Select invalid stat combination → Error handling
- [ ] Export to CSV → File downloads correctly
- [ ] Save query → Appears in saved list
- [ ] Load saved query → Restores all selections
- [ ] Delete saved query → Removed from list
- [ ] Load template → Pre-fills form correctly
- [ ] Sort by different columns → Sorting accurate
- [ ] Filter by week range → Only shows specified weeks

**Files to Create/Modify:**
- `testbed/test_custom_builder_full.py` - Integration tests (NEW)
- `dr.foster.md` - Add Custom Builder documentation (MODIFY)
- `API_DOCUMENTATION.md` - Document custom query endpoint (MODIFY)

---

## 🗓️ Sprint Timeline

### Day 1 (Nov 14) - Backend API
- [ ] Sprint 10 kickoff
- [ ] Create custom query endpoint
- [ ] Write API tests
- [ ] Test with Postman/curl
- [ ] Verify dynamic SQL generation

### Day 2 (Nov 15) - Frontend Foundation
- [ ] Build stat selection interface
- [ ] Create category groupings
- [ ] Add team/season filters
- [ ] Add week range slider
- [ ] Connect to API endpoint

### Day 3 (Nov 16) - Results Display
- [ ] Create results table component
- [ ] Implement sorting functionality
- [ ] Add CSV export
- [ ] Style results display
- [ ] Add loading states

### Day 4 (Nov 17) - Query Management
- [ ] Implement save query functionality
- [ ] Add load saved queries dropdown
- [ ] Add delete/rename capabilities
- [ ] Test localStorage persistence
- [ ] Add query templates

### Day 5 (Nov 18) - Testing & Polish
- [ ] Manual testing all features
- [ ] Fix bugs discovered in testing
- [ ] Update documentation
- [ ] Performance optimization
- [ ] Production deployment

### Days 6-7 (Nov 19-20) - Buffer & Stretch Goals
- [ ] Add advanced filters (min/max thresholds)
- [ ] Add data visualization toggle (table vs chart)
- [ ] Add query sharing (URL parameters)
- [ ] Add query history tracking
- [ ] Sprint 10 retrospective

---

## 🎨 UI/UX Design

### Layout
```
┌─────────────────────────────────────────────────┐
│  🔍 Custom Query Builder                        │
├─────────────────────────────────────────────────┤
│  Load Template: [Top Offenses ▼]               │
│  Load Saved Query: [My Queries ▼]              │
│                                                  │
│  📊 Select Stats                                │
│  ┌─────────────┬─────────────┬─────────────┐   │
│  │ Offense     │ Defense     │ Efficiency  │   │
│  │ ☑ Points    │ ☐ Points    │ ☑ EPA/Play  │   │
│  │ ☑ Yards     │ ☐ Pass Yds  │ ☑ Success % │   │
│  │ ☐ Pass Yds  │ ☐ Sacks     │ ☐ Yards/Ply │   │
│  │ [Select All]│ [Select All]│ [Select All]│   │
│  └─────────────┴─────────────┴─────────────┘   │
│                                                  │
│  🏈 Filters                                     │
│  Teams: [☐ DAL ☐ PHI ☐ NYG ... (Select) ▼]    │
│  Season: [2024 ▼]                               │
│  Weeks: [1 ━━━━●━━━━ 18] (Range slider)        │
│                                                  │
│  🔍 Sort & Display                              │
│  Sort By: [Points Scored ▼] [DESC ▼]           │
│  Results Limit: [50 ▼]                         │
│                                                  │
│  [Run Query] [Clear] [Save Query]              │
├─────────────────────────────────────────────────┤
│  📈 Results (42 games found)                    │
│  [Export to CSV] [Save as Template]             │
│  ┌──────┬─────┬────┬────────┬─────────┬──────┐ │
│  │ Team │ Opp │ Wk │ Points │ EPA/Play│ SR%  │ │
│  │ ▲DAL │ NYG │ 1  │   35 🟢│   0.23  │ 52%  │ │
│  │  PHI │ WAS │ 2  │   31   │   0.19  │ 48%  │ │
│  │  DAL │ ARI │ 3  │   28   │   0.15  │ 45%  │ │
│  └──────┴─────┴────┴────────┴─────────┴──────┘ │
│  Showing 1-10 of 42 | [< 1 2 3 4 5 >]          │
└─────────────────────────────────────────────────┘
```

### Color Scheme
- Match existing Analytics dashboard colors
- Green checkboxes for selected stats
- Blue "Run Query" button (primary action)
- Grey "Clear" button (secondary action)
- Gold "Save Query" button (match H.C. LOMBARDO branding)
- 🟢 Green indicators for top 25% performers
- 🔴 Red indicators for bottom 25% performers

### Responsive Behavior
- **Desktop (>1200px):** 4-column stat selection, full table
- **Tablet (768-1199px):** 2-column stat selection, scrollable table
- **Mobile (<768px):** 1-column stat selection, card-based results

---

## 🧪 Testing Strategy

### Unit Tests (Backend)
- `test_custom_query_endpoint()` - API returns correct data
- `test_stat_filtering()` - Only selected stats returned
- `test_team_filtering()` - Only selected teams returned
- `test_week_range_filtering()` - Week range works correctly
- `test_sorting()` - Sorting by different columns
- `test_empty_results()` - Handle no matches gracefully
- `test_invalid_stats()` - Error handling for bad stat names
- `test_sql_injection()` - Prevent SQL injection attacks

### Integration Tests (Full Stack)
- Frontend → API → Database → Frontend (complete flow)
- Large datasets (all teams, all stats) perform well (<3 seconds)
- CSV export generates valid files
- Query save/load persists correctly across page refreshes

### Manual Testing Checklist
- [ ] Select 1 stat → Returns data
- [ ] Select all stats → Table displays correctly
- [ ] Filter by 1 team → Shows only that team
- [ ] Filter by multiple teams → Shows all selected
- [ ] Filter by season → Shows only that season
- [ ] Filter by week range → Shows only specified weeks
- [ ] Sort ascending → Data sorted correctly
- [ ] Sort descending → Data sorted correctly
- [ ] Export CSV → File downloads with correct data
- [ ] Save query → Appears in saved queries list
- [ ] Load saved query → Restores all selections
- [ ] Delete saved query → Removed from list
- [ ] Load template → Pre-fills form correctly
- [ ] No stats selected → Shows error message
- [ ] Invalid team abbreviation → Shows error

---

## 🚀 Definition of Done

### Sprint 10 Complete When:
- ✅ Custom Builder tab fully functional (no "Coming Soon")
- ✅ Users can select from 35 available stats across 4 categories
- ✅ Users can filter by team, season, and week range
- ✅ Results display in sortable, paginated table
- ✅ CSV export works correctly with proper formatting
- ✅ Save/load queries works with localStorage
- ✅ 5 query templates available for quick access
- ✅ All API tests pass (8/8)
- ✅ All manual tests pass (15/15)
- ✅ Documentation updated (dr.foster.md, API docs)
- ✅ Code committed to GitHub
- ✅ Production deployment successful
- ✅ Sprint 10 retrospective complete

---

## 📈 Sprint Metrics

**Estimated Effort:** 16-20 hours  
**Team Velocity:** ~20 hours/week  
**Confidence Level:** HIGH (building on existing patterns from Sprint 9)

**Risk Assessment:**
- 🟢 LOW RISK: API endpoint (similar to ML prediction endpoint)
- 🟢 LOW RISK: Frontend forms (experience from Analytics dashboard)
- 🟢 LOW RISK: CSV export (standard library functionality)
- 🟢 LOW RISK: localStorage (built-in browser API)

---

## 🔗 Dependencies

**Technical Dependencies:**
- PostgreSQL database (READY ✅)
- Flask API server (READY ✅)
- React frontend (READY ✅)
- HCL schema with 35+ stats available (READY ✅)
- Sprint 9 ML predictions complete (PREREQUISITE)

**External Dependencies:**
- None! All functionality self-contained

---

## 📚 Reference Materials

**Similar Implementations:**
- Team Stats page (dropdown selection pattern)
- Analytics tabs (filter controls pattern)
- Historical Data page (table display pattern)
- ML Predictions tab (API integration pattern from Sprint 9)

**Libraries to Use:**
- React (UI components)
- Flask (API endpoint)
- psycopg2 (database queries)
- Python csv module (CSV export)
- localStorage API (query persistence)

---

## 🎯 Stretch Goals (If Time Permits)

1. **Advanced Filters** - Add min/max thresholds
   - e.g., "Show teams with EPA > 0.1"
   - Range sliders for numeric stats

2. **Data Visualization Toggle** - Switch between table and chart view
   - Bar chart for selected stats
   - Line chart for trends over weeks
   - Radar chart for multi-stat comparison

3. **Share Query** - Generate shareable URL with query parameters
   - Copy link to clipboard
   - Load query from URL on page load

4. **Query History** - Track last 10 queries run (separate from saved)
   - Show timestamp for each query
   - Quick re-run from history

5. **Comparison Mode** - Compare two teams side-by-side
   - Select Team A and Team B
   - Show stats in parallel columns
   - Highlight differences

6. **Export to PDF** - Generate PDF report with results
   - Include charts and visualizations
   - Professional formatting

---

**Sprint Created:** November 6, 2025  
**Sprint Owner:** April V  
**Course:** IS330 (Weeks 6-8)  
**Previous Sprint:** Sprint 9 - ML Predictions  
**Next Review:** November 20, 2025
