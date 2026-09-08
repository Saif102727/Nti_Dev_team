"""
Authentication service.

This is the ONLY file that matters for "the login system".
It has no print(), no input(), and no knowledge of any UI.
It just takes arguments and returns data, or raises an exception.

This means the exact same functions can be called from:
- a CLI test script (cli_test.py, for now)
- a Streamlit app (later)
without changing a single line in here.
"""

import json
import sqlite3
import uuid

from db import get_connection
from security import generate_salt, hash_password, verify_password

MIN_PASSWORD_LENGTH = 6


# ==========================================
# Custom Exceptions
# ==========================================

class AuthError(Exception):
    """Base class for all authentication-related errors."""


class UsernameTakenError(AuthError):
    """Raised when the chosen username already exists."""


class WeakPasswordError(AuthError):
    """Raised when the password does not meet minimum requirements."""


class InvalidCredentialsError(AuthError):
    """
    Raised when username/password don't match.
    Intentionally generic — it never reveals whether the username
    exists or the password was wrong, to avoid leaking account info.
    """


# ==========================================
# Register
# ==========================================

def register(
    username: str,
    password: str,
    name: str,
    age: int,
    university: str,
    faculty: str,
    certificate: str,
    student_id: str = None,
    daily_study_hours: dict = None,
    free_days: list = None,
    preferred_study_location: str = "Home",
) -> str:
    """
    Creates a new student record + a linked user account.

    daily_study_hours / free_days / preferred_study_location let the
    GUI collect the student's weekly availability at sign-up time so
    the study planner has real data to work with immediately. They
    all have sensible defaults so existing callers (e.g. cli_test.py)
    keep working unchanged.

    Returns the newly created student_id.
    Raises UsernameTakenError or WeakPasswordError on failure.
    """
    username = username.strip()
    if not username:
        raise AuthError("Username cannot be empty.")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise WeakPasswordError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        )

    if student_id is None:
        student_id = f"STU-{uuid.uuid4().hex[:8].upper()}"

    if not isinstance(daily_study_hours, dict):
        daily_study_hours = {}

    if not isinstance(free_days, list):
        free_days = []

    if not preferred_study_location:
        preferred_study_location = "Home"

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT 1 FROM users WHERE username = ?", (username,)
        )
        if cursor.fetchone() is not None:
            raise UsernameTakenError("This username is already taken.")

        # Student record starts with sensible defaults for the fields
        # that aren't collected at registration time. These can be
        # filled in later from the profile screen.
        cursor.execute(
            """
            INSERT INTO students (
                student_id, name, age, university, faculty, certificate,
                completed_courses, enrolled_courses,
                preferred_study_location, daily_study_hours,
                free_days, points
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student_id, name, age, university, faculty, certificate,
                json.dumps({}), json.dumps([]),
                preferred_study_location, json.dumps(daily_study_hours),
                json.dumps(free_days), 0,
            ),
        )

        salt = generate_salt()
        password_hash = hash_password(password, salt)

        cursor.execute(
            """
            INSERT INTO users (username, password_hash, salt, student_id)
            VALUES (?, ?, ?, ?)
            """,
            (username, password_hash, salt, student_id),
        )

        conn.commit()
        return student_id

    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


# ==========================================
# Authenticate
# ==========================================

def authenticate(username: str, password: str) -> dict:
    """
    Verifies a username/password pair.

    Returns a dict with the student's data on success.
    Raises InvalidCredentialsError on any failure (unknown username
    or wrong password — same error either way, on purpose).
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT users.password_hash, users.salt, students.*
            FROM users
            JOIN students ON users.student_id = students.student_id
            WHERE users.username = ?
            """,
            (username.strip(),),
        )
        row = cursor.fetchone()

        if row is None:
            raise InvalidCredentialsError("Invalid username or password.")

        if not verify_password(password, row["salt"], row["password_hash"]):
            raise InvalidCredentialsError("Invalid username or password.")

        return {
            "student_id": row["student_id"],
            "name": row["name"],
            "age": row["age"],
            "university": row["university"],
            "faculty": row["faculty"],
            "certificate": row["certificate"],
            "completed_courses": json.loads(row["completed_courses"]),
            "enrolled_courses": json.loads(row["enrolled_courses"]),
            "preferred_study_location": row["preferred_study_location"],
            "daily_study_hours": json.loads(row["daily_study_hours"]),
            "free_days": json.loads(row["free_days"]),
            "points": row["points"],
        }

    finally:
        conn.close()


# ==========================================
# Persist progress (called from the GUI)
# ==========================================

def update_points(student_id: str, points: int) -> None:
    """
    Persists the student's current reward-points total to the
    database. Called from the Streamlit app whenever points change
    (finishing a study session, buying a shop item, ...) so progress
    survives logging out and back in.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE students SET points = ? WHERE student_id = ?",
            (max(0, int(points or 0)), student_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_daily_study_hours(student_id: str, daily_study_hours: dict) -> None:
    """Persists an updated weekly study-hours schedule for the student."""
    if not isinstance(daily_study_hours, dict):
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE students SET daily_study_hours = ? WHERE student_id = ?",
            (json.dumps(daily_study_hours), student_id),
        )
        conn.commit()
    finally:
        conn.close()
