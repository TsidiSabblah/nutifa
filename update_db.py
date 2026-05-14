import sqlite3

# Connect to local database
conn = sqlite3.connect('database/nutifa.db')
cursor = conn.cursor()

# Add new columns
try:
    cursor.execute("ALTER TABLE tracks ADD COLUMN copyright_certified_at TEXT DEFAULT NULL")
    print("✅ Added copyright_certified_at column")
except Exception as e:
    print(f"⚠️ copyright_certified_at already exists or error: {e}")

try:
    cursor.execute("ALTER TABLE tracks ADD COLUMN copyright_certified_ip TEXT DEFAULT NULL")
    print("✅ Added copyright_certified_ip column")
except Exception as e:
    print(f"⚠️ copyright_certified_ip already exists or error: {e}")

conn.commit()
conn.close()
print("Database update complete!")