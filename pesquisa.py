import psycopg2

from db import cursor, conn
cursor.execute("SELECT * FROM usuarios")

rows = cursor.fetchall()
print(rows)
for row in rows:
    column1 = row[0]
    column2 = row[1]
    column3 = row[2]
    column4 = row[3]
    print(column1, column2, column3, column4)

conn.commit()  
cursor.close()
conn.close()