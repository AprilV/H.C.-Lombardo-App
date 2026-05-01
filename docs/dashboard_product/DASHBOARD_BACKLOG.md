# Dashboard Backlog

Date opened: 2026-04-23
Prefix: `DSH-`

## Workflow

Status values:
- `TODO`
- `IN PROGRESS`
- `BLOCKED`
- `DONE`

Priority values:
- `P1` critical
- `P2` high
- `P3` medium

## Tickets

| ID | Priority | Status | Type | Summary | Acceptance Criteria |
|---|---|---|---|---|---|
| DSH-001 | P1 | TODO | Feature | Add dashboard ticket intake panel (parent ticket + subtasks) | Can create TA-style parent ticket and N subtasks from UI inputs without editing code first |
| DSH-002 | P1 | TODO | Feature | Add append-only dashboard activity log | Every ticket field change appends immutable event row with actor and timestamp |
| DSH-003 | P2 | TODO | UX | Rename sprint language to ticket operations where applicable | Navigation and section labels match ticketing workflow terminology |
| DSH-004 | P2 | TODO | Docs | Publish dashboard release note process | Each dashboard change is traceable to release note entries |
| DSH-005 | P2 | TODO | Metrics | Add lead-time and blocked-time KPI views | Dashboard can show lead time and blocked durations by sprint |
| DSH-006 | P3 | TODO | Refactor | Reduce single-file risk by extracting data blocks | Static data sections can be maintained in separated files with build/import step |
| DSH-007 | P3 | TODO | Quality | Add dashboard smoke test checklist | Standard verification list exists and is run before push |
| DSH-008 | P1 | TODO | Security | Enforce branch protection and deploy guardrails | `master` requires PR + review + checks, `gh-pages` is automation-only push path, and branch protection settings are documented in the repo |
| DSH-009 | P2 | IN PROGRESS | Feature | Add configurable dashboard branding + methodology workspace controls | Header/about/report/export text can be edited from in-page controls, methodology label/status updates consistently, and default H.C. Lombardo context remains available without data loss |
| DSH-010 | P1 | IN PROGRESS | Architecture | Define suite-scale auto-computed metrics and extensible chart/layout architecture | Architecture draft defines target users, canonical data model, event-driven auto-update flow, chart registry, user-selectable layouts, methodology packs (Agile/Hybrid/Predictive), and rollout phases |
| DSH-011 | P2 | DONE | Docs | Align PM4 source-of-truth docs after dashboard transition | Dashboard docs reference `pmforge_dashboard/index.html` as active source, legacy path references point to `backups/legacy_dashboard/index.html`, and release notes capture transition evidence (`c2056abd`) |
| DSH-012 | P1 | DONE | Execution | Start dashboard automation implementation with phase-gated delivery and evidence checkpoints | Phase 0 through Phase 5 gates are PASS with evidence artifacts recorded; persisted backend/frontend wiring, metric autosync, and cross-surface drift/mismatch checks are complete and release/index traceability is updated |

## Notes

- Ticket IDs are permanent and never recycled.
- Update this file first when new dashboard work is proposed.
- Cross-reference commit hashes in release notes when tickets move to `DONE`.
