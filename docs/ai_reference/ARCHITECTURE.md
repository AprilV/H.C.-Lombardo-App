# ARCHITECTURE.md
## System Architecture — Authoritative Reference

STATUS: ACTIVE  
AUDIENCE: AI ASSISTANTS  
AUTHORITY: SUBORDINATE TO AI_EXECUTION_CONTRACT.md AND BEST_PRACTICES.md

This document defines **how the system is structured and how components interact**.
All architectural facts override assumptions and code comments.

---

## 1. SYSTEM OVERVIEW

This application is a **data-driven NFL analytics and prediction platform**.

Core responsibilities:
- Ingest NFL game data
- Track Vegas spreads
- Generate ML predictions
- Compare AI vs Vegas performance
- Persist historical results for analysis

All components are interconnected.

---

## 2. CORE COMPONENTS

### API Layer
- Exposes endpoints for predictions, stats, and analytics
- Reads from normalized database tables
- Must not contain business logic duplication

### Database Layer
Primary database: PostgreSQL

Key schemas:
- `hcl.games`
- `ml_predictions`
- Supporting lookup tables

Database is the **source of truth** for game state and outcomes.

---

## 3. DATA FLOW

1. External data sources (ESPN, Vegas lines)
2. Ingestion scripts populate database
3. ML prediction jobs read historical data
4. Predictions stored for comparison
5. API serves computed results

No component operates in isolation.

---

## 4. ML PREDICTION FLOW

- Predictions generated prior to kickoff
- Predictions stored with timestamps
- Results evaluated post-game
- Accuracy tracked season-wide

Predictions MUST reference:
- Locked closing spreads
- Final scores
- Known team identifiers

---

## 5. ENVIRONMENTS

Environments are separated.

- Local development
- Production (EC2)

AI MUST NOT assume environment configuration.
Always verify environment context before changes.

---

## 6. ARCHITECTURAL CONSTRAINTS

PROHIBITED:
- Business logic in multiple layers
- Hard-coded environment values
- Schema changes without migration
- Partial architectural fixes

If architecture is unclear:
→ STOP
→ ASK QUESTIONS

---

END OF ARCHITECTURE
