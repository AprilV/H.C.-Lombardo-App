# TA-078 Vegas Gap Tuning Report

Generated (UTC): 2026-05-20T17:32:01.184122+00:00
Schema: hcl
Train seasons: 2021, 2022, 2023, 2024
Validation seasons: 2025

## Baseline vs Tuned (Validation)
- Baseline delta_pct: -28.57 (AI win% 35.27, Vegas win% 63.84)
- Bias correction delta_pct: -26.79 (bias=-3.1532)
- Linear correction delta_pct: -8.03 (a=-1.5093, b=-0.5048)
- Delta-optimized bias delta_pct: -27.68 (bias=-0.7)

## Recommendation
- Recommended method: linear
- Recommended runtime env: AI_SPREAD_CAL_BIAS=-1.5093, AI_SPREAD_CAL_SCALE=-0.5048

## Train Snapshot
- Baseline delta_pct: -33.22
- Best bias-scan delta_pct: -31.74

## Validation Weekly Breakdown
- Best week (linear): 2025-W06 delta 20.0 on 15 games
- Worst week (linear): 2025-W10 delta -57.14 on 14 games

## Validation Vegas-Spread Bin Breakdown
- abs_vegas_lt3: delta -26.32 (games 57, MAE 10.2681)
- abs_vegas_3_to_7: delta 0.98 (games 103, MAE 9.6638)
- abs_vegas_7_to_10: delta -2.44 (games 41, MAE 12.6769)
- abs_vegas_ge10: delta -13.04 (games 23, MAE 9.7897)

## Validation Game-Level Delta
- Improved vs baseline: 141 games
- Regressed vs baseline: 83 games
- Flat vs baseline: 0 games
- Largest improvement: 2025_08_TEN_IND (2025-W08) err_improvement 28.7529
- Largest regression: 2025_05_DAL_NYJ (2025-W05) err_improvement -15.7198
