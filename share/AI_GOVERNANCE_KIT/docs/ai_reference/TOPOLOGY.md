# TOPOLOGY

## Environment Map

### Local
- Host: localhost
- Frontend: <url>
- API: <url>
- Database: <host:port>

### Test/Staging
- Host/IP: <value>
- Access method: <ssh/vpn/etc>
- Service name: <value>

### Production
- Host/IP: <value>
- Access method: <ssh/vpn/etc>
- Service name: <value>

## Source Control Flow
- Main branch: <branch>
- Test branch: <branch>
- Merge policy: <policy>

## Deployment Flow
1. Local development and verification.
2. Test deployment and validation.
3. Production deployment.

## Notes
- Startup lock is environment-agnostic.
- Runtime snapshot reflects whichever environment is currently active.
