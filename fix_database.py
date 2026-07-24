import sqlite3

# Connect to your database
conn = sqlite3.connect('database/nutifa.db')
cursor = conn.cursor()

# 1. Update platform name to Hajilala
cursor.execute("UPDATE settings SET value = 'Hajilala' WHERE key = 'platform_name'")
print("✅ Platform name updated to Hajilala")

# 2. Update admin email
cursor.execute("UPDATE users SET email = 'admin@hajilala.music' WHERE email = 'admin@nutifa.music'")
print("✅ Admin email updated to admin@hajilala.music")

# 3. (Optional) Update any other references – check if any other fields contain 'nutifa'
cursor.execute("SELECT key FROM settings WHERE value LIKE '%nutifa%'")
rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"⚠️ Found another setting with 'nutifa': {row[0]}")
        # You can update them manually if needed

# Commit changes
conn.commit()

# Verify
cursor.execute("SELECT value FROM settings WHERE key = 'platform_name'")
platform = cursor.fetchone()[0]
print(f"✅ Verification: Platform Name = {platform}")

cursor.execute("SELECT email FROM users WHERE role = 'admin'")
admin_email = cursor.fetchone()[0]
print(f"✅ Verification: Admin Email = {admin_email}")

conn.close()
print("\n🎉 Database is now fully rebranded to Hajilala!")