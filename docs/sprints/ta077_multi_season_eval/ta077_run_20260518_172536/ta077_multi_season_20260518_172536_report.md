# TA-077 Multi-Season Evaluation Report

Generated (UTC): 2026-05-18T17:25:38.295083+00:00
Schema: hcl
Seasons: 2024

## Aggregate Summary
- Weighted winner accuracy: 53.31%
- Weighted spread accuracy: 67.9%
- Weighted total accuracy: None%
- Average margin MAE: 12.084 points
- Average total MAE: 9.723 points
- AI vs Vegas (spread head-to-head): AI 52 wins, Vegas 34 wins, total 256 games
- Gate pass count: 0 / 1

## Season Table
| Season | Winner% | Spread% | Total% | Margin MAE | Total MAE | AI vs Vegas (AI/VEG/TIE) | Leak% | Line-Lock% | Total Coverage% | Gates Pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2024 | 53.31 | 67.9 | None | 12.084 | 9.723 | 52/34/170 | 94.12 | 100.0 | 0.0 | False |

## Gate Thresholds
- Max leakage pct: 5.0
- Max line-lock pct: 95.0
- Min totals coverage pct: 5.0

## Notes
- AI vs Vegas values mirror the existing /api/ml/season-ai-vs-vegas comparison logic.
- Totals quality is highly sensitive to predicted_total independence from vegas_total.
- Gate failures indicate measurement integrity risks that should block completion claims.
