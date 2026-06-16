# DEPLOY & ARCHITECTURE - current truth

This is the single source of truth for how things are built and deployed. If any other doc disagrees, it is stale - fix or delete it.
Last updated: 2026-06-16.

---

## Two products, two SEPARATE deploy paths. Never cross them.

### 1. H.C. Lombardo APP (the React product)

- Source: `frontend/src/**` on branch `master`.
- Deploy: push to `master` -> Netlify auto-builds and publishes. No manual upload. No Amplify.
- Live at: `https://hclombardo.com/` (Netlify-hosted custom domain).
- Build guard: `CI=true` - unused vars/imports fail the build.
- Backend it talks to: Flask API on AWS EC2 (see below). This part did not change.

### 2. PM Forge / Agile Forge DASHBOARD (the sprint dashboard you present from)

- Source: `pmforge_dashboard/index.html` on branch `master` (a single file).

The dashboard is authored in the PM Forge Suite (`C:\PMForgeSuite`) and imported via `scripts/suite/import_pmforge_suite.ps1`, then committed to `master`.

- The suite source is upstream of the repo. Any fix made only in `pmforge_dashboard/index.html` is overwritten on the next import. Secrets and stale content must be fixed in `C:\PMForgeSuite` too, or they reappear.
- Deploy: push to `master` -> GitHub Action `.github/workflows/dashboard-pages-deploy.yml` publishes to the `gh-pages` branch.
- Live at: `https://aprilv.github.io/H.C.-Lombardo-App/`.
- NEVER edit the `gh-pages` branch directly. It is automation-output only.

A task touches ONE of these. `frontend/src` = app. `pmforge_dashboard/index.html` = dashboard. They are not related.

---

## Cached vs live (this is the trap that wasted hours)

After you push, the live site can lag behind `master` for three reasons: the Action hasn't run yet, GitHub Pages/CDN cache, or your browser cache. "It looks wrong" is often "I'm looking at an old copy."

To confirm the live dashboard equals `master`:

1. Confirm the deploy Action ran green (repo -> Actions tab).
2. Compare the deployed file to master:
   `curl -s https://raw.githubusercontent.com/AprilV/H.C.-Lombardo-App/gh-pages/index.html | wc -l` - line count should match `pmforge_dashboard/index.html` on master.
3. Hard-reload the page with the tab closed and reopened (kills browser cache).

For the app (Netlify): confirm the Netlify deploy finished, then hard-reload. Same principle.

If gh-pages did not update after a push, deploy directly: copy `pmforge_dashboard/index.html` into a `gh-pages` worktree and push it.

---

## Backend (unchanged - AWS)

- API: Flask + Gunicorn on AWS EC2 (us-east-2), systemd service on port 5000, reached via AWS SSM Session Manager (no public SSH).
- Database: PostgreSQL on the same EC2 instance.
- Backend deploy: SSM in -> `git pull origin master` -> restart the service. (Frontend changes do NOT require this.)

## No longer used (delete on sight in docs)

- AWS Amplify - the frontend moved to Netlify. Any doc presenting Amplify as the current frontend host is stale.
- Old per-date "PRODUCTION_DEPLOYMENT_" runbooks are historical only.

## Secrets - placeholders only

Never put the EC2 IP, AWS account ID, S3 bucket name, DB password, or Amplify subdomains in committed docs. Use plain placeholder tokens instead, like `EC2_IP_PLACEHOLDER` or `AWS_ACCOUNT_PLACEHOLDER`.

Note: some of these still exist in git history; a history scrub is a separate post-graduation task.
