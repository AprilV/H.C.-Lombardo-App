# TEST ENVIRONMENT GUIDE

## Overview

**Production EC2:** 34.198.25.249  
**Test EC2:** 100.48.43.144

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
3. Create `test` branch
4. Clone production database to test
5. Install Python dependencies
6. Create and start systemd service

**Time:** ~10-15 minutes

## Daily Workflow

### 1. Make Changes Locally

Edit code on your PC as usual.

### 2. Push to Test Branch

```bash
git checkout test
git add .
git commit -m "Your change description"
git push origin test
```

### 3. Deploy to Test Environment

```bash
bash deploy_to_test.sh
```

This script:
- SSHs to test EC2
- Pulls latest `test` branch
- Restarts the service
- Shows status and health check

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
# Merge test into master
git checkout master
git merge test
git push origin master

# Deploy to production
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249 "cd /home/ubuntu/H.C.-Lombardo-App && git pull origin master && sudo systemctl restart hc-lombardo.service"
```

## Common Commands

### SSH Access

**Test:**
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@100.48.43.144
```

**Production:**
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249
```

### Service Management

**Check status:**
```bash
# Test
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@100.48.43.144 "sudo systemctl status hc-lombardo-test.service"

# Production
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249 "sudo systemctl status hc-lombardo.service"
```

**View logs:**
```bash
# Test
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@100.48.43.144 "sudo journalctl -u hc-lombardo-test.service -f"

# Production
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249 "sudo journalctl -u hc-lombardo.service -f"
```

**Restart:**
```bash
# Test
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@100.48.43.144 "sudo systemctl restart hc-lombardo-test.service"

# Production
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249 "sudo systemctl restart hc-lombardo.service"
```

### Database Access

**Test:**
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@100.48.43.144
PGPASSWORD=aprilv120 psql -U nfl_user -d nfl_analytics -h localhost
```

**Production:**
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249
PGPASSWORD=aprilv120 psql -U nfl_user -d nfl_analytics -h localhost
```

## Troubleshooting

### Service won't start

Check logs:
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@100.48.43.144 "sudo journalctl -u hc-lombardo-test.service -n 50"
```

### Database connection issues

Verify PostgreSQL is running:
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@100.48.43.144 "sudo systemctl status postgresql"
```

### Python dependency issues

Reinstall:
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@100.48.43.144 "cd /home/ubuntu/H.C.-Lombardo-App && source venv/bin/activate && pip install -r requirements.txt"
```

## Important Notes

- Test and Production run on SEPARATE EC2 instances
- Test database is a CLONE of production (not live-synced)
- To refresh test database with latest production data, re-run step 6 of setup script
- Always test changes on Test environment before deploying to Production
- Both environments use same database credentials (nfl_user / aprilv120)
