# SYSTEM TOPOLOGY

**Authority Level:** Architecture Reference  
**Last Updated:** May 14, 2026

**Startup Control Note:** For local operation, use `python startup.py` to start services and `python shutdown.py` to stop services.

## PURPOSE

This document explains the complete network topology of the HC Lombardo App in both production and test environments. Understanding this topology is CRITICAL before making any deployments or architectural changes.

---

## PRODUCTION TOPOLOGY

```
┌─────────────────────┐
│   USER'S BROWSER    │
└──────────┬──────────┘
           │ HTTPS
           ↓
┌─────────────────────────────────────────────┐
│      AWS AMPLIFY - Frontend Website         │
│  Current live frontend host (verify current)│
│                                             │
│  • React application (JavaScript)           │
│  • Source: Active GitHub release branch     │
│  • Deploy mode: Git-connected or artifact   │
│  • Serves HTML/CSS/JS to browser            │
└──────────┬──────────────────────────────────┘
           │ HTTP API calls
           ↓
┌─────────────────────────────────────────────┐
│    AWS EC2 (34.198.25.249:5000)            │
│         Production API Server               │
│                                             │
│  • Python backend (Flask/Gunicorn)          │
│  • api_server.py (main Flask app)           │
│  • api_routes_hcl.py (team/game data)       │
│  • api_routes_ml.py (predictions)           │
│  • Source: Approved release branch          │
│  • Manual deployment via SSH/SSM            │
│  • Service: systemd (hc-lombardo.service)   │
│  • 2 Gunicorn workers, 120s timeout         │
└──────────┬──────────────────────────────────┘
           │ SQL queries
           ↓
┌─────────────────────────────────────────────┐
│    PostgreSQL Database (same EC2)           │
│                                             │
│  • Database: nfl_analytics                  │
│  • User: nfl_user                           │
│  • Contains: games, teams, predictions      │
│  • Live production data                     │
└─────────────────────────────────────────────┘
```

**Production URLs:**
- Frontend: Verify current live host in deployment/dashboard config
- API: Verify current live API host in deployment docs
- Database: localhost:5432 (on EC2)

**Production Git Branch:** Verify active release branch before every push

---

## TEST TOPOLOGY

```
┌─────────────────────┐
│   USER'S BROWSER    │
│  (localhost:3000)   │
└──────────┬──────────┘
           │ HTTP
           ↓
┌─────────────────────────────────────────────┐
│     LOCAL PC - Frontend Development         │
│           npm start (port 3000)             │
│                                             │
│  • EXACT SAME React code as production      │
│  • Source: c:\ReactGitEC2\IS330\H.C Lombardo App\frontend│
│  • Runs on developer's PC                   │
│  • Environment variable points to test API  │
│  • REACT_APP_API_URL=http://127.0.0.1:5000  │
└──────────┬──────────────────────────────────┘
           │ HTTP API calls
           ↓
┌─────────────────────────────────────────────┐
│    Local Flask API (127.0.0.1:5000)        │
│         Development API Server              │
│                                             │
│  • Same backend codebase as production      │
│  • Source: local workspace                  │
│  • Started via startup.py / START-DEV.bat   │
│  • Local dev runtime configuration           │
└──────────┬──────────────────────────────────┘
           │ SQL queries
           ↓
┌─────────────────────────────────────────────┐
│    PostgreSQL Database (same EC2)           │
│                                             │
│  • Database: nfl_analytics                  │
│  • User: nfl_user                           │
│  • CLONE of production database             │
│  • Snapshot taken during test setup         │
└─────────────────────────────────────────────┘
```

**Test URLs:**
- Frontend: http://localhost:3000 (on developer PC)
- API: http://127.0.0.1:5000
- Database: localhost:5432 (on test EC2)

**Test Git Branch:** Optional, only if a dedicated test branch flow is currently active

---

## KEY DIFFERENCES: PRODUCTION vs TEST

