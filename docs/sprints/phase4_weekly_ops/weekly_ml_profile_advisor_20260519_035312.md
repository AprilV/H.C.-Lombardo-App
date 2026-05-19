# Phase 4 Gate Profile Advisor

Generated (UTC): 2026-05-19T03:53:12.803444+00:00
Target: season 2025, week 18
Target source: auto_latest
Recommendation: balanced
Reason: Highest-strictness passing profile selected

## Snapshot
- Completed games: 272
- XGBoost: 40.44% accuracy, MAE 13.75, coverage 100.0%
- Elo: 56.99% accuracy, MAE 10.411, coverage 100.0%
- AI vs Vegas delta: -28.57 across 224 games

## Profiles
- balanced: pass=True
- operational: pass=True
- strict-research: pass=False
  failed_checks: ai_vs_vegas_delta_floor, xgb_spread_mae_ceiling, xgb_winner_accuracy_floor
  failed_check_gaps: ai_vs_vegas_delta_floor(+18.570), xgb_spread_mae_ceiling(+0.250), xgb_winner_accuracy_floor(+1.560)
