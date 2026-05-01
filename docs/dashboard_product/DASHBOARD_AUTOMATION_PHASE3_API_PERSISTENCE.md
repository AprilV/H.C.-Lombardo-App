# Dashboard Automation Phase 3 - Backend API Persistence and Runtime Wiring

Date: 2026-05-01
Status: PASS
Ticket: DSH-012

## Scope Boundary

1. In scope: Teacher-facing dashboard backend persistence and API route operations in this repository only.
2. Out of scope: Frontend migration cutover and external PM Forge Suite repositories.

## Entry Criteria Check

1. Phase 0 baseline contract exists and gate decision is PASS: PASS.
2. Phase 1 coverage/canonical model exists and gate decision is PASS: PASS.
3. Phase 2 migration/validation plan exists and gate decision is PASS: PASS.

## Phase 3 Checklist (Completed)

1. Resolve runtime route wiring so startup path consistently exposes dashboard API routes.
2. Implement persisted storage for canonical dashboard entities.
3. Implement mutation and read endpoints for ticket workflow data.
4. Implement append-only activity event logging for dashboard mutations.
5. Implement aggregate endpoints for overall and sprint-scoped rollups.
6. Execute API smoke verification and capture evidence.

## Implementation Summary

1. Added runtime module `dashboard_api.py` at repository root to satisfy `api_server.py` import contract (`from dashboard_api import register_dashboard_routes`).
2. Added `register_dashboard_routes(app)` implementation that:
   - ensures required tables exist (`CREATE TABLE IF NOT EXISTS`), then
   - registers blueprint `/api/dashboard/v1`.
3. Added persistence tables:
   - `dashboard_tickets`
   - `dashboard_subtasks`
   - `dashboard_task_details`
   - `dashboard_blockers`
   - `dashboard_retro_notes`
   - `dashboard_dod_criteria`
   - `dashboard_hours_entries`
   - `dashboard_risk_entries`
   - `dashboard_decision_entries`
   - `dashboard_activity_events`
4. Added normalization and audit handling:
   - canonical status mapping (`todo`, `in_progress`, `blocked`, `done`)
   - priority/effort/source/sprint normalization
   - `updated_by`, `source`, and timestamp persistence on writes
5. Added append-only activity event writes for create/update/delete operations.

## Endpoint Surface Delivered

1. Health
   - `GET /api/dashboard/v1/health`
2. Tickets
   - `GET /api/dashboard/v1/tickets`
   - `GET /api/dashboard/v1/tickets/<ticket_id>`
   - `POST /api/dashboard/v1/tickets`
   - `PUT /api/dashboard/v1/tickets/<ticket_id>`
   - `DELETE /api/dashboard/v1/tickets/<ticket_id>`
3. Subtasks + Task Detail
   - `GET /api/dashboard/v1/subtasks`
   - `POST /api/dashboard/v1/subtasks`
   - `PUT /api/dashboard/v1/subtasks/<subtask_id>/status`
   - `DELETE /api/dashboard/v1/subtasks/<subtask_id>`
   - `GET /api/dashboard/v1/task-details/<subtask_id>`
   - `PUT /api/dashboard/v1/task-details/<subtask_id>`
4. Blockers
   - `GET /api/dashboard/v1/blockers`
   - `POST /api/dashboard/v1/blockers`
   - `PUT /api/dashboard/v1/blockers/<blocker_id>`
   - `DELETE /api/dashboard/v1/blockers/<blocker_id>`
5. Retro
   - `GET /api/dashboard/v1/retro/<sprint_code>`
   - `PUT /api/dashboard/v1/retro/<sprint_code>`
   - `DELETE /api/dashboard/v1/retro/<sprint_code>`
6. DoD
   - `GET /api/dashboard/v1/dod`
   - `POST /api/dashboard/v1/dod`
   - `PUT /api/dashboard/v1/dod/<criterion_id>`
   - `DELETE /api/dashboard/v1/dod/<criterion_id>`
7. Hours
   - `GET /api/dashboard/v1/hours`
   - `PUT /api/dashboard/v1/hours/<week_num>`
   - `DELETE /api/dashboard/v1/hours/<week_num>`
8. Risks
   - `GET /api/dashboard/v1/risks`
   - `POST /api/dashboard/v1/risks`
   - `PUT /api/dashboard/v1/risks/<risk_id>`
   - `DELETE /api/dashboard/v1/risks/<risk_id>`
9. Decisions
   - `GET /api/dashboard/v1/decisions`
   - `POST /api/dashboard/v1/decisions`
   - `PUT /api/dashboard/v1/decisions/<decision_id>`
   - `DELETE /api/dashboard/v1/decisions/<decision_id>`
10. Activity Events + Aggregates
    - `GET /api/dashboard/v1/events`
    - `GET /api/dashboard/v1/aggregates/overview`
    - `GET /api/dashboard/v1/aggregates/sprint/<sprint_code>`

## Verification Results

1. Read-surface smoke checks returned HTTP 200 for health, collection, events, and aggregate endpoints.
2. End-to-end mutation smoke checks returned expected success statuses:
   - create endpoints: HTTP 201
   - update/upsert endpoints: HTTP 200
   - delete endpoints: HTTP 200
3. Aggregates and events endpoints returned HTTP 200 after mutations.
4. Cleanup delete sequence completed successfully for generated smoke entities.

## Phase 3 Evidence Paths

1. API smoke output log:
   - `docs/dashboard_product/evidence/PHASE3_API_SMOKE_2026-05-01.txt`
2. Runtime module and route implementation:
   - `dashboard_api.py`
3. Startup route wiring contract (import + register):
   - `api_server.py`

## Gate Decision

Current: PASS
Reason: Runtime dashboard API wiring now resolves in startup path, persisted canonical entities are implemented, required mutation/read surfaces and aggregate endpoints are operational, and smoke evidence confirms successful endpoint execution.
