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

## Notes

- Ticket IDs are permanent and never recycled.
- Update this file first when new dashboard work is proposed.
- Cross-reference commit hashes in release notes when tickets move to `DONE`.
