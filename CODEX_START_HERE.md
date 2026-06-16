# CODEX START HERE

Last updated: 2026-06-16

This file is the startup orientation for current-state work in this repository.

## Scope Lock

- APP workstream: frontend/src
- DASHBOARD workstream: pmforge_dashboard/index.html
- DOCS workstream: docs, .github, sessions

Do not mix workstreams in one task.

## Current Deployment Reality

- Frontend is deployed on Netlify.
- Backend runs on EC2 with PostgreSQL.
- PM Forge dashboard is published through gh-pages.

For details, use docs/DEPLOY_AND_ARCHITECTURE.md.

## Startup Protocol

1. Run the startup guard command:
   - ./scripts/maintenance/session_resume_guard.ps1 -Reason "Startup lock trigger"
2. Read newest sessions/SESSION_RESUME_YYYY-MM-DD_HHMM.md.
3. Confirm scope and report before edits.

## Verification Rule

Do not claim a deploy is live until all checks agree:

1. origin/master source check
2. origin/gh-pages source check (dashboard only)
3. Real URL response check (no cache query)
4. Browser runtime check on the same real URL
