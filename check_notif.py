import sqlite3

conn = sqlite3.connect('restaurant.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM notifications")
for row in cursor.fetchall():
    print(row)
conn.close()