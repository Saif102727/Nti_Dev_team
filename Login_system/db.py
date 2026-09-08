"""
Database layer.
Responsible ONLY for connecting to SQLite and creating tables.
No authentication or business logic lives here.
"""

import sqlite3
from pathlib import Path

# The .db file will be created next to this script.
# Move this path if you want the database stored elsewhere in your project
# (e.g. a top-level "data/" folder).
DB_PATH = Path(__file__).resolve().parent / "app_data.db"


def get_connection() -> sqlite3.Connection:
    """
    Returns a new SQLite connection.
    row_factory lets us access columns by name (row["name"]) instead of index.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """
    Creates the required tables if they don't already exist.
    Safe to call every time the app starts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            university TEXT,
            faculty TEXT,
            certificate TEXT,
            completed_courses TEXT,      -- JSON dict, e.g. {"CS101": "A"}
            enrolled_courses TEXT,       -- JSON list, e.g. ["CS201", "MATH202"]
            preferred_study_location TEXT,
            daily_study_hours TEXT,      -- JSON dict, e.g. {"Sunday": 3, ...}
            free_days TEXT,              -- JSON list, e.g. ["Friday", "Saturday"]
            points INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            student_id TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)

    conn.commit()
    conn.close()
