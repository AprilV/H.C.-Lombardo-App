# TA-016 Production Probe Auto-Status

Generated UTC: 2026-06-02T04:13:50.817398+00:00

## Summary
- any_reachable: false
- all_reachable: false
- blocked: true
- blocking_reason: No configured production endpoint returned HTTP 200 from current environment.

## Endpoint Results
- url=http://34.198.25.249:5000/health ok=false status_code=None elapsed_ms=20016 error=HTTPConnectionPool(host='34.198.25.249', port=5000): Max retries exceeded with url: /health (Caused by ConnectTimeoutError(<HTTPConnection(host='34.198.25.249', port=5000) at 0x27dc1f34c20>, 'Connection to 34.198.25.249 timed out. (connect timeout=20.0)'))
- url=https://api.aprilsykes.dev/health ok=false status_code=None elapsed_ms=20202 error=HTTPSConnectionPool(host='api.aprilsykes.dev', port=443): Max retries exceeded with url: /health (Caused by ConnectTimeoutError(<HTTPSConnection(host='api.aprilsykes.dev', port=443) at 0x27dc1f35400>, 'Connection to api.aprilsykes.dev timed out. (connect timeout=20.0)'))
