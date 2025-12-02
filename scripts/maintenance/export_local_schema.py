#!/usr/bin/env python3
"""
Export the LOCAL database schema to SQL file
This captures the CORRECT schema with EPA columns
"""
import psycopg2

LOCAL_CONN = {
    'dbname': 'nfl_analytics',
    'user': 'postgres',
    'password': 'aprilv120',
    'host': 'localhost',
    'port': '5432'
}

print("Exporting LOCAL schema to SQL file...")

conn = psycopg2.connect(**LOCAL_CONN)
cur = conn.cursor()

# Get the CREATE TABLE statements
cur.execute("""
    SELECT 
        'CREATE TABLE IF NOT EXISTS hcl.' || table_name || ' (' || 
        string_agg(
            column_name || ' ' || 
            CASE 
                WHEN data_type = 'character varying' THEN 'VARCHAR(' || character_maximum_length || ')'
                WHEN data_type = 'numeric' THEN 'NUMERIC(' || numeric_precision || ',' || numeric_scale || ')'
                WHEN data_type = 'timestamp with time zone' THEN 'TIMESTAMPTZ'
                WHEN data_type = 'timestamp without time zone' THEN 'TIMESTAMP'
                WHEN data_type = 'double precision' THEN 'DOUBLE PRECISION'
                ELSE UPPER(data_type)
            END ||
            CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END ||
            CASE WHEN column_default IS NOT NULL THEN ' DEFAULT ' || column_default ELSE '' END,
            ', '
        ) || ');' as create_statement,
        table_name
    FROM information_schema.columns
    WHERE table_schema = 'hcl'
    GROUP BY table_name
    ORDER BY table_name;
""")

tables = cur.fetchall()

# Write to SQL file
with open('render_correct_schema.sql', 'w') as f:
    f.write("-- HCL Schema Export from LOCAL database (with EPA columns)\n")
    f.write("-- Generated: " + str(psycopg2.TimestampFromTicks(time.time())) + "\n\n")
    f.write("CREATE SCHEMA IF NOT EXISTS hcl;\n\n")
    
    for create_stmt, table_name in tables:
        f.write(f"-- Table: {table_name}\n")
        f.write("DROP TABLE IF EXISTS hcl." + table_name + " CASCADE;\n")
        f.write(create_stmt + "\n\n")
    
    # Add indexes
    f.write("-- Indexes\n")
    cur.execute("""
        SELECT indexdef || ';'
        FROM pg_indexes
        WHERE schemaname = 'hcl'
        ORDER BY tablename, indexname;
    """)
    for (idx,) in cur.fetchall():
        f.write(idx + "\n")

print("✅ Schema exported to: render_correct_schema.sql")

conn.close()
