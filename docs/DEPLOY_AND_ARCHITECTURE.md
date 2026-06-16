# Deploy And Architecture

Status: ACTIVE source of truth
Last updated: 2026-06-16

This document is the single current reference for runtime architecture and deploy flow.

## Live Topology

- Frontend: React app on Netlify
- Backend: Flask API on EC2 (systemd service)
- Database: PostgreSQL on the same EC2 host
- Dashboard: PM Forge static artifact published to gh-pages

## Branch And Publish Rules

- App and backend source branch: master
- Dashboard source file: pmforge_dashboard/index.html on master
- Dashboard publish branch: gh-pages

Do not edit gh-pages directly as source-of-truth content.

## Frontend Deploy (Netlify)

1. Update frontend/src files on master.
2. Push commit to origin/master.
3. Netlify auto-builds and publishes.
4. Verify live URL response and runtime behavior.

## Backend Deploy (EC2)

1. Update backend files on master.
2. Push commit to origin/master.
3. Deploy/restart backend service on EC2 using approved operational path.
4. Verify health endpoint and key API endpoints.

Use placeholders in docs only:

- <EC2_HOST_PLACEHOLDER>
- <FLASK_SERVICE_NAME_PLACEHOLDER>
- <DB_HOST_PLACEHOLDER>
- <DB_NAME_PLACEHOLDER>

## Dashboard Deploy (gh-pages)

1. Edit pmforge_dashboard/index.html on master.
2. Push commit to origin/master.
3. Confirm gh-pages updated from master.
4. If auto-publish lags, use scripts/maintenance/publish_pmforge_live.ps1 fallback.

## Verification Contract

Before claiming a deploy is live, confirm all relevant checks:

1. origin/master artifact contains expected change
2. origin/gh-pages artifact contains expected change (dashboard only)
3. Real URL response contains expected change (no cache query)
4. Browser runtime at real URL renders expected change

## Secret And Identifier Handling

Do not store real infrastructure identifiers in current docs.

Replace with placeholders:

- <EC2_IP_PLACEHOLDER>
- <AWS_ACCOUNT_ID_PLACEHOLDER>
- <S3_BUCKET_PLACEHOLDER>
- <API_GATEWAY_ID_PLACEHOLDER>
- <LEGACY_HOST_PLACEHOLDER>

Historical records may remain in archive paths for traceability.
