# H.C. Lombardo NFL Analytics Database - Structure & 3NF Analysis

## Current Database Schema Overview

Your NFL Analytics database currently has **3 tables** in PostgreSQL:

### 1. TEAMS Table (Main Data)
```sql
CREATE TABLE teams (
    id              SERIAL PRIMARY KEY,     -- Auto-incrementing unique identifier
    name            TEXT NOT NULL,          -- Full team name (e.g., "Detroit Lions")
    abbreviation    TEXT,                   -- Team code (e.g., "DET")
    wins            INTEGER,                -- Total wins this season
    losses          INTEGER,                -- Total losses this season
    ties            INTEGER,                -- Total ties this season
    ppg             REAL,                   -- Points per game (offense)
    pa              REAL,                   -- Points allowed per game (defense)
    games_played    INTEGER,                -- Total games played
    stats           JSONB,                  -- Flexible JSON storage for 100+ stats
    last_updated    TIMESTAMP               -- When data was last refreshed
);
```
**Current Records:** 32 teams (all NFL teams)

### 2. STATS_METADATA Table (Stat Definitions)
```sql
CREATE TABLE stats_metadata (
    stat_key        VARCHAR(100) PRIMARY KEY,   -- Unique identifier (e.g., "offense.points_per_game")
    stat_name       VARCHAR(200),               -- Human-readable name
    category        VARCHAR(50),                -- Category (offense, defense, record)
    data_type       VARCHAR(20),                -- Data type (integer, float)
    description     TEXT,                       -- Full description
    source          VARCHAR(100),               -- Data source (ESPN, TeamRankings, etc.)
    last_updated    TIMESTAMP                   -- When definition was updated
);
```
**Current Records:** 9 stat definitions
**Purpose:** Documents all available statistics and their meanings

### 3. UPDATE_METADATA Table (System Tracking)
```sql
CREATE TABLE update_metadata (
    id              SERIAL PRIMARY KEY,
    last_update     TIMESTAMP
);
```
**Current Records:** 9 records
**Purpose:** Tracks when data refresh operations occurred

---

## Third Normal Form (3NF) Analysis

### What is Third Normal Form?

**Third Normal Form (3NF)** is a database design principle that ensures data is organized efficiently without redundancy. A table is in 3NF if:

