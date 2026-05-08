# Dashboard Release Notes

## Versioning

Format: `YYYY.MM.DD` (example: `2026.04.23`)

---

## 2026.05.07 (Draft / In Progress)

### Completed

1. Updated dashboard top-strip percent logic so `Sprint Tasks Done` uses effort-point percentage whenever sprint effort points are present, aligning with burndown/burnup/velocity units.
2. Added explicit unit subtitle under `Sprint Tasks Done` to remove stakeholder ambiguity between subtask and effort-point progress.
3. Added sprint-aware chart unit note in `Sprint Health` so chart interpretation stays explicit on every sprint selection.

### In Progress

1. `DSH-009` and `DSH-010` remain in progress.

### Notes

1. Sprint 14 now renders as `49%` with `21 of 52 subtasks complete` and `25 of 51 effort points complete`, with unit labels visible in both metrics and chart area.
2. This update is a dashboard clarity/governance refinement and does not change backlog ticket assignments.

### Evidence

1. `pmforge_dashboard/index.html`.
2. `docs/dashboard_product/DASHBOARD_RELEASE_NOTES.md`.

---

## 2026.05.01 (Draft / In Progress)

### Completed

1. Closed `DSH-012` Phase 2 gate with deterministic migration mapping, conflict rules, validation checks, and rollback strategy.
2. Added Phase 2 artifact: `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE2_MIGRATION_VALIDATION.md`.
3. Added baseline parity evidence file: `docs/dashboard_product/evidence/PHASE2_BASELINE_COUNTS_2026-05-01.txt`.
4. Closed `DSH-012` Phase 3 gate with backend persistence API implementation and startup route wiring verification.
5. Added Phase 3 artifact: `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE3_API_PERSISTENCE.md`.
6. Added Phase 3 API smoke evidence file: `docs/dashboard_product/evidence/PHASE3_API_SMOKE_2026-05-01.txt`.
7. Closed `DSH-012` Phase 4 gate with frontend persisted action wiring and rollback-safe handler updates.
8. Added Phase 4 artifact: `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE4_FRONTEND_PERSISTED_WIRING.md`.
9. Added Phase 4 frontend-flow smoke evidence file: `docs/dashboard_product/evidence/PHASE4_FRONTEND_PERSISTENCE_SMOKE_2026-05-01.txt`.
10. Started `DSH-012` Phase 5 implementation with top-strip metric sync to persisted aggregate endpoints (fallback-safe overlay).
11. Added Phase 5 artifact: `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE5_AUTOSYNC_METRICS_CHARTS.md`.
12. Added Phase 5 top-strip aggregate smoke evidence file: `docs/dashboard_product/evidence/PHASE5_TOP_STRIP_AGGREGATE_SMOKE_2026-04-30.txt`.
13. Completed Phase 5 blocker-list and RAG persisted sync subtask in dashboard overview rendering.
14. Added Phase 5 blocker/RAG sync smoke evidence file: `docs/dashboard_product/evidence/PHASE5_RAG_BLOCKER_SYNC_SMOKE_2026-04-30.txt`.
15. Completed Phase 5 persisted chart payload autosync subtask for burndown, burnup, velocity, and severity rendering overlays.
16. Added Phase 5 chart payload sync smoke evidence file: `docs/dashboard_product/evidence/PHASE5_CHART_PAYLOAD_SYNC_SMOKE_2026-04-30.txt`.
17. Completed Phase 5 cross-surface drift/mismatch check subtask for persisted top-strip and chart payload parity checks.
18. Added Phase 5 drift/mismatch smoke evidence file: `docs/dashboard_product/evidence/PHASE5_DRIFT_MISMATCH_CHECK_SMOKE_2026-04-30.txt`.
19. Marked `DSH-012` execution ticket as `DONE` after Phase 5 overall gate PASS closure.

### In Progress

1. `DSH-009` and `DSH-010` remain in progress; `DSH-012` is closed.

### Notes

1. Phase 0 gate decision: PASS.
2. Phase 1 gate decision: PASS.
3. Phase 2 gate decision: PASS.
4. Phase 3 gate decision: PASS.
5. Phase 4 gate decision: PASS.
6. Phase 5 subtask (top-strip aggregate sync) decision: PASS.
7. Phase 5 subtask (blocker-list and RAG persisted sync) decision: PASS.
8. Phase 5 subtask (chart payload persisted sync) decision: PASS.
9. Phase 5 subtask (cross-surface drift/mismatch checks) decision: PASS.
10. Phase 5 overall gate decision: PASS.
11. Next gate: none (Phase 5 complete).

