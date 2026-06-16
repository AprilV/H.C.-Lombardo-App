# H.C. Lombardo NFL Analytics App

H.C. Lombardo is an NFL analytics and AI prediction platform built for everyday bettors. The product focuses on plain-English verdicts, transparent performance tracking, and AI-vs-Vegas comparisons so users can quickly understand where the edge is.

Educational and entertainment purpose only. Nothing in this project should be interpreted as financial advice.

## Documentation Map

- High-level architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- AI execution and repo governance: [docs/ai_reference](docs/ai_reference)
- Sprint artifacts and delivery evidence: [docs/sprints](docs/sprints)

## Overview

This platform combines historical NFL data, live feeds, and ML predictions into a single workflow:

- Evaluate weekly matchups
- Compare model calls against sportsbook lines
- Track long-term AI-vs-Vegas performance
- Present results in a user-friendly, confidence-oriented UI

## System Architecture

- Frontend: React single-page app, deployed on Netlify
- Backend: Flask REST API on an AWS EC2 instance (us-east-2), running as a systemd service on port 5000
- Database: PostgreSQL on the same EC2 host (NFL games, team stats, predictions, betting lines)
- ML stack:
	- XGBoost winner classifier
	- XGBoost spread regressor
	- Elo ratings system
- Model artifact location on EC2:
	- `ml/models/xgb_winner.pkl`
	- `ml/models/xgb_spread.pkl`
	- `ml/models/elo_ratings_current.json`
- Data sources:
	- NFLverse (historical play-by-play; 1999-2025)
	- ESPN API (live data)
- PM Forge / Agile dashboard:
	- Published separately via GitHub Pages from `gh-pages`

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## Local Development

### Prerequisites

- Node.js (for frontend)
- Python 3.11+ and virtual environment tooling
- PostgreSQL (local or remote dev database)

### Frontend

```bash
cd frontend
npm install
npm start
```

### Backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python api_server.py
```

You can also use repo control scripts:

```bash
python startup.py
python shutdown.py
```

### Environment Variables

Use environment variables (or `.env`) for sensitive values. Never commit real secrets.

Required placeholders:

- `DB_HOST=<DB_HOST_PLACEHOLDER>`
- `DB_PORT=<DB_PORT_PLACEHOLDER>`
- `DB_NAME=<DB_NAME_PLACEHOLDER>`
- `DB_USER=<DB_USER_PLACEHOLDER>`
- `DB_PASSWORD=<DB_PASSWORD_PLACEHOLDER>`
- `REACT_APP_API_URL=<API_BASE_URL_PLACEHOLDER>`

Notes:

- In production, frontend is served on Netlify and calls the production API base URL.
- In local development, set `REACT_APP_API_URL` to your local or dev API endpoint.

## Deployment

### Frontend (Netlify)

- Branch: `master`
- Flow: push to `master` -> Netlify auto-builds and deploys
- CI behavior: `CI=true`, so unused vars/imports fail builds

### Backend (EC2)

Typical release flow:

1. Connect to EC2 via AWS Systems Manager Session Manager
2. Pull latest `master`
3. Restart Flask service

```bash
sudo systemctl restart <FLASK_SERVICE_NAME>
sudo systemctl status <FLASK_SERVICE_NAME>
```

Infrastructure placeholders (do not replace in public docs):

- EC2 host: `<EC2_HOST_PLACEHOLDER>`
- AWS account: `<AWS_ACCOUNT_ID_PLACEHOLDER>`

### PM Forge / Agile Dashboard

- Published from branch: `gh-pages`
- Hosting: GitHub Pages

## Backup and Recovery

### Backup Strategy

- Code backup:
	- `master` branch: application code
	- `gh-pages` branch: PM Forge dashboard publishing branch
- Database and model backup target:
	- S3 bucket: `<S3_BUCKET_PLACEHOLDER>`
	- Prefix format: `ec2-backups/YYYYMMDD_HHMMSS/`

### Backup Procedure (Generic)

1. Create database backup (custom PostgreSQL format):

```bash
pg_dump -Fc -h <DB_HOST_PLACEHOLDER> -U <DB_USER_PLACEHOLDER> -d <DB_NAME_PLACEHOLDER> -f nfl_analytics.dump
```

2. Archive ML models:

```bash
tar -czf ml_models.tar.gz ml/models/
```

3. Upload both artifacts to S3:

```bash
aws s3 cp nfl_analytics.dump s3://<S3_BUCKET_PLACEHOLDER>/ec2-backups/<TIMESTAMP_PLACEHOLDER>/
aws s3 cp ml_models.tar.gz s3://<S3_BUCKET_PLACEHOLDER>/ec2-backups/<TIMESTAMP_PLACEHOLDER>/
```

### Recovery Procedure (Generic)

1. Download backup artifacts from S3
2. Restore database:

```bash
pg_restore -h <DB_HOST_PLACEHOLDER> -U <DB_USER_PLACEHOLDER> -d <DB_NAME_PLACEHOLDER> --clean --if-exists nfl_analytics.dump
```

3. Restore models:

```bash
tar -xzf ml_models.tar.gz -C .
```

## Security Notes

- Credentials are stored in environment variables, not source code.
- Public documentation and UI intentionally avoid exposing infrastructure identifiers (IPs, account IDs, bucket names, credentials).
- Secrets must never be committed to Git history, docs, screenshots, or logs.

## Capstone Context

- Program: Senior Capstone Project
- Student: April V. Sykes
- Advisor: Richard Becker
- Institution: Olympic College
- Term: Spring 2026
