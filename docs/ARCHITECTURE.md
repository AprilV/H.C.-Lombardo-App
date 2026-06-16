# H.C. Lombardo Architecture

## Purpose

H.C. Lombardo is an NFL analytics and AI prediction platform focused on helping everyday bettors interpret model output in plain language. The system compares model projections to Vegas lines and presents transparent, user-facing verdicts.

Educational and entertainment purpose only.

## High-Level Topology

- Frontend: React SPA
- API layer: Flask REST service
- Data layer: PostgreSQL
- ML layer: XGBoost winner model, XGBoost spread model, Elo system
- External data feeds: NFLverse (historical), ESPN API (live)
- Secondary product surface: PM Forge / Agile dashboard on GitHub Pages (`gh-pages`)

## Runtime Architecture

### Frontend

- Framework: React
- Deployment: Netlify
- Trigger: push to `master`
- Build guard: `CI=true` (lint/compile strictness)

### Backend

- Framework: Flask
- Host: AWS EC2 (us-east-2)
- Service: systemd-managed process on port 5000
- Service placeholder name: `<FLASK_SERVICE_NAME_PLACEHOLDER>`

### Database

- Engine: PostgreSQL
- Host location: same EC2 instance
- Data domain:
  - historical games
  - team statistics
  - predictions
  - betting line context

### ML Artifacts

Stored under:

- `ml/models/xgb_winner.pkl`
- `ml/models/xgb_spread.pkl`
- `ml/models/elo_ratings_current.json`

## Data Flow (Simplified)

1. Historical and live data are collected from NFLverse and ESPN API.
2. Backend normalizes and stores data in PostgreSQL.
3. ML models generate winner and spread outputs.
4. API endpoints return predictions and comparisons.
5. Frontend renders verdicts, confidence framing, and AI-vs-Vegas outcomes.

## Environments and Configuration

All sensitive configuration must be environment-driven.

Required placeholder values:

- `EC2_HOST=<EC2_HOST_PLACEHOLDER>`
- `AWS_ACCOUNT_ID=<AWS_ACCOUNT_ID_PLACEHOLDER>`
- `S3_BUCKET=<S3_BUCKET_PLACEHOLDER>`
- `DB_PASSWORD=<DB_PASSWORD_PLACEHOLDER>`
- `REACT_APP_API_URL=<API_BASE_URL_PLACEHOLDER>`

Never commit real values in repository docs or source.

## Deployment Workflows

### Frontend

- Push to `master`
- Netlify automatically builds and deploys

### Backend

- Connect to EC2 via AWS SSM
- Pull latest `master`
- Restart service

```bash
sudo systemctl restart <FLASK_SERVICE_NAME_PLACEHOLDER>
sudo systemctl status <FLASK_SERVICE_NAME_PLACEHOLDER>
```

## Backup and Recovery Model

### Backups

- Code: GitHub branches (`master`, `gh-pages`)
- Data + models: S3 backups

S3 destination format:

- Bucket: `<S3_BUCKET_PLACEHOLDER>`
- Prefix: `ec2-backups/YYYYMMDD_HHMMSS/`

### Backup Commands (Generic)

```bash
pg_dump -Fc -h <DB_HOST_PLACEHOLDER> -U <DB_USER_PLACEHOLDER> -d <DB_NAME_PLACEHOLDER> -f nfl_analytics.dump
tar -czf ml_models.tar.gz ml/models/
aws s3 cp nfl_analytics.dump s3://<S3_BUCKET_PLACEHOLDER>/ec2-backups/<TIMESTAMP_PLACEHOLDER>/
aws s3 cp ml_models.tar.gz s3://<S3_BUCKET_PLACEHOLDER>/ec2-backups/<TIMESTAMP_PLACEHOLDER>/
```

### Restore Commands (Generic)

```bash
pg_restore -h <DB_HOST_PLACEHOLDER> -U <DB_USER_PLACEHOLDER> -d <DB_NAME_PLACEHOLDER> --clean --if-exists nfl_analytics.dump
tar -xzf ml_models.tar.gz -C .
```

## Security Posture (Documentation-Level)

- Secrets are environment-managed.
- Infrastructure identifiers and credentials are intentionally redacted in public-facing docs.
- Documentation should use placeholders only for hosts, account IDs, buckets, passwords, and keys.
