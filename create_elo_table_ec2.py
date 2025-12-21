#!/usr/bin/env python3
"""Create Elo predictions table on EC2"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "nfl_analytics"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost")
)

cursor = conn.cursor()

sql = open("create_elo_predictions_table.sql").read()
cursor.execute(sql)
conn.commit()

print("✅ Successfully created hcl.ml_predictions_elo table")

cursor.close()
conn.close()
