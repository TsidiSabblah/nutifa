import sqlite3

conn = sqlite3.connect('database/nutifa.db')
conn.execute("UPDATE settings SET value = 'Hajilala' WHERE key = 'platform_name'")
conn.commit()
print("✅ Platform name updated to Hajilala")
conn.close()