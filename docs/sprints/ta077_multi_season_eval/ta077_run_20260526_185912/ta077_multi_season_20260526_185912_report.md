# TA-077 Multi-Season Evaluation Report

Generated (UTC): 2026-05-26T18:59:17.360195+00:00
Schema: hcl
Cohort mode: pregame
Seasons: 2021, 2022, 2023, 2024, 2025

## Aggregate Summary
- Weighted winner accuracy: 38.93%
- Weighted spread accuracy: 50.67%
- Weighted total accuracy: 54.44%
- Average margin MAE: 14.064 points
- Average total MAE: 10.358 points
- AI vs Vegas (spread head-to-head): AI 199 wins, Vegas 184 wins, total 1309 games
- Gate pass count: 4 / 5

## Season Table
| Season | Winner% | Spread% | Total% | Margin MAE | Total MAE | AI vs Vegas (AI/VEG/TIE) | Leak% | Line-Lock% | Total Coverage% | Gates Pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 39.34 | 50.37 | 73.33 | 15.472 | 10.789 | 34/31/207 | 0.0 | 94.49 | 5.51 | True |
| 2022 | 34.69 | 54.79 | 52.63 | 12.807 | 10.395 | 43/32/196 | 0.0 | 92.99 | 7.01 | True |
| 2023 | 41.91 | 48.84 | 45.16 | 14.208 | 10.239 | 40/45/187 | 0.0 | 88.24 | 11.4 | True |
| 2024 | 38.24 | 47.01 | 71.43 | 14.081 | 9.73 | 43/47/182 | 0.0 | 94.85 | 5.15 | True |
| 2025 | 40.44 | 52.73 | 36.36 | 13.75 | 10.637 | 39/29/154 | 0.0 | 95.05 | 4.04 | False |

## Gate Thresholds
- Max leakage pct: 5.0
- Max line-lock pct: 95.0
- Min totals coverage pct: 5.0

## Notes
- AI vs Vegas values mirror the existing /api/ml/season-ai-vs-vegas comparison logic.
- Totals quality is highly sensitive to predicted_total independence from vegas_total.
- Gate failures indicate measurement integrity risks that should block completion claims.
