# TA-077 Multi-Season Evaluation Report

Generated (UTC): 2026-05-26T19:10:09.518954+00:00
Schema: hcl
Cohort mode: pregame
Seasons: 2021, 2022, 2023, 2024, 2025

## Aggregate Summary
- Weighted winner accuracy: 38.93%
- Weighted spread accuracy: 50.67%
- Weighted total accuracy: 52.02%
- Average margin MAE: 14.064 points
- Average total MAE: 11.405 points
- AI vs Vegas (spread head-to-head): AI 199 wins, Vegas 184 wins, total 1309 games
- Gate pass count: 5 / 5

## Season Table
| Season | Winner% | Spread% | Total% | Margin MAE | Total MAE | AI vs Vegas (AI/VEG/TIE) | Leak% | Line-Lock% | Total Coverage% | Gates Pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | 39.34 | 50.37 | 53.23 | 15.472 | 11.926 | 34/31/207 | 0.0 | 2.21 | 96.69 | True |
| 2022 | 34.69 | 54.79 | 54.86 | 12.807 | 10.989 | 43/32/196 | 0.0 | 4.43 | 94.83 | True |
| 2023 | 41.91 | 48.84 | 53.05 | 14.208 | 10.728 | 40/45/187 | 0.0 | 2.94 | 96.32 | True |
| 2024 | 38.24 | 47.01 | 47.89 | 14.081 | 11.044 | 43/47/182 | 0.0 | 2.94 | 95.96 | True |
| 2025 | 40.44 | 52.73 | 50.9 | 13.75 | 12.336 | 39/29/154 | 0.0 | 0.0 | 81.62 | True |

## Gate Thresholds
- Max leakage pct: 5.0
- Max line-lock pct: 95.0
- Min totals coverage pct: 5.0

## Notes
- AI vs Vegas values mirror the existing /api/ml/season-ai-vs-vegas comparison logic.
- Totals quality is highly sensitive to predicted_total independence from vegas_total.
- Gate failures indicate measurement integrity risks that should block completion claims.
