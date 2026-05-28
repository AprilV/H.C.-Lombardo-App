# TA-017 Secret Exposure Audit Evidence

Date: 2026-05-27
Owner: GitHub Copilot (Developer)
Ticket: TA-017
Scope: Audit git history and tracked repository content for exposed secrets

## Summary
- Completed credential/signature audit across tracked files and full git history.
- No AWS key ID, GitHub PAT, Google API key, Slack token, or Stripe live-key signatures were detected.
- Literal database password values were detected in both tracked scripts and historical/devlog artifacts.
- Audit outcome: exposure risk exists for DB credentials in repository artifacts and utility scripts; remediation is required in follow-up hardening work.

## Audit Commands
### Working tree signature scan (tracked files)
- `git grep -n -I -E "AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82,}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35}|sk_live_[0-9A-Za-z]{16,}" -- .`

### Working tree literal-password checks
- `git grep -n -I "aprilv120" -- . ":(exclude)docs/devlog/**" ":(exclude)docs/ai_reference/DEV_LOG_FULL.txt" ":(exclude)docs/archive/**" ":(exclude)backups/**"`
- `git grep -n -I "nfl2024" -- . ":(exclude)docs/devlog/**" ":(exclude)docs/ai_reference/DEV_LOG_FULL.txt" ":(exclude)docs/archive/**" ":(exclude)backups/**"`

### History checks
- `git log --all --oneline -S"aprilv120" --`
- `git log --all --oneline -S"nfl2024" --`
- `git log --all --oneline -G"AKIA[0-9A-Z]{16}" --`
- `git log --all --oneline -G"ghp_[A-Za-z0-9]{36}" --`

## Verification Results
### Signature patterns
- Working tree + history:
  - `AKIA*`: 0
  - `ASIA*`: 0
  - `ghp_*`: 0
  - `github_pat_*`: 0
  - `AIza*`: 0
  - `xox*`: 0
  - `sk_live_*`: 0

### Literal credential findings
- `aprilv120`:
  - 80 tracked-file hits after excluding archive/devlog baseline paths above.
  - 37 hits across 31 script/executable files (`.py`, `.sh`, `.bat`, `.service`, etc.).
  - `git log -S"aprilv120"`: 56 commits.
- `nfl2024`:
  - 15 tracked-file hits after exclusions above.
  - 2 script-file hits.
  - `git log -S"nfl2024"`: 20 commits.

## High-Risk Active Script Findings (Representative)
- `START-DEV.bat`
- `START.bat`
- `startup.py`
- `hc-lombardo-updater.service`
- `scripts/maintenance/multi_source_data_fetcher.py`
- `scripts/maintenance/startup.py`
- `scripts/maintenance/update_live_data.py`
- `scripts/maintenance/simple_api.py`
- `scripts/verification/check_local_schema.py`
- `scripts/verification/check_dallas_ties.py`

## History/Artifact Findings (Representative)
- `devlog_output.html` includes multiple historical code diff fragments with literal DB passwords.
- `docs/ai_reference/STARTUP_GUIDE.md` includes literal credential values.
- `docs/deployment/DEPLOYMENT_GUIDE.md` includes literal DB password references.

## Risk Assessment
- Severity: High
- Rationale:
  - Literal DB credentials remain in active scripts and automation/service definitions.
  - Historical artifacts retain credential literals, expanding disclosure surface.
  - Current ticket objective was audit; this report confirms remediation is still required.

## Recommended Remediation (Follow-up)
1. Rotate all affected DB credentials immediately.
2. Replace hardcoded literals with environment-only lookups in active scripts and service files.
3. Remove or sanitize credential literals from operational docs and generated devlog artifacts.
4. Perform history rewrite/sanitization only after explicit approval and repository impact review.
5. Re-run this audit after remediation and attach delta evidence.

## Acceptance Mapping
- Step 01: Defined audit pattern set for common key/token signatures and literal credential probes.
- Step 02: Scanned tracked files and quantified current-exposure matches.
- Step 03: Audited git history for signature and literal-password evidence.
- Step 04: Published findings, severity, and remediation recommendations in this evidence bundle.
