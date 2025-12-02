"""SSH into EC2 and check what's actually there"""
import subprocess
import sys

print("\n" + "="*100)
print("EC2 DATABASE CHECK - What does the LIVE system have?")
print("="*100)

# SSH command to check EC2 database
ssh_cmd = """
ssh -i ~/.ssh/ec2_key.pem ubuntu@34.198.25.249 << 'EOF'
cd /home/ubuntu/H.C.-Lombardo-App
source venv/bin/activate

python3 << 'PYTHON'
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    database='nfl_analytics',
    user='nfl_user',
    password='nfl2024',
    port='5432'
)
cur = conn.cursor()

print("\n1. LATEST WEEK:")
cur.execute("SELECT MAX(week) FROM hcl.games WHERE season = 2025 AND home_score IS NOT NULL")
print(f"   Week {cur.fetchone()[0]}")

print("\n2. WEEK 13 TEAMS:")
cur.execute("SELECT COUNT(DISTINCT team) FROM hcl.team_game_stats WHERE season = 2025 AND week = 13")
print(f"   {cur.fetchone()[0]}/32 teams")

print("\n3. WEEK 13 EPA:")
cur.execute("SELECT COUNT(*) FROM hcl.team_game_stats WHERE season = 2025 AND week = 13 AND epa_per_play IS NOT NULL")
print(f"   {cur.fetchone()[0]}/32 have EPA stats")

print("\n4. SAMPLE (KC Week 13):")
cur.execute("SELECT points, epa_per_play, success_rate FROM hcl.team_game_stats WHERE season = 2025 AND week = 13 AND team = 'KC'")
pts, epa, sr = cur.fetchone()
print(f"   Points: {pts}, EPA: {epa}, Success Rate: {sr}")

conn.close()
PYTHON
EOF
"""

print("\nConnecting to EC2 to check database...")
print("(This requires SSH key at ~/.ssh/ec2_key.pem)")
print("="*100)

result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print("="*100)