| Component | Production | Test |
|-----------|-----------|------|
| **Frontend Hosting** | AWS Amplify | Developer's PC (npm start) |
| **Frontend URL** | Current live host (verify) | http://localhost:3000 |
| **Frontend Source** | GitHub active release branch | Local filesystem (c:\ReactGitEC2\...\frontend) |
| **Frontend Deployment** | Git-connected branch deploy or manual artifact upload | Manual (npm start) |
| **API Server Host** | Current production host (verify) | 127.0.0.1 |
| **API Source** | GitHub approved release branch | Local workspace or optional test branch |
| **API Deployment** | Manual SSH/SSM + service restart | Local run or optional deploy script |
| **Service Name** | hc-lombardo.service | hc-lombardo-test.service |
| **Database** | Live production data | Clone of production (snapshot) |
| **Git Branch** | Release branch (verify) | Working branch (verify) |

---

## CRITICAL ARCHITECTURE POINTS

### 1. Frontend Code is IDENTICAL

The React code running on your PC during testing is **THE EXACT SAME CODE** that runs on AWS Amplify in production. The only difference is:
- **Where it runs:** AWS Amplify (production) vs your PC (test)
- **Which API it calls:** Configured via REACT_APP_API_URL environment variable

### 2. API Code is IDENTICAL

The Python code on test EC2 is **THE EXACT SAME CODE** as production EC2. The only differences are:
- **Git branch:** active release branch (production) vs optional validation branch (test)
- **IP address:** Different EC2 instances
- **Database:** Live data (production) vs snapshot (test)

### 3. Database is a SNAPSHOT

The test database is **NOT live-synced** with production. It's a one-time clone taken during test environment setup. To refresh test data:
1. SSH to production: dump database
2. SSH to test: restore database
3. This is manual - not automated

### 4. Deployment Independence

- **Frontend:** Amplify deployment mode must be checked before push (Git-connected vs manual artifact)
- **Backend Production:** Manual runtime update (pull approved branch + systemctl restart)
- **Backend Test:** Optional and environment-dependent; do not assume test EC2 is available

---

## DATA FLOW

### Production Request Flow

```
User clicks button in browser
  ↓
React app (AWS Amplify) sends HTTP request to 34.198.25.249:5000/api/...
  ↓
Flask app (api_server.py) receives request
  ↓
Routes to api_routes_hcl.py or api_routes_ml.py
  ↓
Queries PostgreSQL database (localhost:5432)
  ↓
Returns JSON response
  ↓
React app displays data in browser
```

### Test Request Flow

```
User clicks button in browser (localhost:3000)
  ↓
React app (npm start on PC) sends HTTP request to 127.0.0.1:5000/api/...
  ↓
Flask app (api_server.py locally) receives request
  ↓
Routes to api_routes_hcl.py or api_routes_ml.py
  ↓
Queries PostgreSQL database (localhost:5432)
  ↓
Returns JSON response
  ↓
React app displays data in browser
```

**Key Point:** The data flow is IDENTICAL. Only runtime hosts differ by mode.

---

## DEPLOYMENT WORKFLOW

### Making Backend Changes (Python API)

1. **Edit code on PC:** Modify api_routes_hcl.py or other Python files
2. **Validate locally before pushing:**
   ```powershell
  python startup.py
  python health_check.py
  ./scripts/maintenance/verify_backend_core_chain.ps1
  ```
3. **Commit and push your working branch:**
  ```powershell
  git status
  git add -A
   git commit -m "Fix: description"
  git push origin HEAD
   ```
4. **Promote to release branch and push:**
   ```powershell
  git push origin HEAD:<release-branch>
   ```
5. **Run frontend locally:**
   ```powershell
   cd frontend
  $env:REACT_APP_API_URL="http://127.0.0.1:5000"
   npm start
   ```
6. **Test in browser:** http://localhost:3000
7. **Deploy backend runtime (SSH/SSM) and restart service:**
   ```powershell
  ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@<current-ec2-host> "cd /home/ec2-user/H.C.-Lombardo-App || cd /home/ubuntu/H.C.-Lombardo-App; git fetch origin; git checkout <release-branch>; git pull --ff-only origin <release-branch>; sudo systemctl restart hc-lombardo.service"
   ```

### Making Frontend Changes (React UI)

1. **Edit code on PC:** Modify React components in frontend/src/
2. **Test locally:**
   ```powershell
   cd frontend
   npm start
   # Opens localhost:3000 automatically
   ```
3. **If works, deploy to production:**
   ```powershell
  git status
  git add -A
   git commit -m "UI: description"
  git push origin HEAD
  # If needed: git push origin HEAD:<release-branch>
  # Amplify deploys via configured mode (wait 2-3 minutes if Git-connected)
   ```

