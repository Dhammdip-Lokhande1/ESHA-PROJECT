"""
backend/scripts/migrate_roles.py

Safely migrates existing 'instructor' and 'student' user records in ehsa.db to 'user'.
Preserves user IDs, usernames, emails, password hashes, timestamps, and history.
Creates a timestamped backup before performing modifications.
Idempotent and safe to run multiple times.
"""

import os
import shutil
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ehsa.db")

def migrate_database():
    if not os.path.exists(DB_PATH):
        print(f"[SKIP] Database file not found at {DB_PATH}. No migration needed.")
        return

    # 1. Create a backup
    backup_filename = f"ehsa.db.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_path = os.path.join(os.path.dirname(DB_PATH), backup_filename)
    shutil.copy2(DB_PATH, backup_path)
    print(f"[BACKUP] Created database backup at: {backup_path}")

    # 2. Connect to SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("[INFO] 'users' table does not exist yet in database. No user migration needed.")
            return

        # Check current distribution of roles
        cursor.execute("SELECT id, username, email, role FROM users")
        users = cursor.fetchall()
        print(f"[INFO] Found {len(users)} users in database before migration:")
        for u_id, username, email, role in users:
            print(f"  - User: {username} ({email}) | Role: {role}")

        # Execute migration
        cursor.execute("UPDATE users SET role = 'user' WHERE role IN ('instructor', 'student')")
        migrated_count = cursor.rowcount
        conn.commit()

        print(f"[SUCCESS] Migrated {migrated_count} accounts to role 'user'.")

        # Verify updated roles
        cursor.execute("SELECT id, username, email, role FROM users")
        updated_users = cursor.fetchall()
        print(f"[INFO] Users after migration:")
        for u_id, username, email, role in updated_users:
            print(f"  - User: {username} ({email}) | Role: {role}")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
