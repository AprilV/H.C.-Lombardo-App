# LIVE_SCORE_SETUP.md
## Live Score System — AI Operational Reference

STATUS: ACTIVE  
AUDIENCE: AI ASSISTANTS  
AUTHORITY: SUBORDINATE TO ARCHITECTURE.md

This document defines how live scores and closing spreads are handled.

---

## 1. PURPOSE

This system:
- Saves live NFL scores
- Locks Vegas spreads prior to kickoff
- Ensures historical integrity

---

## 2. DATA HANDLING RULES

- `spread_line` may change before kickoff
- `closing_spread` is locked exactly once
- Once locked, `closing_spread` NEVER changes

Closing spreads are authoritative for analysis.

---

## 3. LOCKING LOGIC

Trigger:
- 1 hour before kickoff

Action:
- Copy `spread_line` → `closing_spread`
- Prevent future updates

Failure to lock spreads is a SYSTEM ERROR.

---

## 4. SCORE UPDATES

- Scores update every 5–10 minutes
- Only during active games
- Final scores remain immutable post-game

---

## 5. AI USAGE REQUIREMENTS

AI MUST:
- Use `closing_spread` when available
- Fall back to `spread_line` only if not locked
- Never recompute or overwrite locked data

---

END OF LIVE SCORE SETUP
