# Dashboard Data Ownership and Control Rules

Date: 2026-04-23

## Scope

Defines ownership and source-of-truth for dashboard operational data.

## Ownership

1. Product owner: April V. Sykes
2. AI implementer: updates by instruction, never policy override

## Data Domains

1. Sprint task completion state
- Source: `COMPLETED_TASKS`, `BLOCKED_TASKS` in `Dashboard/index.html`

2. Task resolution metadata
- Source: `TASK_DETAILS` in `Dashboard/index.html`
- Required fields for completed subtasks:
  - `resolution`
  - `date`
  - `timestamp`
  - `updatedBy`

3. Reporting inputs
- Source: `HOURS_DATA`, risks array, decisions array in `Dashboard/index.html`

4. Dashboard governance artifacts
- Source: files in `docs/dashboard_product/`

## Control Rules

1. No browser localStorage for persisted shared state.
2. Runtime memory edits are not official until committed to source.
3. Ticket status and release notes must be synchronized before close.
4. Direct edits to live `gh-pages` output are not allowed; deploy from source workflow.

## Auditability

1. Every dashboard release must include release notes entry.
2. Every closed dashboard ticket must reference completed change intent.
3. Commit history is the immutable evidence trail for published changes.
