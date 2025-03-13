import sqlite3

# Connect to (or create) the users database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create the users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        name TEXT,
        role TEXT CHECK(role IN ('Employee', 'Student'))
    )
''')

# Insert test users (only if table is empty)
cursor.execute("SELECT COUNT(*) FROM users")
if cursor.fetchone()[0] == 0:
    users_data = [
        ("EMP001", "John Doe", "Employee"),
        ("STU001", "Alice Smith", "Student"),
        ("EMP002", "Jane Doe", "Employee"),
        ("STU002", "Bob Brown", "Student")
    ]
    cursor.executemany("INSERT INTO users (user_id, name, role) VALUES (?, ?, ?)", users_data)
    conn.commit()
    print("✅ Users table created and test data inserted!")

conn.close()