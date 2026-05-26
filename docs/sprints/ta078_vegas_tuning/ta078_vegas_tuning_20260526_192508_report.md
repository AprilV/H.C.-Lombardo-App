# TA-078 Vegas Gap Tuning Report

Generated (UTC): 2026-05-26T19:25:08.160935+00:00
Schema: hcl
Train seasons: 2021, 2022, 2023, 2024
Validation seasons: 2025

## Baseline vs Tuned (Validation)
- Baseline delta_pct: -8.03 (AI win% 45.54, Vegas win% 53.57)
- Bias correction delta_pct: -8.03 (bias=0.0001)
- Linear correction delta_pct: -8.03 (a=-0.0001, b=0.9999)
- Delta-optimized bias delta_pct: -16.07 (bias=2.3)

## Recommendation
- Recommended method: bias
- Recommended runtime env: AI_SPREAD_CAL_BIAS=0.0001, AI_SPREAD_CAL_SCALE=1.0

## Train Snapshot
- Baseline delta_pct: -15.36
- Best bias-scan delta_pct: -10.58

## Validation Weekly Breakdown
- Best week (bias): 2025-W06 delta 20.0 on 15 games
- Worst week (bias): 2025-W10 delta -57.14 on 14 games

## Validation Vegas-Spread Bin Breakdown
- abs_vegas_lt3: delta -26.32 (games 57, MAE 10.268)
- abs_vegas_3_to_7: delta 0.98 (games 103, MAE 9.6638)
- abs_vegas_7_to_10: delta -2.44 (games 41, MAE 12.6768)
- abs_vegas_ge10: delta -13.04 (games 23, MAE 9.7898)

## Validation Game-Level Delta
- Improved vs baseline: 0 games
- Regressed vs baseline: 0 games
- Flat vs baseline: 224 games
- Largest improvement: 2025_01_ARI_NO (2025-W01) err_improvement 0.0001
- Largest regression: 2025_01_CAR_JAX (2025-W01) err_improvement -0.0001

## Targeted Diagnostics
- Focus week requested: 2025-W10
- Focus week used: 2025-W10 (requested)
- Focus week improved/regressed/flat: 0 / 0 / 14
- Focus week avg err improvement: 0.0
- High-spread threshold (abs): 10.0
- High-spread improved/regressed/flat: 0 / 0 / 21
- High-spread avg err improvement: -0.0
- High-spread bin snapshot (abs_vegas_ge10): delta -13.04 on 23 games
- Focus week artifact: C:\ReactGitEC2\IS330\H.C Lombardo App\docs\sprints\ta078_vegas_tuning\ta078_vegas_tuning_20260526_192508_targeted_focus_week.csv
- High-spread artifact: C:\ReactGitEC2\IS330\H.C Lombardo App\docs\sprints\ta078_vegas_tuning\ta078_vegas_tuning_20260526_192508_targeted_high_spread.csv
