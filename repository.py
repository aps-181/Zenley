import sqlite3
from datetime import datetime

# Define database path (make sure it matches your setup)
DB_PATH = "/app/db/zenley.db"


def initalize_user_session(users):
    """Insert users into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for user in users:
        print("Member name: ",user["real_name"],end="\n")
        user_id = user["id"]
        try:
            cursor.execute("""
                INSERT INTO users_sessions (user_id, session_start_time, session_end_time, is_active) 
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO NOTHING
            """, (user_id, None, None, False))  # Default session values

        except sqlite3.Error as e:
            print(f"Error inserting user {user_id}: {e}")

    conn.commit()
    conn.close()
    print(f"Inserted {len(users)} users into the database.")


def fetch_all_user_sessions():
    """Fetch all users and their session data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, session_start_time, session_end_time, is_active 
        FROM users_sessions
    """)

    users = cursor.fetchall()  # Fetch all rows
    conn.close()

    return [
        {
            "user_id": user[0],
            "session_start_time": datetime.strptime(user[1], "%Y-%m-%d %H:%M:%S.%f") if user[1] else None,
            "session_end_time": datetime.strptime(user[2], "%Y-%m-%d %H:%M:%S.%f") if user[2] else None,
            "is_active": bool(user[3])
        }
        for user in users
    ]

    
def update_user_sessions(users_data):
    """Batch update session data for multiple users while keeping user_id constant."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        for user in users_data:
            user_id = user["user_id"]  # Always stays the same
            session_start = user["session_start_time"]
            session_end = user["session_end_time"]
            is_active = user["is_active"]

            # ✅ Update only the session data while keeping user_id constant
            cursor.execute("""
                UPDATE users_sessions 
                SET session_start_time = ?, session_end_time = ?, is_active = ?
                WHERE user_id = ?
            """, (session_start, session_end, is_active, user_id))

        conn.commit()  # ✅ Save all changes at once
        print(f"Updated {len(users_data)} user sessions.")

    except sqlite3.Error as e:
        conn.rollback()  # ❌ Rollback on error
        print(f"Database error: {e}")

    finally:
        conn.close()

