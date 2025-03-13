import sqlite3

db_path = "users.db"

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insert sample users (Modify as needed)
users = [
    ("STU001", "Rahul Sharma", "Student"),
    ("STU002", "Ananya Reddy", "Student"),
    ("STU003", "Karthik Rao", "Student"),
    ("EMP001", "Amit Kumar", "Employee"),
    ("EMP002", "Priya Singh", "Employee")
]

# Insert users if they do not exist
for user in users:
    cursor.execute("INSERT OR IGNORE INTO users (user_id, name, role) VALUES (?, ?, ?)", user)

# Commit and close
conn.commit()
conn.close()

print("✅ Sample users added successfully!")