1. ✅ **First Normal Form (1NF)**: All columns contain atomic (indivisible) values
2. ✅ **Second Normal Form (2NF)**: No partial dependencies (all non-key columns depend on the ENTIRE primary key)
3. ✅ **Third Normal Form (3NF)**: No transitive dependencies (non-key columns don't depend on other non-key columns)

### How Your Database Measures Up

#### ✅ **TEAMS Table - Compliant with 3NF**

**1NF Check: Are all values atomic?**
- ✅ **YES** - Each column contains single values
- ✅ `name` = "Detroit Lions" (single text value)
- ✅ `wins` = 5 (single integer)
- ✅ `ppg` = 34.8 (single float)
- ✅ `stats` = JSONB (treated as single complex value by PostgreSQL)

**2NF Check: Are there partial dependencies?**
- ✅ **YES** - Primary key is `id` (single column)
- Since the primary key is just one column, it's impossible to have partial dependencies
- All other columns depend on `id` (the team's unique identifier)

**3NF Check: Are there transitive dependencies?**
- ✅ **YES - COMPLIANT** with one consideration:

**Potential Issue:** `ppg` and `games_played`
- In theory, you could calculate total points: `total_points = ppg × games_played`
- This creates a **functional dependency**: `ppg` and `games_played` → `total_points`
- However, you're NOT storing `total_points` as a separate column
- ✅ **Solution:** You store it in the JSONB `stats` column as calculated data, which is acceptable

**Why the JSONB `stats` column is OK:**
- JSONB is designed for semi-structured, flexible data
- It's treated as a single attribute (blob of data)
- It stores both raw stats AND calculated stats
- It doesn't violate 3NF because it's not creating dependencies between table columns

**No problematic transitive dependencies found** like:
- ❌ `conference_name` depending on `division_id` (would need separate Divisions table)
- ❌ `coach_name` depending on `team_id` (would need separate Coaches table)

#### ✅ **STATS_METADATA Table - Fully 3NF Compliant**

**1NF Check:**
- ✅ All atomic values

**2NF Check:**
- ✅ Primary key is `stat_key` (single column)
- All columns depend directly on `stat_key`

**3NF Check:**
- ✅ No transitive dependencies
- `stat_name`, `category`, `description` all describe the stat itself (the key)
- They don't depend on each other

#### ✅ **UPDATE_METADATA Table - Fully 3NF Compliant**

**1NF/2NF/3NF Check:**
- ✅ Simple two-column table
- ✅ Primary key `id`, timestamp depends directly on it
- ✅ No possible violations

---

## Relationship Diagram

```
┌─────────────────────────────────────┐
│         TEAMS (32 records)          │
├─────────────────────────────────────┤
│ id (PK)          SERIAL              │  ← Primary Key (unique identifier)
│ name             TEXT                │
│ abbreviation     TEXT                │
│ wins             INTEGER             │
│ losses           INTEGER             │
│ ties             INTEGER             │
│ ppg              REAL                │  ← Points Per Game (calculated stat)
│ pa               REAL                │  ← Points Allowed (calculated stat)
│ games_played     INTEGER             │
│ stats            JSONB               │  ← Flexible storage for 100+ stats
│ last_updated     TIMESTAMP           │
└─────────────────────────────────────┘
            │
            │ (no formal FK, but logical relationship)
            │
            ▼
┌─────────────────────────────────────┐
│   STATS_METADATA (9 records)        │
├─────────────────────────────────────┤
│ stat_key (PK)    VARCHAR(100)       │  ← Primary Key
│ stat_name        VARCHAR(200)       │  ← Human-readable name
│ category         VARCHAR(50)        │  ← Grouping (offense/defense/record)
│ data_type        VARCHAR(20)        │  ← Type (integer/float/text)
│ description      TEXT                │  ← Full explanation
│ source           VARCHAR(100)       │  ← Data source (ESPN, TeamRankings)
│ last_updated     TIMESTAMP           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  UPDATE_METADATA (9 records)        │
├─────────────────────────────────────┤
│ id (PK)          SERIAL              │
│ last_update      TIMESTAMP           │  ← When refresh happened
└─────────────────────────────────────┘
```

**Note:** Currently there are **NO foreign key constraints** defined. This is acceptable but could be improved (see recommendations below).

---

## Key Design Decisions

### 1. **JSONB for Extensibility**
**Why:** Your system needs to support 100+ NFL statistics without constantly altering the database schema.

**Benefits:**
- ✅ Can add new stats without `ALTER TABLE` commands
- ✅ Fast queries with GIN indexes on JSONB
- ✅ Flexible structure for nested data (offense/defense/special teams)

**Example from your data:**
```json
{
  "offense": {
    "points_per_game": 34.8,
    "total_points": 174
  },
  "defense": {
    "points_allowed_per_game": 12.2,
    "total_points_allowed": 61
  },
  "record": {
    "wins": 5,
    "losses": 0,
    "games_played": 5
  }
}
```

### 2. **Hybrid Approach: Columns + JSONB**
**Why:** Keep frequently queried fields (wins, losses, ppg, pa) as regular columns for fast filtering/sorting.

**Benefits:**
- ✅ Fast queries: `SELECT * FROM teams WHERE wins > 3 ORDER BY ppg DESC`
- ✅ Standard SQL operations without JSONB syntax
- ✅ Additional stats in JSONB for flexibility

### 3. **No Foreign Keys Currently**
**Current State:** No FK constraints between tables

**Why this works:**
- `stats_metadata` is a reference table (documentation)
- `update_metadata` is a system table (logging)
- No data integrity issues because you control all inserts

---

## Potential Improvements (If Needed for Class)

### Option 1: Add Divisions/Conferences Tables (Full 3NF)

If your professor wants to see more normalized relationships, you could split divisions and conferences:

```sql
-- New table: CONFERENCES
CREATE TABLE conferences (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(10) NOT NULL,  -- 'AFC' or 'NFC'
    full_name       VARCHAR(50)            -- 'American Football Conference'
);

-- New table: DIVISIONS
CREATE TABLE divisions (
    id              SERIAL PRIMARY KEY,
    conference_id   INTEGER REFERENCES conferences(id),
    name            VARCHAR(20) NOT NULL,  -- 'AFC East', 'NFC North', etc.
    UNIQUE(conference_id, name)
);

-- Modified TEAMS table
ALTER TABLE teams ADD COLUMN division_id INTEGER REFERENCES divisions(id);
```

**Benefits:**
- ✅ Eliminates redundancy (division/conference names stored once)
- ✅ Demonstrates understanding of foreign keys
- ✅ Shows proper entity relationships

**Drawbacks:**
- ❌ Adds complexity for minimal gain (only 8 divisions, rarely change)
- ❌ Requires joins for simple queries

### Option 2: Add Games/Schedules Tables (Event Tracking)

For more advanced normalization:

```sql
CREATE TABLE games (
    id              SERIAL PRIMARY KEY,
    home_team_id    INTEGER REFERENCES teams(id),
    away_team_id    INTEGER REFERENCES teams(id),
    home_score      INTEGER,
    away_score      INTEGER,
    game_date       DATE,
    week            INTEGER,
    season          INTEGER
);
```

**Benefits:**
- ✅ Can calculate wins/losses from game results
- ✅ Historical data preserved
- ✅ Supports multiple seasons

---

## Summary: Is Your Database 3NF Compliant?

### ✅ **YES - Your current schema IS Third Normal Form compliant**

**Evidence:**

1. **First Normal Form (1NF):**
   - ✅ All columns contain atomic values
   - ✅ Each row is unique (primary keys defined)
   - ✅ No repeating groups

2. **Second Normal Form (2NF):**
   - ✅ All tables have single-column primary keys
   - ✅ No partial dependencies possible
   - ✅ All non-key columns depend on the entire primary key

3. **Third Normal Form (3NF):**
   - ✅ No transitive dependencies between regular columns
   - ✅ JSONB is treated as atomic (single complex value)
   - ✅ Each non-key column depends ONLY on the primary key

### Why JSONB Doesn't Violate 3NF

**Common Concern:** "Doesn't JSONB store calculated data?"

**Answer:** No, it doesn't violate 3NF because:
- JSONB is a **single attribute** (one column)
- The database treats it as an opaque value
- It's not creating dependencies **between table columns**
- It's a modern solution for semi-structured data

**Analogy:** It's like storing a document in a filing cabinet. The cabinet (table) is organized properly (3NF), and the document itself (JSONB) can have whatever structure makes sense.

---

## Conclusion & Recommendations

### For Your Class Discussion:

**Talking Points:**
1. ✅ "My database is in Third Normal Form because there are no transitive dependencies between table columns."
2. ✅ "I use JSONB for extensibility, which is a modern approach for semi-structured data without violating normalization principles."
3. ✅ "I could further normalize by creating Divisions and Conferences tables with foreign keys, but the current design is appropriate for this use case."

### What to Mention:

**Strengths:**
- Clean separation: `teams` (data), `stats_metadata` (documentation), `update_metadata` (logging)
- Hybrid approach balances query performance with flexibility
- No redundant data in regular columns
- Scalable to 100+ statistics without schema changes

**Trade-offs:**
- JSONB queries are slightly more complex (`stats->>'offense.ppg'`)
- No foreign keys means no enforced referential integrity
- Could add more tables (divisions, conferences) if needed for academic demonstration

### If Asked "Could You Improve This?"

**Answer:** "Yes, I could add foreign key relationships for conferences and divisions to demonstrate entity relationships, but the current design is already 3NF compliant and optimized for the application's needs."

---

## Quick Reference: Normalization Rules

### First Normal Form (1NF)
- ✅ Atomic values (no arrays, no comma-separated lists)
- ✅ Unique rows (primary key exists)
- ✅ No repeating groups

### Second Normal Form (2NF)
- ✅ Must be in 1NF
- ✅ No partial dependencies (every non-key column depends on THE WHOLE primary key)

### Third Normal Form (3NF)
- ✅ Must be in 2NF
- ✅ No transitive dependencies (non-key columns don't depend on other non-key columns)

### Example of 3NF Violation (You DON'T Have This):
```sql
-- BAD: Violates 3NF
CREATE TABLE teams_bad (
    id              SERIAL PRIMARY KEY,
    team_name       TEXT,
    division_id     INTEGER,
    division_name   TEXT,      -- ❌ Depends on division_id, not team_id!
    conference_name TEXT       -- ❌ Depends on division_id, not team_id!
);

-- GOOD: 3NF Compliant (What you should do IF adding divisions)
CREATE TABLE teams_good (
    id              SERIAL PRIMARY KEY,
    team_name       TEXT,
    division_id     INTEGER REFERENCES divisions(id)  -- FK to divisions table
);

CREATE TABLE divisions (
    id              SERIAL PRIMARY KEY,
    name            TEXT,
    conference_name TEXT
);
```

---

**Last Updated:** October 15, 2025  
**Database:** PostgreSQL 13+  
**Total Tables:** 3  
**Total Records:** 32 teams, 9 stats, 9 updates
