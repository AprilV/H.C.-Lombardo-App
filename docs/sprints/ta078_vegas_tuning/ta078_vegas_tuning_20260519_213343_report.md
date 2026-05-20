# TA-078 Vegas Gap Tuning Report

Generated (UTC): 2026-05-19T21:33:43.568768+00:00
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