### Evidence

1. `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE2_MIGRATION_VALIDATION.md`.
2. `docs/dashboard_product/evidence/PHASE2_BASELINE_COUNTS_2026-05-01.txt`.
3. `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE3_API_PERSISTENCE.md`.
4. `docs/dashboard_product/evidence/PHASE3_API_SMOKE_2026-05-01.txt`.
5. `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE4_FRONTEND_PERSISTED_WIRING.md`.
6. `docs/dashboard_product/evidence/PHASE4_FRONTEND_PERSISTENCE_SMOKE_2026-05-01.txt`.
7. `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE5_AUTOSYNC_METRICS_CHARTS.md`.
8. `docs/dashboard_product/evidence/PHASE5_TOP_STRIP_AGGREGATE_SMOKE_2026-04-30.txt`.
9. `docs/dashboard_product/evidence/PHASE5_RAG_BLOCKER_SYNC_SMOKE_2026-04-30.txt`.
10. `docs/dashboard_product/evidence/PHASE5_CHART_PAYLOAD_SYNC_SMOKE_2026-04-30.txt`.
11. `docs/dashboard_product/evidence/PHASE5_DRIFT_MISMATCH_CHECK_SMOKE_2026-04-30.txt`.

---

## 2026.04.30 (Draft / In Progress)

### Completed

1. Closed `DSH-012` Phase 0 gate with baseline contract and required traceability evidence.
2. Added Phase 1 coverage/model artifact: `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE1_COVERAGE_MODEL.md`.
3. Documented complete dashboard surface ownership matrix, canonical entities, enum mappings, and audit field requirements for migration planning.

### In Progress

1. `DSH-012` remains in execution for later gated phases after Phase 1 PASS.

### Notes

1. Phase 0 gate decision: PASS.
2. Phase 1 gate decision: PASS.
3. Next gate: Phase 2 deterministic migration plan (no implementation cutover yet).

### Evidence

1. Commit `40100148` - "dashboard: close Phase 0 gate for DSH-012".
2. `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE0_KICKOFF.md`.
3. `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE1_COVERAGE_MODEL.md`.

---

## 2026.04.27

### Completed

1. Switched GitHub Pages dashboard deployment source from legacy `Dashboard/index.html` to `pmforge_dashboard/index.html` via `.github/workflows/dashboard-pages-deploy.yml`.
2. Archived legacy dashboard file to `backups/legacy_dashboard/index.html` and moved legacy update guide to `backups/legacy_dashboard/DASHBOARD_UPDATE_GUIDE.md`.
3. Updated importer legacy mirror target to `backups/legacy_dashboard/index.html` in `scripts/suite/import_pmforge_suite.ps1`.
4. Aligned dashboard and suite documentation to PM4 source-of-truth paths and legacy archive behavior.

### Ticket Updates

1. `DSH-011` moved to `DONE`.

### Evidence

1. Commit `c2056abd` - "Switch dashboard deploy to PM4 and archive legacy dashboard".

---

## 2026.04.24 (Draft / In Progress)

### In Progress

1. Started `DSH-009`: configurable branding and methodology workspace controls in `pmforge_dashboard/index.html` (consumer copy in H.C.).
2. Added crash-safe local patch backup and session resume note for restart continuity.
3. Started `DSH-010`: suite architecture draft for auto-computed metrics, chart extensibility, methodology packs, and user-selectable dashboard layouts (moved to standalone PM Forge Suite repo).

### Added

1. Added suite architecture draft with target user strategy, canonical data model, API draft, chart registry model, and phased rollout (now maintained in standalone PM Forge Suite docs).

### Notes

1. Do not mark `DSH-009` as complete until acceptance criteria are verified and final UX copy is approved.
2. Do not mark `DSH-010` as complete until data contract, ERD, and migration sequencing are approved.

---

## 2026.04.23

### Added

1. Dashboard product documentation set under `docs/dashboard_product/`.
2. Dedicated `DSH-` ticket backlog for dashboard system work.
3. Charter, SOP, data ownership rules, and metrics baseline docs.

### Changed

1. Dashboard terminology updated to emphasize ticket workflow in nav labeling.
2. Dashboard update guides now require tracking dashboard work as `DSH-` tickets.

### Why

Shifted the dashboard from ad hoc support artifact to a managed product with traceability.

### Follow-up

1. Implement `DSH-001` ticket intake UI.
2. Implement `DSH-002` append-only activity log.
