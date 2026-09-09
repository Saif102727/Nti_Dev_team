"""
Login diagnostic tool.

Run this on your OWN machine (where app_data.db actually lives) to find out
EXACTLY why a login is failing, instead of guessing.

Usage:
    python diagnose_login.py                  -> lists what's in the database
    python diagnose_login.py <username>        -> checks if that username exists
    python diagnose_login.py <username> <pass> -> full step-by-step auth check

Nothing here writes to the database. It's 100% read-only / diagnostic.
"""

import sys

from db import get_connection, init_db, DB_PATH
from security import verify_password


def show_overview():
    print(f"Database file: {DB_PATH}")
    print(f"Exists on disk: {DB_PATH.exists()}\n")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS c FROM students")
    student_count = cursor.fetchone()["c"]

    cursor.execute("SELECT COUNT(*) AS c FROM users")
    user_count = cursor.fetchone()["c"]

    print(f"students table: {student_count} row(s)")
    print(f"users table:    {user_count} row(s)\n")

    if user_count == 0:
        print(
            "⚠️  No users at all. Nobody can log in yet because no account "
            "was ever created in THIS database file.\n"
            "   -> Go create an account first from the 'Create account' tab, "
            "or run bulk_register.py.\n"
        )
        conn.close()
        return

    cursor.execute("SELECT username FROM users ORDER BY username")
    usernames = [row["username"] for row in cursor.fetchall()]

    print("Registered usernames currently in this database:")
    for name in usernames[:30]:
        print(f"  - {name!r}")
    if len(usernames) > 30:
        print(f"  ... and {len(usernames) - 30} more")

    conn.close()


def check_username(username: str):
    conn = get_connection()
    cursor = conn.cursor()

    # Exact match (this is what authenticate() actually does)
    cursor.execute(
        "SELECT username, student_id FROM users WHERE username = ?",
        (username.strip(),),
    )
    exact = cursor.fetchone()

    if exact:
        print(f"✅ Exact match found for username {username.strip()!r} "
              f"(student_id={exact['student_id']}).")
    else:
        print(f"❌ No exact match for {username.strip()!r}.")

        # Case-insensitive match, to catch a common mismatch
        cursor.execute(
            "SELECT username FROM users WHERE LOWER(username) = LOWER(?)",
            (username.strip(),),
        )
        ci_match = cursor.fetchone()
        if ci_match:
            print(
                f"   ↳ But a DIFFERENT-CASE username exists: "
                f"{ci_match['username']!r}. Usernames are matched "
                f"case-sensitively, so this counts as a different account. "
                f"Try logging in with the exact casing above."
            )
        else:
            print(
                "   ↳ And no case-insensitive match either — this username "
                "genuinely was never registered in this database file."
            )

    conn.close()
    return bool(exact)


def check_password(username: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password_hash, salt FROM users WHERE username = ?",
        (username.strip(),),
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return  # already reported by check_username

    ok = verify_password(password, row["salt"], row["password_hash"])

    if ok:
        print("✅ Password matches. authenticate() should succeed with "
              "these exact values.")
    else:
        print("❌ Password does NOT match the stored hash.")
        if password != password.strip():
            print(
                "   ↳ Heads up: your password has leading/trailing spaces. "
                "register()/authenticate() never strip passwords on purpose "
                "(spaces can be a valid part of a password), so a stray "
                "space from copy-pasting will silently break the login."
            )


def main():
    init_db()  # safe no-op if tables already exist

    args = sys.argv[1:]

    if len(args) == 0:
        show_overview()
    elif len(args) == 1:
        check_username(args[0])
    elif len(args) == 2:
        username, password = args
        found = check_username(username)
        if found:
            check_password(username, password)
    else:
        print("Usage: python diagnose_login.py [username] [password]")


if __name__ == "__main__":
    main()
