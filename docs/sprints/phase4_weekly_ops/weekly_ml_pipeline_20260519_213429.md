# Phase 4 Weekly ML Pipeline Report

Generated (UTC): 2026-05-19T21:34:29.957106+00:00
Target: season 2025, week 18
Target source: explicit

## Operations
- XGBoost generated: 0
- XGBoost inserted: 0
- Elo generated: 0
- Elo inserted: 0
- XGBoost rows scored this run: 0
- Elo rows scored this run: 0

## Season Snapshot
- Completed games: 272
- XGBoost: 110/272 (40.44%), MAE 13.75, coverage 100.0%
- Elo: 155/272 (56.99%), MAE 10.411, coverage 100.0%
- AI vs Vegas: AI 79 wins, Vegas 143 wins, ties 2, delta -28.57 pts

## Gates
- Profile: operational
- Evaluated: True
- Overall pass: True
- XGBoost winner accuracy floor: actual 40.44 vs threshold 40.0 (pass=True)
- XGBoost spread MAE ceiling: actual 13.75 vs threshold 14.0 (pass=True)
- XGBoost coverage minimum: actual 100.0 vs threshold 95.0 (pass=True)
- Elo winner accuracy floor: actual 56.99 vs threshold 50.0 (pass=True)
- Elo spread MAE ceiling: actual 10.411 vs threshold 14.0 (pass=True)
- Elo coverage minimum: actual 100.0 vs threshold 95.0 (pass=True)
- AI vs Vegas delta floor: actual -28.57 across 224 games vs threshold -30.0 (pass=True)

## TA-078 Tuning
- Executed: True
- Success: True
- Exit code: 0
- Recommended method: linear
- Recommended runtime env: AI_SPREAD_CAL_BIAS=-1.5093, AI_SPREAD_CAL_SCALE=-0.5048
- Summary artifact: C:\ReactGitEC2\IS330\H.C Lombardo App\docs\sprints\ta078_vegas_tuning\ta078_vegas_tuning_20260519_213429_summary.json
