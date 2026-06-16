# AWS Account Recovery Status

Last Updated: 2026-05-16
Owner: April Sykes
Scope: Sprint 14 AWS continuity recovery (TA-072, TA-063, TA-008, TA-025, carryover s11_2)

## Why This File Exists

This is the single source of truth for AWS recovery progress so setup history is not lost and steps do not need to be rediscovered.

## Current Snapshot

- New AWS account created: Yes
- Root account email: april_sykes@proton.me
- AWS account ID: 563960656132
- Root MFA enabled: Yes (virtual MFA assigned)
- Root access key present: No (deleted 2026-05-15)
- Root access key status: Deleted
- Billing guardrails configured: Yes (monthly budget and cost anomaly alert subscription configured)
- Non-root IAM admin user created: Yes (hcl-admin)
- IAM admin sign-in credentials saved securely: Yes (CSV downloaded and stored)
- IAM admin console sign-in/password recovery: Completed
- IAM admin MFA enabled: Yes (enabled 2026-05-15)
- Backup strategy lock: EC2 runtime + S3 backups
- S3 backup bucket created: Yes (hcl-lombardo-backups-563960656132-us-east-2)
- S3 backup test upload completed: Yes (DB dump + app bundle uploaded)
- Final validated backup after data load: Yes (latest prefix: ec2-backups/20260516_022248/)
- EC2 provisioned in new account: Yes (Running, Session Manager connected)
- Admin SSH readiness evidence: Confirmed (sshd active/enabled, key auth enabled, port 22 listening, SG sg-071735c7da61895cc allows SSH from 24.18.67.141/32)
- Pre-cleanup disk baseline captured: Yes (/tmp/ta63_s638_precleanup_20260516_030531.txt; root fs 34% used, /var=285M, /var/log=26M, journal=24M)
- Safe cleanup pass completed: Yes (/tmp/ta63_s639_cleanup_20260516_030748.txt; root fs reduced to 33% used, major cache reclaim completed)
- Service restart validation status: Completed (postgresql/hc-lombardo/nginx active; /health and /api/hcl/teams?season=2025 returned 200)
- Post-cleanup utilization validation captured: Yes (/tmp/ta63_s6311_postcleanup_20260516_031652.txt; ROOT_USE_PCT=33, UTIL_TARGET_ROOT_LE_40=pass)
- Cleanup command/outcome/rollback evidence documented: Yes (TA-063 s63_12 complete in recovery log + dashboard task details)
- EC2 API service configured: Yes (hc-lombardo systemd service active)
- EC2 API health endpoint: Healthy ({"status":"healthy","database":"connected","cors":"enabled"})
- Automated backup schedule configured: Yes (daily 02:15 via ec2-user crontab)
- Local backup retention hardening: Yes (keeps 2 newest local backup directories)
- Historical production dataset loaded on EC2: Yes (hcl.games=7276, hcl.team_game_stats=15474, season_range=1999-2025)
- Advanced metrics backfill status: Completed (total_yards/completion_pct non-null coverage 1999-2025; 14546 populated rows)
- public.teams restored and seeded: Yes (32 rows)
- HCL data endpoint validation: Yes (/api/hcl/teams success for season=1999 and season=2025)
- Amplify app provisioned in new account: Yes (app1699, app_id=d2fwv8daemi5y2, branch=staging)
- DNS cutover completed: No (legacy custom domains still pending; Amplify default domain is active)
- TA-008 live app URL status: Completed (public frontend URL restored and validated at https://staging.d2fwv8daemi5y2.amplifyapp.com/)
- API Gateway HTTPS proxy path restored: Yes (hcl-api-proxy, api_id=9dkkj5n2rc, routes `/` and `/{proxy+}` mapped to EC2 integration)
- API Gateway CORS for staging origin: Enabled (Access-Control-Allow-Origin = https://staging.d2fwv8daemi5y2.amplifyapp.com; methods/headers wildcard)
- ML runtime dependency status: Recovered (xgboost 2.1.4 installed in /home/ec2-user/H.C.-Lombardo-App/venv)
- ModelPerformance schema dependencies: Restored (add_epa_columns.sql and create_predictions_tracking.sql applied on EC2)
- TA-025 model metrics flow status: Completed (backend endpoints and staging ModelPerformance render path validated)
- Sprint 14 dashboard closure gate: Pass (52 subtasks, 52 completed, 0 blocked)

## Locked Governance Rules

1. Production deploys are ticket-bundle approvals only.
2. Minimum 3 TA tickets per production release (3+ rule).
3. No per-subtask production pushes.
4. Production data workflow is manual-only (no weekly auto schedule).

## Bundle A Execution Checklist

- [x] TA-072 s72_1: Provision and secure new AWS account access (MFA and billing validated)
- [x] TA-072 s72_2: Stand up/recover EC2 runtime with required network/security configuration
- [x] TA-072 s72_3: Update deployment credentials/workflow and verify pull + restart path
- [x] TA-072 s72_4: Validate app health and capture post-cutover evidence
- [x] TA-063 s63_7: Recover AWS/EC2 access path and confirm admin SSH readiness
- [x] TA-063 s63_8: Capture pre-cleanup disk baseline
- [x] TA-063 s63_9: Remove safe-to-delete logs/cache/tmp artifacts
- [x] TA-063 s63_10: Restart and validate services
- [x] TA-063 s63_11: Capture post-cleanup disk usage and utilization target
- [x] TA-063 s63_12: Record cleanup commands and outcomes
- [x] TA-008 t8_1: Update dashboard live app URL to working production frontend
- [x] TA-025 s25_1: Verify performance endpoint returns expected winner/spread metric payload
- [x] TA-025 s25_2: Confirm ModelPerformance page handles empty and populated states
- [x] TA-025 s25_3: Validate weekly trend and benchmark delta metric structures
- [x] TA-025 s25_4: Record acceptance evidence for restored metrics flow
- [x] Carryover s11_2: Clear blocked EC2 recovery dependency

## Decision Log

- 2026-05-15: Move forward with AWS recovery path on new account.
- 2026-05-15: Release cadence locked to 3+ TA bundle rule.
- 2026-05-15: Backup architecture locked: EC2 for app/runtime, S3 for backup storage.

## Step-By-Step Tracking Log

- 2026-05-15: New AWS account created (email and account ID recorded above).
- 2026-05-15: Root MFA enabled and attached to root user.
- 2026-05-15: Root access key generated and saved locally; key value not stored in project records.
- 2026-05-15: Root access key set to Inactive (confirmed via console screenshot); deletion still required.
- 2026-05-15: Root access key deleted (user confirmed).
- 2026-05-15: Monthly AWS Cost Budget created successfully (10 USD monthly budget with alerts visible in console screenshot).
- 2026-05-15: Cost Anomaly Detection alert subscription created successfully (HCL Cost Anomaly Alert, daily summaries, 1 USD threshold, email recipient).
- 2026-05-15: IAM admin user hcl-admin created with console access and temporary password retrieval screen confirmed.
- 2026-05-15: IAM admin credentials CSV downloaded and saved securely (user confirmed).
- 2026-05-15: IAM admin password recovery/login step completed by user using an autogenerated password.
- 2026-05-15: IAM admin MFA enabled successfully (confirmed in IAM security credentials).
- 2026-05-15: EC2 launch submitted with SSM instance profile and network/storage settings.
- 2026-05-15: EC2 instance hcl-api-prod-1 reached Running state with all status checks passed.
- 2026-05-15: Session Manager shell opened and root/bootstrap commands executed on hcl-api-prod-1.
- 2026-05-16: Amazon Linux packages installed for runtime (git, python3/pip, PostgreSQL 15 server/client, nginx).
- 2026-05-16: PostgreSQL initialized and started; nfl_user role and nfl_analytics database created with grants applied.
- 2026-05-16: PostgreSQL auth rules updated in pg_hba.conf to allow password auth for nfl_user; API DB connection confirmed.
- 2026-05-16: Repo cloned to /home/ec2-user/H.C.-Lombardo-App; Python venv and requirements installed.
- 2026-05-16: hc-lombardo systemd service created, enabled, and started; /health returned healthy.
- 2026-05-16: IAM role hcl-ec2-ssm-role updated to include AmazonS3FullAccess.
- 2026-05-16: S3 bucket hcl-lombardo-backups-563960656132-us-east-2 created and configured (versioning + AES256 encryption).
- 2026-05-16: Backup script /home/ec2-user/backup_hcl_to_s3.sh created and executed; DB dump and app tar uploaded to S3.
- 2026-05-16: Daily backup automation configured in ec2-user crontab: 15 2 * * * cd ~ && ./backup_hcl_to_s3.sh >> ~/backup_hcl_to_s3.log 2>&1.
- 2026-05-16: Production schema applied from production_hcl_schema.sql on EC2 PostgreSQL.
- 2026-05-16: Historical load executed in four chunks via scripts/data_loading/ingest_historical_games.py --production for seasons 1999-2006, 2007-2014, 2015-2020, and 2021-2025.
- 2026-05-16: Post-load verification confirmed hcl.games=7276, hcl.team_game_stats=14552, season coverage 1999-2025, db_size=15 MB, and /health healthy.
- 2026-05-16: public.teams table recreated on EC2 (missing in new account DB), seeded from insert_teams.sql, and standings synced with scripts/data_loading/update_public_teams_from_games.py --season 2025.
- 2026-05-16: /api/hcl/teams endpoint revalidated successfully (season=1999 count=31, season=2025 count=32).
- 2026-05-16: Backup retention script hardened and fixed (timestamp pattern + working directory) and validated to keep exactly two local backups while uploading to S3.
- 2026-05-16: Advanced stat backfill completed for remaining historical seasons using ingest_historical_games.load_team_game_stats (final non-null coverage reached 1999-2025).
- 2026-05-16: Post-backfill verification recorded: hcl.games=7276, hcl.team_game_stats=15474, total_yards/completion_pct non-null=14546, null=928.
- 2026-05-16: Runtime validation recorded: /health returned 200 healthy and /api/hcl/teams?season=2025 returned 200 with count=32.
- 2026-05-16: Final backup re-run and validated at ec2-backups/20260516_022248/ (S3 objects: app_bundle.tar.gz and nfl_analytics.sql; local retention remained at 2 backup directories).
- 2026-05-16: TA-063 s63_7 access path re-validated via Session Manager (ssm-user shell reachable on i-023b034755afb1486; public IP 18.223.118.197).
- 2026-05-16: TA-063 s63_7 SSH readiness confirmed on-host (sshd active/enabled, listeners on 0.0.0.0:22 and [::]:22, effective auth config: pubkeyauthentication yes, passwordauthentication no, permitrootlogin without-password).
- 2026-05-16: TA-063 s63_7 security boundary confirmed in EC2 console for sg-071735c7da61895cc (Inbound SSH TCP/22 allowed from 24.18.67.141/32 only).
- 2026-05-16: TA-063 s63_8 pre-cleanup baseline captured at /tmp/ta63_s638_precleanup_20260516_030531.txt (root filesystem 20G total, 6.7G used, 14G available, 34%; /var=285M, /var/log=26M, /tmp=48K, /home/ec2-user/.cache=100M; journals use 24.0M).
- 2026-05-16: TA-063 s63_8 largest log artifacts before cleanup identified (three 8.0M journal files under /var/log/journal/... plus audit and SSM agent logs) to guide safe deletion scope in s63_9.
- 2026-05-16: TA-063 s63_9 safe cleanup executed with evidence file /tmp/ta63_s639_cleanup_20260516_030748.txt (dnf/yum cache purge, old tmp/var/tmp sweep, ec2-user cache cleanup, journal vacuum attempt).
- 2026-05-16: TA-063 s63_9 cleanup results recorded: /var/cache reduced 152140931 -> 1546978 bytes (~150.6 MB reclaimed), /home/ec2-user/.cache reduced 103387022 -> 6 bytes (~103.4 MB reclaimed), root usage dropped from 34% to 33%, and 679 user-cache artifacts were removed.
- 2026-05-16: TA-063 s63_9 post-cleanup note: /var/log and journald footprint increased during active maintenance execution (logs 26656566 -> 35088491 bytes; journal 24.0M -> 32.0M), so follow-up service restart/post-check remains required in s63_10/s63_11.
- 2026-05-16: TA-063 s63_10 service restart executed with evidence file /tmp/ta63_s6310_restart_20260516_031434.txt (postgresql, hc-lombardo, nginx restarted successfully).
- 2026-05-16: TA-063 s63_10 validation confirmed all core services active and listening (hc-lombardo on :5000, nginx on :80) with endpoint checks passing (/health 200 and /api/hcl/teams?season=2025 200).
- 2026-05-16: TA-063 s63_11 post-cleanup verification captured in /tmp/ta63_s6311_postcleanup_20260516_031652.txt (root filesystem 20G total, 6.5G used, 14G available, 33%; ROOT_USE_PCT=33; UTIL_TARGET_ROOT_LE_40=pass).
- 2026-05-16: TA-063 s63_12 evidence consolidation completed in this tracker and dashboard artifacts (cleanup command files: /tmp/ta63_s638_precleanup_20260516_030531.txt, /tmp/ta63_s639_cleanup_20260516_030748.txt, /tmp/ta63_s6310_restart_20260516_031434.txt, /tmp/ta63_s6311_postcleanup_20260516_031652.txt; rollback anchor: ec2-backups/20260516_022248/).
- 2026-05-16: Dashboard status sync completed in pmforge_dashboard/index.html (TA-063 and TA-072 moved from blocked to done with evidence-backed TASK_DETAILS updates).
- 2026-05-16: Ticket evidence sync completed for EC2/S3 restore narrative (TA-072 parent ticket detail now explicitly records restored EC2 runtime path and verified S3 backup objects under ec2-backups/20260516_022248/).
- 2026-05-16: TA-008 t8_1 re-validation performed from browser checks; live frontend targets master.d2tamnlcbzo0d5.amplifyapp.com and nfl.aprilsykes.dev both failed DNS resolution (ERR_NAME_NOT_RESOLVED), so TA-008 remains blocked pending working frontend URL restoration.
- 2026-05-16: Amplify console check completed in us-east-2 for account 563960656132; page shows onboarding state (Deploy an app / Start with a template), confirming no frontend app is currently provisioned for TA-008 URL assignment.
- 2026-05-16: TA-008 execution resumed in Amplify console: created app1699 and staging branch using manual deploy path (Deploy without Git) in us-east-2.
- 2026-05-16: Initial deploy artifact (frontend_build_upload.zip) produced 404s for /static/js and /static/css due Windows path separators in zip entries.
- 2026-05-16: Repacked frontend artifact as frontend_build_upload_posix.zip with forward-slash paths and redeployed via Amplify "Deploy updates".
- 2026-05-16: Amplify deployment reached Deployed for app_id d2fwv8daemi5y2; domain https://staging.d2fwv8daemi5y2.amplifyapp.com is reachable and frontend shell loads at / and /team-stats.
- 2026-05-16: Dashboard governance sync completed for TA-008 (t8_1 moved Blocked -> Done, live URL defaults updated, PB TA-008 status set to Done, completion evidence recorded).
- 2026-05-16: API Gateway recovery completed for TA-025 path: created route ANY /{proxy+}, attached integration URI ANY http://18.223.118.197/{proxy}, and confirmed /health + /api/hcl/teams over HTTPS invoke URL.
- 2026-05-16: Installed missing xgboost in EC2 runtime venv (2.1.4) using TMPDIR override and restarted hc-lombardo service.
- 2026-05-16: Applied missing DB migrations on EC2 PostgreSQL for model metrics flow (add_epa_columns.sql and create_predictions_tracking.sql).
- 2026-05-16: Enabled API Gateway CORS for staging origin and validated Access-Control-Allow-Origin headers on /health and /api/hcl/teams with Origin request header.
- 2026-05-16: Staging frontend re-validation passed for data-path restoration: dashboard/team stats/ML pages fetch data from execute-api endpoint; ModelPerformance page renders without endpoint failure.
- 2026-05-16: Executed Sprint 14 dashboard closure gate check (`scripts/maintenance/dashboard_closure_gate.py`) with PASS result: subtasks=52, completed=52, blocked=0.

## Next Single Step

Run Sprint 14 dashboard closure gate and publish final Sprint 14 completion evidence package.

## Related Documents

- docs/deployment/AWS_ACCOUNT_RECOVERY_RUNBOOK.md
- docs/deployment/DEPLOYMENT_GUIDE.md
- .github/workflows/nfl-data-update.yml
- pmforge_dashboard/index.html
