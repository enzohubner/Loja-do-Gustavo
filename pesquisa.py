import psycopg2
from db import cursor, conn

# Delete all rows from the table
cursor.execute('DELETE FROM notificacoes')
conn.commit()  # Important: commit the changes

# Verify the table is empty
cursor.execute('SELECT * FROM notificacoes')
rows = cursor.fetchall()

print("\nTable data after deletion:")
for row in rows:
    print(row)
