# PREDICTION_TRACKING_SYSTEM.md
## ML Prediction Tracking — System Rules

STATUS: ACTIVE  
AUDIENCE: AI ASSISTANTS  
AUTHORITY: SUBORDINATE TO ARCHITECTURE.md

This document governs ML prediction lifecycle.

---

## 1. PREDICTION STORAGE

Each prediction MUST store:
- Game ID
- Predicted spread
- Timestamp
- Model identifier

Predictions are immutable after creation.

---

## 2. EVALUATION RULES

Post-game:
- Compare prediction vs closing spread
- Record win / loss / tie
- Persist results

No retroactive modification permitted.

---

## 3. AGGREGATION

Season statistics:
- AI wins
- Vegas wins
- Ties
- Percentages

Aggregation logic MUST be deterministic.

---

## 4. AI RESTRICTIONS

AI MUST NOT:
- Re-score historical predictions
- Delete or rewrite outcomes
- Alter evaluation rules mid-season

---

END OF PREDICTION TRACKING
