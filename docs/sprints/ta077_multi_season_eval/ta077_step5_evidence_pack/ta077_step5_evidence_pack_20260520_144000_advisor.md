# TA-077 Advisor Evidence Pack (Step 05)

Generated (UTC): 2026-05-20T21:40:00.893594+00:00
Manifest: docs/sprints/ta077_multi_season_eval/ta077_step5_evidence_pack/ta077_step5_evidence_pack_20260520_144000_manifest.json
Machine summary: docs/sprints/ta077_multi_season_eval/ta077_step5_evidence_pack/ta077_step5_evidence_pack_20260520_144000_summary.json

## Executive Snapshot
- Winner accuracy: 38.93%
- Spread accuracy: 50.67%
- Total accuracy: 54.44%
- Margin MAE: 14.06
- Total MAE: 10.36
- AI vs Vegas: AI 193 vs Vegas 477 (ties 639)
- Guardrails overall: leakage FAIL at 98.82%; line-lock PASS at 93.05%; overall FAIL

## Recommendation
- Status: NO-GO
- Reason: TA-077 competitiveness claims are blocked by unresolved leakage integrity failure.
- Promotion conditions:
  - Leakage guardrail pass at overall and all-season level.
  - Line-lock guardrail pass at overall and all-season level.
  - Refreshed AI-vs-Vegas deltas recomputed on integrity-clean cohort.

## Run Manifest Notes
- Total artifacts hashed: 11
- Missing artifacts: 0
- Hashes/sizes/timestamps are in the manifest JSON.
