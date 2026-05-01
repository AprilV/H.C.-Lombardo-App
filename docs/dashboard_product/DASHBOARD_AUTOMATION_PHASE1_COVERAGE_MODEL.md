# Dashboard Automation Phase 1 - Coverage Matrix and Canonical Data Model

Date: 2026-04-30
Status: PASS
Ticket: DSH-012

## Scope Boundary

1. In scope: Teacher-facing dashboard automation surfaces in this repository.
2. Out of scope: External PM Forge Suite source repos and non-dashboard app feature work.

## Entry Criteria Check

1. Phase 0 baseline contract exists and is committed.
2. Phase 0 gate decision is PASS.
3. Non-regression UI rules are established in Phase 0 artifact.

## Phase 1 Checklist (Completed)

1. Build complete feature matrix for all tabs, subviews, and modal/editor flows.
2. Define canonical entities and relationships.
3. Define required enums/status mappings and audit fields.
4. Define source-of-truth rule for operational data.

## Coverage Matrix (Feature Surface Ownership)

| Surface | Current Behavior Source | Primary Runtime Path | Canonical Entity Ownership |
|---|---|---|---|
| Overview tab (`tab-overview`) | `SPRINT_ARCHIVE`, `PB_ITEMS`, board checkboxes | `loadSprintDashboard`, `syncDashMetrics`, `computeLiveTaskCounts` | `Sprint`, `Ticket`, `Subtask`, `Blocker`, `SprintMetricsSnapshot` |
| Architecture tab (`tab-architecture`) | static content + Three.js scene | `init3DArchitecture`, `createArchitecture` | `ReferenceContent` (non-operational static) |
| Sprints workspace (`tab-sprints`) | board DOM + `COMPLETED_TASKS`, `BLOCKED_TASKS`, `TASK_DETAILS` | `showSprintPageView`, `syncTaskStatesFromData` | `Sprint`, `Ticket`, `Subtask`, `TaskDetail` |
| Sprint Board (`spage-board`) | board DOM groups + task checkbox ids | `wireTaskBoard`, `wireParentTaskGroups`, `toggleTask` | `Subtask`, `TaskDetail`, `ActivityEvent` |
| Retrospective (`spage-retro`) | sprint-specific retro card DOM | `applyRetroEditorChanges`, `autofillRetroFromTickets` | `RetroNote`, `Sprint` |
| Definition of Done (`spage-dod`) | sprint-specific DoD list DOM | `applyDodEditorChanges`, `autofillDodFromTickets` | `DodCriterion`, `Sprint` |
| Product Backlog Tracker (`tab-backlog`) | `PB_ITEMS` + tracker filters/sort | `renderTaskTracker`, `submitCreateTicket`, `saveTicketEdits` | `Ticket`, `Subtask`, `ActivityEvent` |
| Ticket Create modal | in-memory modal fields | `openCreateTicketModal`, `submitCreateTicket` | `Ticket`, `Subtask`, `ActivityEvent` |
| Ticket Editor modal | in-memory edit/comment/history | `openTicketEditor`, `saveTicketEdits`, `addTicketComment`, `assignTicketOwner` | `Ticket`, `ActivityEvent` |
| Task Resolution modal | `TASK_DETAILS` + subtask state arrays | `openTaskModal`, `applyTaskResolutionUpdate`, `copyTaskResolutionSnippet` | `TaskDetail`, `Subtask`, `ActivityEvent` |
| Hours Log (`tab-hours`) | `HOURS_DATA` array | `buildHoursLog` IIFE + derived totals | `HoursEntry` |
| Weekly Report (`tab-report`) | generated from hours + sprint/task state | `buildReportData`, `renderReport`, `buildSprintSummaryText` | `ReportView` derived from `HoursEntry`, `Subtask`, `Ticket` |
| Risk Register (`tab-risk`) | in-script `risks` array | `buildRiskRegister` IIFE | `RiskEntry` |
| Decision Log (`tab-decisions`) | in-script `decisions` array | `buildDecisionLog` IIFE | `DecisionEntry` |
| AI Project Logbook (`tab-ailog`) | static embedded logbook HTML | static content render | `ReferenceContent` (append-only archival source) |
| Branding and methodology controls | browser storage + form fields | `getBrandingSnapshot`, `readBrandingStorage`, `writeBrandingStorage`, `applyBrandingToUI` | `WorkspaceConfig` |
| Sprint selector persistence | browser storage | `readPersistedDashSprint`, `persistDashSprintSelection`, `watchSprintDateRollover` | `WorkspaceConfig`, `Sprint` |

## Canonical Entity Model

### 1) Sprint

- Purpose: Time-box boundary and aggregate context.
- Core fields:
  - `id` (integer)
  - `code` (string, example: `S13`)
  - `name` (string)
  - `start_date` (date)
  - `end_date` (date)
  - `state` (enum)

### 2) Ticket

- Purpose: Parent work item for backlog and sprint execution.
- Core fields:
  - `id` (string, example: `TA-059` or `TK-001`)
  - `title` (string)
  - `description` (text)
  - `category` (enum/string)
  - `priority` (enum)
  - `effort` (enum)
  - `status` (enum)
  - `assignee` (string)
  - `sprint_code` (string or `TBD`)
  - `due_date` (date nullable)

### 3) Subtask

