# TA-077 Multi-Season Evaluation Report

Generated (UTC): 2026-05-18T17:26:26.278431+00:00
Schema: hcl
Seasons: 2021, 2022, 2023, 2024, 2025

## Aggregate Summary
- Weighted winner accuracy: 54.92%
- Weighted spread accuracy: 67.3%
- Weighted total accuracy: None%
- Average margin MAE: 11.891 points
- Average total MAE: 10.03 points
- AI vs Vegas (spread head-to-head): AI 111 wins, Vegas 65 wins, total 512 games
- Gate pass count: 0 / 5

## Season Table
| Season | Winner% | Spread% | Total% | Margin MAE | Total MAE | AI vs Vegas (AI/VEG/TIE) | Leak% | Line-Lock% | Total Coverage% | Gates Pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2021 | None | None | None | None | None | 0/0/0 | None | None | None | False |
| 2022 | None | None | None | None | None | 0/0/0 | None | None | None | False |
| 2023 | 56.64 | 66.67 | None | 11.698 | 10.338 | 59/31/166 | 100.0 | 100.0 | 0.0 | False |
| 2024 | 53.31 | 67.9 | None | 12.084 | 9.723 | 52/34/170 | 94.12 | 100.0 | 0.0 | False |
| 2025 | None | None | None | None | None | 0/0/0 | None | None | None | False |

## Gate Thresholds
- Max leakage pct: 5.0
- Max line-lock pct: 95.0
- Min totals coverage pct: 5.0

## Notes
- AI vs Vegas values mirror the existing /api/ml/season-ai-vs-vegas comparison logic.
- Totals quality is highly sensitive to predicted_total independence from vegas_total.
- Gate failures indicate measurement integrity risks that should block completion claims.
