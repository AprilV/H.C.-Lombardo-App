# Dashboard Charter

Date: 2026-04-23
Owner: April V. Sykes
Product: H.C. Lombardo PM Dashboard

## Purpose

Operate a visible, auditable delivery system for the capstone project.

The dashboard must show:
- What is planned
- What is in progress
- What is blocked
- What is done
- Who updated what and when

## Users

1. Product owner (April)
2. Academic advisor and evaluators
3. Future employers reviewing PM execution evidence

## Success Criteria

1. Every completed sprint subtask has resolution, date, timestamp, and updater.
2. Every dashboard enhancement is tracked by `DSH-` ticket.
3. Weekly report reflects source arrays without manual spreadsheet work.
4. No localStorage dependency for shared project state.
5. Change history is publishable and reviewable through git and release notes.

## Non-Goals

1. Replacing Jira/Azure DevOps.
2. Multi-user role-based auth.
3. Backend persistence in this phase.

## Constraints

1. Single-file runtime (`Dashboard/index.html`) is current implementation.
2. Public output is served by `gh-pages` deployment.
3. Hardcoded arrays remain the active source for dashboard runtime data.

## Review Cadence

1. Weekly: refresh hours, risks, decisions, and sprint completion evidence.
2. Sprint close: update release notes and dashboard metrics.
3. Monthly: reassess dashboard backlog priorities.
