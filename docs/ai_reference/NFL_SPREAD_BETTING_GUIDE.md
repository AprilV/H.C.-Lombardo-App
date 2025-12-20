# NFL_SPREAD_BETTING_GUIDE.md
## Spread Betting Logic — Authoritative Rules

STATUS: ACTIVE  
AUDIENCE: AI ASSISTANTS  
AUTHORITY: SUBORDINATE TO ARCHITECTURE.md

This document defines betting logic interpretation.

---

## 1. SPREAD SIGN CONVENTIONS

- Negative spread = favorite
- Positive spread = underdog

AI MUST NOT invert or reinterpret spreads.

---

## 2. COVERAGE RULES

A team covers if:
- Favorite: wins by more than the spread
- Underdog: loses by less than the spread or wins outright

Ties against spread are recorded explicitly.

---

## 3. DISPLAY RULES

Frontend and reporting MUST:
- Use consistent sign conventions
- Clearly indicate favorites and underdogs
- Never re-normalize spreads arbitrarily

---

## 4. FAILURE CONDITIONS

PROHIBITED:
- Mixing sign logic
- Recalculating spreads
- Inferring betting outcomes without final scores

---

END OF SPREAD GUIDE
