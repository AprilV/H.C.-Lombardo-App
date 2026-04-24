# Dashboard Operating SOP

Date: 2026-04-23

## Objective

Run the PM dashboard with repeatable operating discipline.

## Rule Set

1. No localStorage for shared source-of-truth updates.
2. All dashboard enhancement work must be ticketed as `DSH-`.
3. Every completed sprint subtask requires resolution metadata.

## Standard Flow

1. Intake
- Create or update a `DSH-` ticket in `DASHBOARD_BACKLOG.md`.
- Define acceptance criteria before code changes.

2. Implementation
- Update `Dashboard/index.html` and relevant docs.
- Keep changes scoped to one intent per commit when possible.

3. Verification
- Confirm key dashboard tabs load and nav is functional.
- Confirm updated task metadata appears in modal/UI.
- Confirm no localStorage dependency was introduced.

4. Evidence
- Add an entry to `DASHBOARD_RELEASE_NOTES.md`.
- Record ticket status transitions in `DASHBOARD_BACKLOG.md`.

5. Publish
- Deploy `Dashboard/index.html` to `gh-pages` mirror workflow.
- Validate live page after deployment.

## Definition of Done for Dashboard Tickets

1. Acceptance criteria met.
2. Documentation updated.
3. Release notes updated.
4. Verification completed.
5. Ticket status moved to `DONE`.