**Note:** Frontend changes don't need test EC2 - you can test directly on localhost:3000 calling production API.

---

## SECURITY NOTES

### Production

- Frontend served over HTTPS (AWS Amplify provides SSL)
- API served over HTTP (internal, not exposed publicly except via frontend)
- Database accessible only from localhost on EC2

### Test

- Frontend on localhost (HTTP, development only)
- API on HTTP (test EC2, accessible from developer PC)
- Database accessible only from localhost on test EC2

### Access Control

- **Production EC2:** SSH via hc-lombardo-key.pem (34.198.25.249)
- **Test EC2:** Verify current host before SSH (environment may be local-only)
- **Both EC2s:** Security group allows SSH (22), HTTP (80), Custom TCP (5000)

---

## DISASTER RECOVERY

### If Production API Fails

1. Check logs: `ssh ubuntu@34.198.25.249 "sudo journalctl -u hc-lombardo.service -n 100"`
2. Restart service: `ssh ubuntu@34.198.25.249 "sudo systemctl restart hc-lombardo.service"`
3. If code issue: revert to last working commit, git pull, restart

### If Production Frontend Fails

1. Check AWS Amplify console for deployment errors
2. Revert commit on GitHub master branch
3. AWS Amplify will auto-redeploy previous version

### If Test Environment Breaks

Test environment is expendable - can be rebuilt from scratch using setup_test_environment.sh. Production is unaffected.

---

## FUTURE ARCHITECTURE CONSIDERATIONS

### Not Currently Implemented

- **Automated database sync:** Test DB is manual snapshot, not continuous
- **Frontend test hosting:** Frontend tested locally, not on separate Amplify environment
- **CI/CD pipeline:** All deployments are manual
- **Load balancing:** Single EC2 instance for production API
- **Database backups:** No automated backup system
- **Monitoring/alerting:** No uptime monitoring or error alerts

### Potential Improvements

1. **Separate Amplify environments:** Create test.amplify.app for frontend testing
2. **Database replication:** Auto-sync test DB with production nightly
3. **GitHub Actions:** Automated testing and deployment on push
4. **Multi-instance setup:** Load balancer + multiple EC2 instances
5. **Managed database:** Move to AWS RDS for automated backups
6. **Monitoring:** AWS CloudWatch or Datadog integration

---

## TROUBLESHOOTING COMMON TOPOLOGY ISSUES

### "Frontend can't reach API"

**Symptom:** Browser console shows CORS errors or failed API requests

**Diagnosis:**
1. Check which API URL frontend is using (browser DevTools Network tab)
2. Verify API server is running: `curl http://127.0.0.1:5000/health`
3. Check REACT_APP_API_URL environment variable

**Solution:**
- Production: Frontend should call the currently configured production API host
- Test: Set `$env:REACT_APP_API_URL="http://127.0.0.1:5000"` before npm start

### "Changes not showing up after deployment"

**Symptom:** Pushed code changes but website/API behaves the same

**Diagnosis:**
1. Check which branch is checked out on EC2: `git branch`
2. Check last commit on EC2: `git log -1`
3. Verify service restarted: `systemctl status hc-lombardo.service`

**Solution:**
- Ensure git pull ran successfully
- Ensure systemctl restart ran after pull
- Check for Python import cache issues: delete `__pycache__` folders

### "Test environment not mirroring production"

**Symptom:** Code works in test but fails in production (or vice versa)

**Diagnosis:**
1. Compare Python versions: `python3 --version` on both EC2s
2. Compare package versions: `pip freeze` on both EC2s
3. Compare database schemas: check table structures
4. Compare environment variables: check systemd service files

**Solution:**
- Reinstall Python packages on test to match production
- Re-clone production database to test
- Verify systemd service configurations are identical

---

## REFERENCES

- **Setup Script:** setup_test_environment.sh
- **Deployment Script:** deploy_to_test.sh
- **User Guide:** TEST_ENVIRONMENT_GUIDE.md
- **Production API:** Verify current production host
- **Test API:** 127.0.0.1:5000
- **GitHub Repo:** https://github.com/AprilV/H.C.-Lombardo-App
