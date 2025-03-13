import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Check if table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
table_exists = cursor.fetchone()

if table_exists:
    print("✅ Table 'users' exists!")

    # Print existing users
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for user in users:
        print(user)
else:
    print("❌ Table 'users' does NOT exist!")

conn.close()
