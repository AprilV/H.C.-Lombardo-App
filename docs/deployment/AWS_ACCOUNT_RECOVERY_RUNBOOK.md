# AWS Account Recovery Runbook (Sprint 14)

Last Updated: 2026-05-15

## Purpose

Recover H.C. Lombardo production on a new AWS account and prevent credit burn from high-frequency deploys.

Status tracking source:
- docs/deployment/AWS_ACCOUNT_RECOVERY_STATUS.md

This runbook follows the locked governance rules:
- Production deploys are ticket-bundle based.
- Minimum bundle size is 3 TA tickets (3+ rule).
- No per-subtask production pushes.

## Bundle A Scope (first release bundle)

1. TA-072: New AWS account continuity path.
2. TA-063: EC2 cleanup and runtime recovery tasks.
3. TA-008: Restore live app URL in dashboard.
4. Carryover unblock: s11_2 EC2 access recovery check.

## What You Need To Do

These steps require your direct AWS/registrar access.

1. Create the new AWS account and secure access.
- Enable MFA.
- Add a second recovery factor.
- Create an IAM admin user for daily work (do not use root for routine operations).

2. Configure billing guardrails before launching resources.
- Set monthly budget alerts.
- Enable anomaly detection alerts.
- Add threshold notifications (for example, low, medium, and high spend thresholds).

3. Provision baseline resources.
- Create EC2 instance for backend runtime.
- Create security group with least required inbound rules.
- Create/attach Elastic IP for API endpoint.
- Create Amplify app linked to this repository.

4. Update DNS at registrar.
- Point `nfl` host to new Amplify target.
- Point `api` host to new EC2 Elastic IP.

5. Confirm access checkpoints back to me.
- EC2 SSH access works.
- Amplify app exists and can build.
- DNS changes saved.

## What I Will Do

1. Repo and workflow guardrails.
- Keep production data workflow manual-only.
- Keep dashboard workflow scoped to dashboard files only.
- Keep docs aligned with bundle-release policy.

2. Backend/app validation support.
- Verify routes, CORS, health endpoints, and prediction endpoints.
- Provide exact command sets for EC2 bootstrap, service restart, and verification.

3. Evidence and sprint closure support.
- Map outputs to TA-072/TA-063/TA-008 evidence requirements.
- Prepare checklist outputs for dashboard status updates.

## Verification Gate (must pass before Bundle A close)

1. Frontend public URL loads expected app shell.
2. API public health endpoint returns healthy.
3. Frontend can call API routes from production domain.
4. Key prediction routes return valid payloads.
5. Dashboard live-app button points to working public app URL.

## Deployment Frequency Controls

1. One approved push per release bundle.
2. Minimum 3 TA tickets per bundle.
3. Manual-only production data workflow execution.
4. No automatic weekly production workflow run.

## Notes

- Do not share secrets (keys, passwords, tokens) in chat.
- Share only non-sensitive status outputs (pass/fail, endpoint reachability, instance IDs if needed).
