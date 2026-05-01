# Dashboard Automation Phase 2 - Deterministic Migration Plan and Validation

Date: 2026-05-01
Status: PASS
Ticket: DSH-012

## Scope Boundary

1. In scope: Teacher-facing dashboard data migration planning for this repository only.
2. Out of scope: External PM Forge Suite repositories and feature implementation cutover.

## Entry Criteria Check

1. Phase 1 coverage matrix and canonical model exist and are committed: PASS.
2. Phase 1 gate decision is PASS: PASS.

## Phase 2 Checklist (Completed)

1. Create field mapping for legacy arrays/objects to canonical entities.
2. Define deterministic import order and conflict rules.
3. Define migration validation checks with parity metrics.
4. Define rollback strategy for failed migration runs.

## Legacy Source Inventory (Baseline Cardinalities)

Baseline source was extracted from `pmforge_dashboard/index.html` using deterministic parsing of active (last) runtime blocks.

| Legacy source | Count | Notes |
|---|---:|---|
| `COMPLETED_TASKS` | 131 | Subtasks marked done |
| `BLOCKED_TASKS` | 2 | Subtasks marked blocked |
| Unique status-task ids (`completed U blocked`) | 133 | Overlap count is 0 |
| `TASK_DETAILS` object entries | 133 | Matches unique status-task ids |
| `PB_ITEMS` rows | 72 | Ticket-level records |
| `HOURS_DATA` rows | 10 | Weekly entries |
| Retro content blocks (`retro-content-*`) | 5 | Sprint retros |
| DoD lists (`data-dod-list`) | 5 | Sprint DoD sets |

## Legacy to Canonical Mapping

| Legacy structure | Canonical target | Key mapping |
|---|---|---|
| `PB_ITEMS[]` | `Ticket` | `id -> ticket_id`, `feature -> title`, `description -> description`, `cat -> category`, `pri -> priority`, `effort -> effort`, `status -> status`, `assignee -> assignee`, `sprint -> sprint_code`, `dueDate -> due_date`, `createdAt -> created_at`, `updatedAt -> updated_at`, `updatedBy -> updated_by` |
| `COMPLETED_TASKS[]` + `BLOCKED_TASKS[]` | `Subtask` status | `task_id -> subtask_id`, derive `status` using precedence rules |
| Sprint board/task DOM labels | `Subtask` | `task_id -> subtask_id`, derived `ticket_id`, `title`, `source_type=board`, `sequence` |
| Ticket `manualSubtasks[]` | `Subtask` | `id -> subtask_id`, parent `ticket_id`, `title`, `source_type=manual`, `sequence` |
| `TASK_DETAILS{}` | `TaskDetail` | object key -> `subtask_id`; fields map to `resolution`, `date`, `timestamp`, `updated_by` |
| `HOURS_DATA[]` | `HoursEntry` | `num -> week_num`, `dates -> date_range_label`, `sprint -> sprint_code`, `hours -> hours`, `notes -> notes` |
| Retro cards/inputs by sprint | `RetroNote` | sprint scoped `went_well`, `did_not_go_well`, `improvements` |
| DoD lists by sprint | `DodCriterion` | sprint scoped criterion text list with deterministic sequence |
| Risk register rows | `RiskEntry` | `id`, `risk`, `like`, `impact`, `mitigation`, `sprint`, `status` |
| Decision log rows | `DecisionEntry` | `id`, `date`, `sprint`, `title`, `chosen`, `considered`, `why` |
| ticket `history[]` and comment events | `ActivityEvent` | append-only event stream preserving actor/time/message |

## Deterministic Import Order

1. Load `Sprint` reference records from `SPRINT_SCHEDULE`.
2. Import all `Ticket` rows from `PB_ITEMS`.
3. Build full `Subtask` set from board tasks plus manual subtasks.
4. Apply status from `COMPLETED_TASKS`/`BLOCKED_TASKS` using precedence.
5. Import `TaskDetail` rows from `TASK_DETAILS`.
6. Import `HoursEntry` rows from `HOURS_DATA`.
7. Import sprint-scoped `RetroNote` and `DodCriterion` rows.
8. Import `RiskEntry` and `DecisionEntry` rows.
9. Import `ActivityEvent` from ticket history/comments.
10. Compute and persist `SprintMetricsSnapshot` derived aggregates.

## Deterministic Conflict Rules

1. Subtask status precedence: `blocked` > `done` > `todo`.
2. Ticket status derivation (if recomputed): all subtasks done -> `done`; any blocked -> `blocked`; any progress -> `in_progress`; else `todo`.
3. Duplicate subtask ids: keep first canonical row, append conflict event to `ActivityEvent`, and do not mutate source order.
4. Missing `TaskDetail` for a status-tracked subtask: create row with null detail fields and `source=migration`.
5. `TaskDetail` exists for unknown subtask id: create placeholder subtask under inferred ticket (or `TBD`) and flag with `source=migration` event.
6. Missing sprint codes resolve to `TBD` (not dropped).
7. Missing assignee resolves to `Unassigned`.

## Idempotency and Re-run Rules

1. Upsert keys:
   - `Ticket.ticket_id`
   - `Subtask.subtask_id`
   - `TaskDetail.subtask_id`
   - `HoursEntry.week_num`
   - `RiskEntry.id`
   - `DecisionEntry.id`
2. Migration is re-runnable with stable ordering by source sequence.
3. Re-runs update mutable fields but must not duplicate append-only `ActivityEvent` rows for identical migration event signatures.

## Validation and Parity Checks

1. Extraction determinism check:
   - run1 and run2 cardinality snapshots are byte-identical: PASS.
2. Status-task parity check:
   - unique status-task ids = 133
   - task detail rows = 133
   - parity result: PASS.
3. Baseline presence checks:
   - ticket rows > 0, hours rows > 0, retro blocks > 0, DoD lists > 0: PASS.
4. Required migration output checks (must pass during execution phase):
   - target row counts match baseline-derived expected counts.
   - no null primary keys in canonical entities.
   - enum normalization has zero invalid values.

## Rollback Strategy

1. Run migration in a single transaction boundary per migration batch.
2. Write pre-migration export snapshot (`tickets`, `subtasks`, `task_details`, `hours`, `retro`, `dod`) before first write.
3. On validation failure:
   - rollback transaction;
   - persist failure log with failed check ids;
   - keep pre-migration snapshot for replay.
4. Recovery path:
   - fix mapper/rule issue;
   - re-run full deterministic import from unchanged source snapshot;
   - verify parity report before enabling downstream phases.

## Phase 2 Evidence Paths

1. Migration plan and rules:
   - docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE2_MIGRATION_VALIDATION.md
2. Baseline parity metrics:
   - docs/dashboard_product/evidence/PHASE2_BASELINE_COUNTS_2026-05-01.txt
3. Upstream gate artifacts:
   - docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE0_KICKOFF.md
   - docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE1_COVERAGE_MODEL.md

## Gate Decision

Current: PASS
Reason: Phase 2 required mapping, deterministic sequencing, conflict handling, validation design, and rollback strategy are complete with reproducible baseline evidence.
