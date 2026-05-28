# TA-032 Rate Limiting Evidence

Date: 2026-05-28
Owner: GitHub Copilot (Developer)
Ticket: TA-032
Scope: Rate limiting on Flask API

## Summary
- Added request rate limiting to the Flask API using Flask-Limiter.
- Configured proxy-aware client-key resolution using `X-Forwarded-For` fallback to `request.remote_addr`.
- Exempted `/health` from rate limiting to keep monitoring and readiness probes stable.
- Implemented JSON 429 responses with deterministic `Retry-After` fallback support.

## Policy Implemented
- Default policy: `API_RATE_LIMIT_DEFAULT` (default value: `180 per minute`).
- Storage backend: `API_RATE_LIMIT_STORAGE_URI` (default value: `memory://`).
- Retry hint fallback: `API_RATE_LIMIT_RETRY_AFTER_SECONDS` (default value: `60`).
- Route exemption: `/health` via `@limiter.exempt`.

## Code Changes
- `api_server.py`
  - Added Flask-Limiter initialization and app binding.
  - Added `get_rate_limit_key()` for proxy-aware client identity.
  - Added `@app.errorhandler(RateLimitExceeded)` to return structured 429 responses.
  - Added fallback `Retry-After` response header behavior.
  - Exempted `/health` route from limiter enforcement.
- `requirements.txt`
  - Added `Flask-Limiter==3.8.0`.
- `requirements-py314.txt`
  - Added `Flask-Limiter`.
- `requirements-py314-lock.txt`
  - Added `Flask-Limiter==3.8.0`.

## Verification Commands
Executed with local workspace interpreter via Python snippet runner:

```python
import os
import importlib

os.environ['API_RATE_LIMIT_DEFAULT'] = '5 per minute'
os.environ['API_RATE_LIMIT_RETRY_AFTER_SECONDS'] = '42'

import api_server
importlib.reload(api_server)

client = api_server.app.test_client()
for _ in range(6):
    client.get('/api/teams')
resp = client.get('/api/teams')

print('status', resp.status_code)
print('retry_after', resp.headers.get('Retry-After'))
print('error', (resp.get_json() or {}).get('error'))
```

## Verification Output
```text
status 429
retry_after 42
error rate_limit_exceeded
```

## Acceptance Mapping
- Step 01: Defined policy defaults and exempted `/health` from limit enforcement.
- Step 02: Implemented limiter and safe defaults in Flask server configuration.
- Step 03: Verified deterministic 429 behavior and `Retry-After` header output.
- Step 04: Published this runbook-style evidence with policy, validation, and rollback notes.

## Rollback Notes
If rollback is required:
1. Remove limiter initialization and handler additions from `api_server.py`.
2. Remove `Flask-Limiter` from requirements files.
3. Restart API service and validate `/health` plus key endpoints.
4. Re-run the same snippet with low limit to confirm 429 no longer triggers.
