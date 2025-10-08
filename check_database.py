import sqlite3

conn = sqlite3.connect('data/nfl_teams.db')
cursor = conn.cursor()

print("\nDATABASE TABLE STRUCTURE:")
print("="*60)
cursor.execute("PRAGMA table_info(teams)")
for row in cursor.fetchall():
    print(row)

print("\nTOP 5 TEAMS IN DATABASE:")
print("="*60)
cursor.execute("SELECT name, ppg, pa FROM teams ORDER BY ppg DESC LIMIT 5")
for row in cursor.fetchall():
    print(f"{row[0]:30} PPG: {row[1]:5.1f}  PA: {row[2]:5.1f}")

print("\nTOTAL ROWS:")
cursor.execute("SELECT COUNT(*) FROM teams")
print(f"Teams in database: {cursor.fetchone()[0]}")

conn.close()
