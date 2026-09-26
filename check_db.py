import sqlite3

conn = sqlite3.connect('restaurant.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:")
for t in tables:
    print(f"  - {t[0]}")

# Check notifications count
try:
    cursor.execute("SELECT COUNT(*) FROM notifications")
    count = cursor.fetchone()[0]
    print(f"\nNotifications count: {count}")
except Exception as e:
    print(f"\nError: {e}")

conn.close()