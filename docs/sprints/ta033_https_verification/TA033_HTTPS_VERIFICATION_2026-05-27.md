# TA-033 HTTPS Verification Evidence

Date: 2026-05-27
Owner: GitHub Copilot (Developer)
Ticket: TA-033
Scope: HTTPS confirmed - all traffic encrypted

## Summary
- Implemented proxy-aware HTTPS enforcement in the Flask API server.
- Added HSTS response header for HTTPS traffic in non-local environments.
- Switched ESPN live scoreboard upstream URL from HTTP to HTTPS.
- Verified behavior with Flask test client using forwarded-proto simulation.

## Code Changes
- api_server.py
  - Added `ProxyFix` middleware (`x_proto=1`, `x_host=1`).
  - Added `@app.before_request` HTTPS redirect guard for non-local traffic.
  - Added `@app.after_request` HSTS header on HTTPS responses.
  - Kept localhost development exempt from forced redirect.
- api_routes_live_scores.py
  - Updated `ESPN_SCOREBOARD_URL` to `https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard`.

## Mixed-Content Audit Notes
- Frontend image and external links already use HTTPS where applicable.
- No hardcoded `http://` API base URLs found in frontend route fetch logic.
- API calls are derived from `REACT_APP_API_URL` and relative endpoint joins.

## Verification Commands
Executed via Python snippet runner against local workspace interpreter:

```python
from api_server import app

client = app.test_client()

r_redirect = client.get('/health', headers={
    'Host': 'nfl.aprilsykes.dev',
    'X-Forwarded-Host': 'nfl.aprilsykes.dev',
    'X-Forwarded-Proto': 'http'
}, follow_redirects=False)

r_hsts = client.get('/health', headers={
    'Host': 'nfl.aprilsykes.dev',
    'X-Forwarded-Host': 'nfl.aprilsykes.dev',
    'X-Forwarded-Proto': 'https'
}, follow_redirects=False)

r_local = client.get('/health', headers={'Host': '127.0.0.1:5000'}, follow_redirects=False)

print('redirect_status', r_redirect.status_code)
print('redirect_location', r_redirect.headers.get('Location'))
print('hsts_header', r_hsts.headers.get('Strict-Transport-Security'))
print('local_status', r_local.status_code)
print('local_location', r_local.headers.get('Location'))
```

## Verification Output
```text
redirect_status 301
redirect_location https://nfl.aprilsykes.dev/health
hsts_header max-age=31536000; includeSubDomains
local_status 200
local_location None
```

## Acceptance Mapping
- Step 01: Verified redirect behavior and HTTPS transport enforcement for non-local traffic.
- Step 02: Audited for mixed-content risks and removed upstream HTTP ESPN endpoint.
- Step 03: Re-tested API request behavior under HTTP/HTTPS forwarded-proto scenarios.
- Step 04: Published this timestamped evidence bundle with commands and outputs.
