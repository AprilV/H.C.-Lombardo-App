# TEST ENVIRONMENT GUIDE

## Overview

Current runtime hosts and branch mappings must be verified before deployment:
- Check runtime status in `docs/deployment/AWS_ACCOUNT_RECOVERY_STATUS.md`
- Check active frontend release branch in AWS Amplify console

Test environment is an EXACT MIRROR of production:
- Same Ubuntu 24.04 LTS
- Same Python 3.12
- Same PostgreSQL 16
- Same database structure and data
- Same systemd service setup

## Initial Setup (ONE TIME ONLY)

Run the setup script from your local PC:

```bash
bash setup_test_environment.sh
```

This will:
1. Install all required software on test EC2
2. Clone GitHub repo
3. Optionally set up an isolated validation branch
4. Clone production database to test
5. Install Python dependencies
6. Create and start systemd service

**Time:** ~10-15 minutes

## Daily Workflow

### 1. Make Changes Locally

Edit code on your PC as usual.

### 2. Push to Test Branch

```bash
git status
git add -A
git commit -m "Your change description"
git push origin HEAD
```

If your validation branch is different from your local branch:

```bash
git push origin HEAD:<validation-branch>
```

### 3. Deploy to Test Environment

```bash
bash deploy_to_test.sh
```

This script:
- SSHs to test EC2
- Pulls the configured validation branch
- Restarts the service
- Shows status and health check

If no test EC2 is active, validate locally with `python startup.py` and `python health_check.py`.

### 4. Verify Changes Work

Test the API:
```bash
# Health check
curl http://100.48.43.144:5000/health

# Team Detail API
curl http://100.48.43.144:5000/api/hcl/teams/DAL?season=2025

# ML Predictions
curl http://100.48.43.144:5000/api/predictions/combined/2025/16
```

### 5. If Everything Works → Deploy to Production

```bash
# Push validated code to active production release branch
git push origin HEAD:<release-branch>

# Deploy to production
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@<production-ec2-host> "cd /home/ec2-user/H.C.-Lombardo-App || cd /home/ubuntu/H.C.-Lombardo-App; git fetch origin; git checkout <release-branch>; git pull --ff-only origin <release-branch>; sudo systemctl restart hc-lombardo.service"
```

## Common Commands

### SSH Access

**Test:**
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@<test-ec2-host>
```

**Production:**
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@<production-ec2-host>
```

### Service Management

**Check status:**
```bash
# Test
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@<test-ec2-host> "sudo systemctl status hc-lombardo-test.service"

# Production
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@<production-ec2-host> "sudo systemctl status hc-lombardo.service"
```

**View logs:**
```bash
# Test
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@<test-ec2-host> "sudo journalctl -u hc-lombardo-test.service -f"

# Production
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@<production-ec2-host> "sudo journalctl -u hc-lombardo.service -f"
```

**Restart:**
```bash
# Test
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@<test-ec2-host> "sudo systemctl restart hc-lombardo-test.service"

# Production
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@<production-ec2-host> "sudo systemctl restart hc-lombardo.service"
```

### Database Access

**Test:**
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@<test-ec2-host>
PGPASSWORD=$DB_PASSWORD psql -U nfl_user -d nfl_analytics -h localhost
```

**Production:**
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@<production-ec2-host>
PGPASSWORD=$DB_PASSWORD psql -U nfl_user -d nfl_analytics -h localhost
```

## Troubleshooting

### Service won't start

Check logs:
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@<test-ec2-host> "sudo journalctl -u hc-lombardo-test.service -n 50"
```

### Database connection issues

Verify PostgreSQL is running:
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@<test-ec2-host> "sudo systemctl status postgresql"
```

### Python dependency issues

Reinstall:
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@<test-ec2-host> "cd /home/ubuntu/H.C.-Lombardo-App && source venv/bin/activate && pip install -r requirements.txt"
```

## Important Notes

- Test and production may run on different EC2 hosts; verify active hosts before deployment
- Test database is a clone of production (not live-synced)
- To refresh test database with latest production data, re-run setup clone steps
- Always validate locally before any release push
- Do not assume `master`, `test`, or `staging` is the active release branch without checking deployment config
