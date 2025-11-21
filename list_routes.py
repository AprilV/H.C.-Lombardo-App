"""List all Flask routes to debug route registration"""
import sys
sys.path.insert(0, 'c:\\IS330\\H.C Lombardo App')

from api_server import app

print("\n=== ALL REGISTERED ROUTES ===\n")
for rule in app.url_map.iter_rules():
    methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    print(f"{rule.endpoint:40s} {methods:20s} {rule.rule}")

print("\n=== ROUTES MATCHING '/teams' ===\n")
for rule in app.url_map.iter_rules():
    if 'teams' in rule.rule:
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"{rule.endpoint:40s} {methods:20s} {rule.rule}")
