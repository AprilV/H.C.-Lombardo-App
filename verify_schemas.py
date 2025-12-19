#!/usr/bin/env python3
"""Verify both production and test schemas have data"""
import psycopg2
from db_config import DATABASE_CONFIG

conn = psycopg2.connect(**DATABASE_CONFIG)
cur = conn.cursor()

cur.execute('SELECT COUNT(*) FROM hcl.games WHERE season=2025')
prod = cur.fetchone()[0]

cur.execute('SELECT COUNT(*) FROM hcl_test.games WHERE season=2025')
test = cur.fetchone()[0]

print(f'✅ PRODUCTION (hcl): {prod} games')
print(f'✅ TEST (hcl_test): {test} games')

cur.close()
conn.close()
