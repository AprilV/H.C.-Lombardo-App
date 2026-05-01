# Dashboard Release Notes

## Versioning

Format: `YYYY.MM.DD` (example: `2026.04.23`)

---

## 2026.04.30 (Draft / In Progress)

### In Progress

1. Started `DSH-012`: dashboard automation implementation kickoff with Phase 0 baseline freeze.
2. Added phase kickoff and handoff runbook doc: `docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE0_KICKOFF.md`.
3. Added explicit next-chat execution template so implementation can continue in a separate chat without ambiguity.

### Notes

1. Phase 1 is gated and must not begin until Phase 0 done criteria are verified.

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