- Purpose: Executable unit tied to a ticket and sprint board.
- Core fields:
  - `id` (string)
  - `ticket_id` (string)
  - `title` (string)
  - `status` (enum)
  - `source_type` (enum: board/manual)
  - `sequence` (integer)

### 4) TaskDetail

- Purpose: Resolution metadata for completed/blocked subtasks.
- Core fields:
  - `subtask_id` (string)
  - `resolution` (text)
  - `date` (date)
  - `timestamp` (datetime)
  - `updated_by` (string)
  - `status_override` (enum nullable)

### 5) Blocker

- Purpose: Explicit blocker records for count, severity, and narrative consistency.
- Core fields:
  - `id` (string)
  - `ticket_id` (string nullable)
  - `summary` (text)
  - `severity` (enum)
  - `status` (enum)
  - `sprint_code` (string)

### 6) HoursEntry

- Purpose: Weekly work evidence and report input.
- Core fields:
  - `week_num` (integer)
  - `date_range_label` (string)
  - `sprint_code` (string)
  - `hours` (numeric)
  - `notes` (text)

### 7) RiskEntry

- Purpose: Risk register row.
- Core fields:
  - `id` (string)
  - `risk` (text)
  - `likelihood` (enum)
  - `impact` (enum)
  - `mitigation` (text)
  - `sprint_code` (string or `All`)
  - `status` (enum)

### 8) DecisionEntry

- Purpose: Architecture and governance decision history.
- Core fields:
  - `id` (string)
  - `date_label` (string/date)
  - `sprint_code` (string)
  - `title` (string)
  - `chosen` (text)
  - `considered` (text)
  - `rationale` (text)

### 9) RetroNote

- Purpose: Sprint retrospective content.
- Core fields:
  - `sprint_code` (string)
  - `went_well` (text)
  - `did_not_go_well` (text)
  - `improvements` (text)

### 10) DodCriterion

- Purpose: Sprint definition-of-done criteria list.
- Core fields:
  - `id` (string)
  - `sprint_code` (string)
  - `criterion` (text)
  - `status` (enum)
  - `sequence` (integer)

### 11) ActivityEvent

- Purpose: Append-only audit stream for mutating actions.
- Core fields:
  - `id` (string)
  - `entity_type` (enum)
  - `entity_id` (string)
  - `action` (enum)
  - `message` (text)
  - `actor` (string)
  - `occurred_at` (datetime)

### 12) WorkspaceConfig

- Purpose: Persisted dashboard configuration values (branding/sprint selection/method label).
- Core fields:
  - `key` (string)
  - `value` (json/text)
  - `scope` (enum)

### 13) SprintMetricsSnapshot (derived)

- Purpose: Deterministic aggregate projection for overview/cards/charts.
- Core fields:
  - `sprint_code` (string)
  - `task_pct` (numeric)
  - `task_count` (string)
  - `open_p1_blockers` (integer)
  - `open_tasks` (integer)
  - `burndown` (json)
  - `burnup` (json)
  - `velocity` (json)
  - `severity` (json)

## Relationship Map

1. `Sprint` 1-to-many `Ticket`.
2. `Ticket` 1-to-many `Subtask`.
3. `Subtask` 0-or-1 `TaskDetail`.
4. `Sprint` 1-to-many `RetroNote` (current = one per sprint, future supports revisions).
5. `Sprint` 1-to-many `DodCriterion`.
6. `Sprint` 1-to-many `HoursEntry`.
7. `Sprint` 1-to-many `RiskEntry` and `DecisionEntry`.
8. `ActivityEvent` many-to-one entity references by (`entity_type`, `entity_id`).

## Required Enums and Status Map

### Ticket/Subtask status enum

- Canonical: `todo`, `in_progress`, `blocked`, `done`.
- Current UI map:
  - `To Do` -> `todo`
  - `In Progress` -> `in_progress`
  - `Blocked` -> `blocked`
  - `Done` -> `done`
  - legacy `In Sprint` -> `in_progress`
  - legacy `Backlog` or `TBD` -> `todo`

### Priority enum

- `critical`, `high`, `medium`, `low`.

### Effort enum

- `xs`, `s`, `m`, `l`, `xl`.

### Risk likelihood/impact enum

- `L`, `M`, `H`.

### Risk status enum

- `open`, `implemented`, `resolved`, `accepted`.

### Sprint state enum

- `planned`, `active`, `done`.

## Mandatory Audit Fields

Every operational mutable entity must carry:

1. `created_at` (datetime)
2. `updated_at` (datetime)
3. `updated_by` (string)
4. `source` (enum: `ui`, `migration`, `system`, `api`)

## Source-of-Truth Rule

1. Operational data source of truth is persisted backend state.
2. Frontend runtime arrays become view caches only after cutover.
3. Browser storage is configuration cache only, not shared operational state.

## Phase 1 Done Criteria Check

1. Coverage matrix complete with named ownership for every active dashboard surface: PASS.
2. Canonical model and enum mapping defined for migration and API design: PASS.

## Phase 1 Evidence Paths

1. This artifact:
   - docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE1_COVERAGE_MODEL.md
2. Automation phase sequence and gate rules:
   - docs/dashboard_product/DASHBOARD_AUTOMATION_PHASE0_KICKOFF.md
   - /memories/repo/pm_dashboard_automation_phased_execution_plan.md

## Gate Decision

Current: PASS
Reason: Phase 1 checklist and evidence requirements are complete in-repo; Phase 2 deterministic migration planning is unblocked.
