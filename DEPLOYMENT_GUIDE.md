# H.C. Lombardo NFL Analytics - Deployment Guide

**Complete infrastructure setup and technical documentation**  
*Last Updated: November 27, 2025*

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Domain Setup (Namecheap)](#domain-setup-namecheap)
3. [Backend Infrastructure (AWS EC2)](#backend-infrastructure-aws-ec2)
4. [Frontend Hosting (AWS Amplify)](#frontend-hosting-aws-amplify)
5. [Database Configuration](#database-configuration)
6. [Critical Configuration Files](#critical-configuration-files)
7. [Deployment Workflow](#deployment-workflow)
8. [Common Issues & Solutions](#common-issues--solutions)

---

## Architecture Overview

### System Design
```
User Browser (HTTPS)
    ↓
AWS Amplify (Frontend) ───────→ https://nfl.aprilsykes.dev
    │                            https://master.d2tamnlcbzo0d5.amplifyapp.com
    ↓ (API Calls)
AWS EC2 (Backend API) ─────────→ https://api.aprilsykes.dev
    │                            IP: 34.198.25.249
    ↓
PostgreSQL Database (on EC2)
    └─ Database: nfl_analytics
    └─ User: nfl_user
```

### Technology Stack
- **Frontend**: React 18 (Create React App)
- **Backend**: Python Flask + Gunicorn
- **Database**: PostgreSQL 14
- **Web Server**: Nginx (reverse proxy + SSL termination)
- **SSL**: Let's Encrypt (Certbot)
- **Version Control**: GitHub (AprilV/H.C.-Lombardo-App)

### Why This Architecture?

**AWS Amplify for Frontend:**
- ✅ Automatic builds on git push
- ✅ Free tier includes 1000 build minutes/month
- ✅ Built-in CDN for fast global delivery
- ✅ 8 GB RAM build servers (vs 1 GB on EC2)
- ✅ No manual deployment needed

**AWS EC2 for Backend:**
- ✅ Full control over Python environment
- ✅ PostgreSQL database on same machine (low latency)
- ✅ Can run background jobs (data updates)
- ✅ Cost-effective t3.micro ($0.0104/hour)

**Separation of Concerns:**
- Frontend can scale independently
- Backend can be upgraded without affecting UI
- HTTPS everywhere (no mixed content errors)

---

## Domain Setup (Namecheap)

### Domain Registration
- **Domain**: aprilsykes.dev
- **Registrar**: Namecheap
- **Purchase Date**: November 27, 2025
- **Cost**: $6.98/year (Black Friday promo code: MATRIXTLD25)
- **Expiration**: November 28, 2026
- **Privacy**: WhoisGuard enabled (free)

### DNS Configuration

**Access**: Namecheap Dashboard → Domain List → Manage → Advanced DNS

| Record Type | Host | Value | TTL | Purpose |
|------------|------|-------|-----|---------|
| A Record | `api` | `34.198.25.249` | Automatic | Backend API endpoint |
| CNAME Record | `nfl` | `master.d2tamnlcbzo0d5.amplifyapp.com` | Automatic | Frontend app |

**Propagation Time**: 
- Typical: 5-30 minutes
- Maximum: Up to 48 hours (Namecheap specific)

### How to Add DNS Records

1. Log into Namecheap
2. Navigate to: Domain List → aprilsykes.dev → Manage
3. Click "Advanced DNS" tab
4. Click "Add New Record"
5. For API subdomain:
   - Type: `A Record`
   - Host: `api`
   - Value: `34.198.25.249`
   - TTL: `Automatic`
6. For NFL subdomain:
   - Type: `CNAME Record`
   - Host: `nfl`
   - Value: `master.d2tamnlcbzo0d5.amplifyapp.com`
   - TTL: `Automatic`

---

## Backend Infrastructure (AWS EC2)

### Instance Details
- **Instance ID**: i-076502f470ab36343
- **Type**: t3.micro (1 vCPU, 1 GB RAM)
- **OS**: Ubuntu 22.04 LTS
- **Region**: us-east-1 (N. Virginia)
- **Elastic IP**: 34.198.25.249 (permanent, doesn't change on restart)
- **SSH Key**: hc-lombardo-key.pem (stored in `~/.ssh/`)

### Security Group Configuration
**Group ID**: sg-0bf4d667de8b0eafe

| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 22 | TCP | Your IP | SSH access |
| 80 | TCP | 0.0.0.0/0 | HTTP (redirects to HTTPS) |
| 443 | TCP | 0.0.0.0/0 | HTTPS (API traffic) |
| 5000 | TCP | Localhost | Flask application |
| 5432 | TCP | Localhost | PostgreSQL database |

### SSH Access
```bash
# Windows PowerShell
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249

# Connect with timeout (recommended)
ssh -i ~/.ssh/hc-lombardo-key.pem -o ConnectTimeout=10 ubuntu@34.198.25.249
```

### Installed Software

**System Packages:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv postgresql nginx certbot python3-certbot-nginx
```

**Python Virtual Environment:**
```bash
# Location: ~/H.C.-Lombardo-App/venv
cd ~/H.C.-Lombardo-App
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Key Python Packages:**
- Flask 2.3.0
- flask-cors 4.0.0
- psycopg2-binary 2.9.9
- gunicorn 21.2.0
- pandas, numpy, scikit-learn (for ML models)

### Nginx Configuration

**Purpose**: Reverse proxy to Flask app + SSL termination

**Config File**: `/etc/nginx/sites-available/api.aprilsykes.dev`

```nginx
server {
    listen 80;
    server_name api.aprilsykes.dev;
    
    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name api.aprilsykes.dev;
    
    # SSL certificates from Let's Encrypt
    ssl_certificate /etc/letsencrypt/live/api.aprilsykes.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.aprilsykes.dev/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
    
    # Proxy all requests to Flask app on port 5000
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable Configuration:**
```bash
sudo ln -s /etc/nginx/sites-available/api.aprilsykes.dev /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl reload nginx
```

### SSL Certificate Setup

**Tool**: Certbot (Let's Encrypt)

**Installation:**
```bash
sudo apt install certbot python3-certbot-nginx
```

**Obtain Certificate:**
```bash
sudo certbot --nginx -d api.aprilsykes.dev
```

**Certificate Details:**
- Issuer: Let's Encrypt
- Expiration: February 25, 2026 (90 days from issue)
- Auto-renewal: Enabled via `certbot.timer`
- Location: `/etc/letsencrypt/live/api.aprilsykes.dev/`

**Check Auto-Renewal:**
```bash
sudo systemctl status certbot.timer
sudo certbot renew --dry-run  # Test renewal process
```

### Running the API

**Manual Start:**
```bash
cd ~/H.C.-Lombardo-App
source venv/bin/activate
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 api_server:app
```

**Background Process (current method):**
```bash
cd ~/H.C.-Lombardo-App
source venv/bin/activate
nohup gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 api_server:app > gunicorn.log 2>&1 &
```

**Check if Running:**
```bash
ps aux | grep gunicorn
```

**Kill Existing Process:**
```bash
pkill -9 gunicorn
```

**Restart API (full process):**
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249 \
  "cd ~/H.C.-Lombardo-App && \
   git pull && \
   pkill -9 gunicorn && \
   sleep 2 && \
   source venv/bin/activate && \
   nohup gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 api_server:app > gunicorn.log 2>&1 &"
```

### Environment Variables

**File**: `~/H.C.-Lombardo-App/.env`

```env
DB_NAME=nfl_analytics
DB_USER=nfl_user
DB_PASSWORD=nfl2024
DB_HOST=localhost
DB_PORT=5432
```

**Why .env file?**
- Keeps secrets out of git repository
- Easy to update without code changes
- Python `dotenv` package loads automatically

---

## Frontend Hosting (AWS Amplify)

### App Configuration
- **App Name**: H.C.-Lombardo-App
- **Region**: us-east-1 (same as EC2)
- **Repository**: https://github.com/AprilV/H.C.-Lombardo-App
- **Branch**: master (auto-deploy enabled)
- **Build Instance**: Standard (8 GB RAM)

### URLs
- **Amplify Default**: https://master.d2tamnlcbzo0d5.amplifyapp.com
- **Custom Domain**: https://nfl.aprilsykes.dev (via CNAME)

### Build Configuration

**File**: `amplify.yml` (in repository root)

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/build
    files:
      - '**/*'
  cache:
    paths:
      - frontend/node_modules/**/*
backend:
  phases:
    build:
      commands:
        - pip install -r requirements.txt
```

**Key Points:**
- `npm ci` instead of `npm install` (faster, uses package-lock.json)
- Build happens in `frontend/` subdirectory
- Output artifacts from `frontend/build/`
- Node modules cached between builds

### Build Process

**Trigger**: Automatic on every `git push` to master branch

**Steps:**
1. Amplify detects new commit on GitHub
2. Provisions build container (8 GB RAM)
3. Runs `npm ci` to install dependencies
4. Runs `npm run build` to create production bundle
5. Deploys to CDN
6. Build time: 2-3 minutes

**Build Logs**: Available in Amplify Console → App → Build history

### Why Amplify Over EC2 for Frontend?

**Problem with EC2 (t3.micro):**
- Only 1 GB RAM
- React build needs ~800 MB
- Also running PostgreSQL + Python API
- Build takes 30+ minutes or crashes

**Amplify Solution:**
- 8 GB RAM build servers
- Dedicated to builds only
- Builds complete in 2-3 minutes
- No impact on backend performance
- Automatic deployment on push

---

## Database Configuration

### PostgreSQL Setup

**Version**: PostgreSQL 14  
**Database**: `nfl_analytics`  
**User**: `nfl_user`  
**Password**: `nfl2024`

**Access:**
```bash
# From EC2 instance
psql -U nfl_user -h localhost -d nfl_analytics

# Set password in environment
export PGPASSWORD=nfl2024
psql -U nfl_user -h localhost -d nfl_analytics
```

### Database Schema

**Primary Schema**: `hcl` (Historical Context Layer)

**Tables:**
- `hcl.teams` - NFL team information (32 teams)
- `hcl.games` - Game results and schedules (7,263 games)
- `hcl.team_game_stats` - Per-game team statistics (14,398 records)
- `hcl.ml_predictions` - AI model predictions (800 predictions)
- `hcl.betting_data` - Vegas lines and spreads
- `hcl.weather_data` - Weather conditions for games
- `hcl.referee_data` - Referee assignments and statistics

**Feature Views** (for ML models):
- `hcl.v_team_betting_performance` - Win/loss vs spread
- `hcl.v_weather_impact_analysis` - Weather effects on scoring
- `hcl.v_rest_advantage` - Days of rest between games
- `hcl.v_referee_tendencies` - Referee statistics

### Database Permissions

```sql
-- Grant permissions to nfl_user
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA hcl TO nfl_user;
GRANT USAGE ON SCHEMA hcl TO nfl_user;
```

### Data Volume
- **Total Games**: 7,263 (seasons 1999-2025)
- **Total Statistics**: 14,398 team-game records
- **Predictions**: 800 (current season)
- **Database Size**: ~50 MB

---

## Critical Configuration Files

### 1. Frontend: API URL Configuration

**Affected Files** (13 total):
```
frontend/src/App.js
frontend/src/Homepage.js
frontend/src/GameStatistics.js
frontend/src/TeamStats.js
frontend/src/TeamDetail.js
frontend/src/ModelPerformance.js
frontend/src/MLPredictions.js
frontend/src/MatchupAnalyzer.js
frontend/src/LiveScores.js
frontend/src/LiveGamesTicker.js
frontend/src/HistoricalData.js
frontend/src/Analytics.js
frontend/src/Admin.js
```

**Configuration Pattern:**
```javascript
const API_URL = 'https://api.aprilsykes.dev';

// All API calls use this constant
fetch(`${API_URL}/api/hcl/teams?season=2025`)
```

### 2. Backend: CORS Configuration

**File**: `api_server.py`

```python
from flask_cors import CORS

CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",           # Local development
            "http://127.0.0.1:3000", 
            "http://localhost:5000", 
            "http://127.0.0.1:5000",
            "https://master.d2tamnlcbzo0d5.amplifyapp.com",  # Amplify default
            "https://nfl.aprilsykes.dev",      # Custom domain
            "null"                             # File protocol
        ],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})
```

**Why CORS is Critical:**
- Browser security prevents cross-origin requests by default
- Frontend (nfl.aprilsykes.dev) calls API (api.aprilsykes.dev)
- Different domains = CORS required
- Missing origin = "CORS policy blocked" error

### 3. Backend: Team Abbreviation Mapping

**File**: `api_routes_live_scores.py`

**Problem**: ESPN API and database use different team abbreviations

```python
TEAM_ABBR_MAP = {
    'LAR': 'LA',   # ESPN uses LAR, database uses LA (Rams)
    'WSH': 'WAS',  # ESPN uses WSH, database uses WAS (Washington)
}

def normalize_team_abbr(abbr):
    """Convert ESPN abbreviation to database format"""
    return TEAM_ABBR_MAP.get(abbr, abbr)
```

**Frontend Logo Mapping:**

Files: `LiveGamesTicker.js`, `Homepage.js`, `TeamStats.js`

```javascript
const teamLogoMap = {
  'WSH': 'was',  // ESPN data uses WSH, logo file is was.png
  'WAS': 'was',  // Database uses WAS
  'LAR': 'lar',  // LA Rams
  'LAC': 'lac',  // LA Chargers
};

const getTeamLogoName = (abbr) => {
  return (teamLogoMap[abbr] || abbr).toLowerCase();
};

// Usage
<img src={`/images/teams/${getTeamLogoName(team.abbreviation)}.png`} />
```

### 4. Database Connection

**File**: `db_config.py`

```python
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}
```

**Reads from .env file** (not in git repository)

---

## Deployment Workflow

### Complete Deployment Process

```
Local Development → GitHub → AWS (Amplify + EC2)
```

### Step-by-Step Deployment

#### 1. Make Code Changes Locally
```bash
cd "c:\IS330\H.C Lombardo App"

# Edit files as needed
# Example: frontend/src/Homepage.js
```

#### 2. Test Locally (Optional)
```bash
# Frontend
cd frontend
npm start  # http://localhost:3000

# Backend
python api_server.py  # http://localhost:5000
```

#### 3. Commit to Git
```bash
git add .
git commit -m "Descriptive message about changes"
git push origin master
```

#### 4. Automatic Deployments

**Frontend (AWS Amplify):**
- Detects push automatically
- Starts build within 30 seconds
- Completes in 2-3 minutes
- Live at https://nfl.aprilsykes.dev

**Backend (AWS EC2):**
- Manual pull and restart required
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249 \
  "cd ~/H.C.-Lombardo-App && \
   git pull && \
   pkill -9 gunicorn && \
   sleep 2 && \
   source venv/bin/activate && \
   nohup gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 api_server:app > gunicorn.log 2>&1 &"
```

### Deployment Checklist

**Before Pushing:**
- [ ] Test changes locally
- [ ] Check for console errors
- [ ] Verify API endpoints work
- [ ] Review git diff

**After Pushing:**
- [ ] Monitor Amplify build logs (if frontend changes)
- [ ] SSH to EC2 and restart API (if backend changes)
- [ ] Test live site: https://nfl.aprilsykes.dev
- [ ] Check browser console for errors
- [ ] Verify API responses: https://api.aprilsykes.dev/health

---

## Common Issues & Solutions

### Issue 1: CORS Errors

**Symptom:**
```
Access to fetch at 'https://api.aprilsykes.dev/...' has been blocked by CORS policy: 
No 'Access-Control-Allow-Origin' header is present
```

**Cause**: Amplify domain not in CORS whitelist

**Solution:**
1. Add domain to `api_server.py` CORS origins
2. Push to GitHub
3. Pull on EC2 and restart gunicorn

### Issue 2: Missing Predictions on Cards

**Symptom:** Some game cards show predictions, others don't

**Cause:** Team abbreviation mismatch (ESPN vs database)

**Solution:**
1. Add mapping in `api_routes_live_scores.py` → `TEAM_ABBR_MAP`
2. Restart API on EC2

### Issue 3: Missing Team Logos

**Symptom:** Team logo doesn't display, shows abbreviation instead

**Cause:** Logo filename doesn't match team abbreviation

**Solution:**
1. Add mapping in `teamLogoMap` (Frontend components)
2. Push to GitHub (Amplify auto-deploys)

### Issue 4: Database Connection Failed

**Symptom:**
```
connection to server at "localhost", port 5432 failed: 
FATAL: password authentication failed for user "nfl_user"
```

**Cause:** Missing `.env` file on EC2

**Solution:**
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249
cd ~/H.C.-Lombardo-App
cat > .env << EOF
DB_NAME=nfl_analytics
DB_USER=nfl_user
DB_PASSWORD=nfl2024
DB_HOST=localhost
DB_PORT=5432
EOF
```

### Issue 5: EC2 Build Out of Memory

**Symptom:** npm build crashes or takes 30+ minutes

**Solution:** Don't build on EC2! Use AWS Amplify for frontend builds.

### Issue 6: SSL Certificate Expired

**Symptom:** Browser shows "Your connection is not private"

**Solution:**
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249
sudo certbot renew
sudo systemctl reload nginx
```

### Issue 7: API Not Responding

**Check if Running:**
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249
ps aux | grep gunicorn
```

**Check Logs:**
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249
tail -50 ~/H.C.-Lombardo-App/gunicorn.log
```

**Restart:**
```bash
pkill -9 gunicorn
cd ~/H.C.-Lombardo-App
source venv/bin/activate
nohup gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 api_server:app > gunicorn.log 2>&1 &
```

---

## Key Learnings & Best Practices

### 1. Separation of Frontend and Backend
**Why it matters:**
- Frontend scales independently on Amplify CDN
- Backend handles compute-intensive ML predictions
- Can update UI without touching database

### 2. HTTPS Everywhere
**Why it matters:**
- Browsers block mixed content (HTTPS → HTTP)
- Protects user data
- Required for production apps
- Free with Let's Encrypt

### 3. Environment Variables for Secrets
**Why it matters:**
- Passwords never committed to git
- Easy to rotate credentials
- Different values for dev/prod

### 4. Team Abbreviation Mapping
**Why it matters:**
- External APIs (ESPN) use different conventions
- Database may use historical abbreviations
- Logos named differently than data
- Need consistent mapping layer

### 5. Automatic Deployments
**Why it matters:**
- Amplify: Push to git = auto-deploy
- Reduces human error
- Faster iteration
- Always know what's deployed

### 6. Documentation
**Why it matters:**
- You will forget how you set this up
- Others can maintain your system
- Debugging is faster with docs
- This file you're reading now!

---

## Quick Reference Commands

### SSH to EC2
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249
```

### Restart API
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249 \
  "cd ~/H.C.-Lombardo-App && git pull && pkill -9 gunicorn && sleep 2 && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 api_server:app > gunicorn.log 2>&1 &"
```

### Check API Logs
```bash
ssh -i ~/.ssh/hc-lombardo-key.pem ubuntu@34.198.25.249 "tail -50 ~/H.C.-Lombardo-App/gunicorn.log"
```

### Deploy Frontend + Backend
```bash
# From local machine
cd "c:\IS330\H.C Lombardo App"
git add .
git commit -m "Your changes"
git push

# Wait 2-3 minutes for Amplify build
# Then restart EC2 API (command above)
```

### Test Endpoints
```bash
# Health check
curl https://api.aprilsykes.dev/health

# Get teams
curl https://api.aprilsykes.dev/api/hcl/teams?season=2025

# Live scores
curl https://api.aprilsykes.dev/api/live-scores
```

---

## Cost Breakdown

| Service | Tier | Cost | Notes |
|---------|------|------|-------|
| **Namecheap Domain** | - | $6.98/year | aprilsykes.dev |
| **AWS EC2 (t3.micro)** | Free tier | $0.00 | First 12 months free |
| **AWS EC2 (after free)** | On-demand | ~$7.50/month | $0.0104/hour × 730 hours |
| **Elastic IP** | - | $0.00 | Free while attached to running instance |
| **AWS Amplify** | Free tier | $0.00 | 1000 build minutes/month |
| **Let's Encrypt SSL** | - | $0.00 | Free forever |
| **GitHub** | Free | $0.00 | Public repository |
| **Total (Year 1)** | - | **$6.98** | Domain only |
| **Total (Year 2+)** | - | **~$96/year** | Domain + EC2 |

**Ways to Reduce Costs:**
- Stop EC2 when not in use ($0 when stopped)
- Use AWS Free Tier credits
- Consider AWS Lightsail ($3.50/month alternative to EC2)

---

## Maintenance Schedule

### Daily
- Monitor Amplify build status (if pushing changes)
- Check API health: `curl https://api.aprilsykes.dev/health`

### Weekly
- Review gunicorn logs for errors
- Check database size: `du -sh /var/lib/postgresql/`

### Monthly
- Test SSL certificate renewal: `sudo certbot renew --dry-run`
- Review AWS billing dashboard
- Update Python packages: `pip install --upgrade -r requirements.txt`

### Quarterly
- Review and archive old logs
- Database optimization: `VACUUM ANALYZE;`
- Security updates: `sudo apt update && sudo apt upgrade`

### Annually
- Renew domain (Namecheap auto-renewal recommended)
- Review architecture for improvements
- Update documentation

---

## Support & Resources

### Documentation
- **AWS Amplify**: https://docs.amplify.aws/
- **AWS EC2**: https://docs.aws.amazon.com/ec2/
- **Nginx**: https://nginx.org/en/docs/
- **Let's Encrypt**: https://letsencrypt.org/docs/
- **Flask CORS**: https://flask-cors.readthedocs.io/

### Monitoring URLs
- **Frontend**: https://nfl.aprilsykes.dev
- **API Health**: https://api.aprilsykes.dev/health
- **Amplify Console**: https://console.aws.amazon.com/amplify/
- **EC2 Console**: https://console.aws.amazon.com/ec2/

### Repository
- **GitHub**: https://github.com/AprilV/H.C.-Lombardo-App

---

**Document Version**: 1.0  
**Last Updated**: November 27, 2025  
**Maintained By**: April Sykes  
**Questions?** Review this guide first, then check logs, then debug systematically.
