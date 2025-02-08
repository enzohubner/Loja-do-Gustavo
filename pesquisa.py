import psycopg2
from db import cursor, conn

# Get all table names
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
""")
tables = cursor.fetchall()

# For each table, get its columns
for table in tables:
    table_name = table[0]
    cursor.execute(f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = '{table_name}'
    """)
    columns = cursor.fetchall()
    
    print(f"\nTable: {table_name}")
    for column in columns:
        print(f"  Column: {column[0]}, Type: {column[1]}")