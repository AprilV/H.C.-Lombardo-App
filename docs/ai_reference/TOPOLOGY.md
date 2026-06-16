# SYSTEM TOPOLOGY

Authority Level: Architecture Reference
Last Updated: 2026-06-16

Startup control note: use python startup.py to start local services and python shutdown.py to stop local services.

## Purpose

This document provides a current topology summary for production and local development.
For deployment and verification details, use docs/DEPLOY_AND_ARCHITECTURE.md.

## Production Topology

- Frontend: Netlify-hosted React application
- API: Flask service on EC2
- Database: PostgreSQL on the same EC2 host
- Dashboard: PM Forge static site on gh-pages

Flow:

1. Browser requests frontend from Netlify.
2. Frontend sends API requests to Flask service.
3. Flask reads and writes PostgreSQL data.
4. Dashboard is published independently from gh-pages.

## Local Development Topology

- Frontend dev server: localhost:3000
- API dev server: localhost:5000
- Database: configured local/dev PostgreSQL target

Flow:

1. Browser requests frontend from local dev server.
2. Frontend sends API requests to local Flask endpoint.
3. Flask reads and writes the configured dev database.

## Branch And Deploy Topology

- Source branch for app/backend/dashboard source: master
- Dashboard publish branch: gh-pages

## Identifier Policy

Do not store real infrastructure identifiers in current-reference docs.
Use placeholders for hosts, account IDs, bucket names, and gateway IDs.

## Legacy Notes

Historical topology records are retained in archive paths for governance traceability.
