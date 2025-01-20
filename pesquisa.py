import psycopg2
from db import cursor, conn


# Show table data
cursor.execute('SELECT * FROM produtos')
rows = cursor.fetchall()

print("\nTable data:")
# Show existing data
for row in rows:
    print(row)
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'usuarios'")
    columns = cursor.fetchall()
    print("\nColumns in usuarios table:")
    for column in columns:
        print(column[0])