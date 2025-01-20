import psycopg2
from db import cursor, conn


# Show table data
cursor.execute('SELECT * FROM produtos')
rows = cursor.fetchall()

print("\nTable data:")
# Show existing data
for row in rows:
    print(row)
