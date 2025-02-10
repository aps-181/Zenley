import sqlite3
import os

# Define database path
DB_DIR = "/app/db"
os.makedirs(DB_DIR, exist_ok=True)  # Ensure the directory exists
DB_PATH = os.path.join(DB_DIR, "zenley.db")

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create a migrations table to track applied migrations
cursor.execute("""
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_name TEXT UNIQUE,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# List of migration scripts (prevent running them multiple times)
migrations = [
    {
        "name": "create_users_sessions_table",
        "query": """
        CREATE TABLE IF NOT EXISTS users_sessions (
            user_id TEXT PRIMARY KEY, 
            session_start_time DATETIME,
            session_end_time DATETIME,
            is_active BOOLEAN
        )
        """
    }
]

# Apply migrations if not already applied
for migration in migrations:
    cursor.execute("SELECT 1 FROM migrations WHERE migration_name = ?", (migration["name"],))
    if not cursor.fetchone():  # Migration not applied
        cursor.execute(migration["query"])  # Run the SQL
        cursor.execute("INSERT INTO migrations (migration_name) VALUES (?)", (migration["name"],))

# Commit and close
conn.commit()
conn.close()

print("Database migrations applied successfully!")
