"""
Bulk-registers the 100 students from dummy_data.json into the login system.

IMPORTANT MISMATCH TO KNOW ABOUT:
dummy_data.json (the Study Planner dataset) does NOT contain username,
password, age, university, faculty, or certificate. Those fields only exist
in the LOGIN system's Student model — the Study Planner schema never had
them. This script fills them in with placeholder/test values below so
register() has everything it needs. Change the DEFAULT_* constants if you
want different values.

CRITICAL: this script passes the student's EXISTING student_id (from
dummy_data.json) into register(), instead of letting register() generate
a random new one. This is what keeps the login system's student record and
the Study Planner's per-student data (courses, constraints, preferences...)
pointing at the same student_id. Skip this and you'll end up with two
disconnected ID spaces that can't be joined together later.

Run:
    python bulk_register.py

Produces:
    - app_data.db populated with 100 students + 100 user accounts
    - generated_credentials.json -> the username/password created for each
      student, since randomly-registered accounts are unusable for testing
      if nobody knows their login
"""

import json
from pathlib import Path

from db import init_db
from auth_service import register, UsernameTakenError, WeakPasswordError, AuthError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STUDENTS_JSON_PATH = PROJECT_ROOT / "data" / "dummy_data.json"
CREDENTIALS_OUTPUT_PATH = Path(__file__).resolve().parent / "generated_credentials.json"

# Placeholders for fields dummy_data.json doesn't contain.
DEFAULT_AGE = 20
DEFAULT_UNIVERSITY = "Placeholder University"
DEFAULT_FACULTY = "Computer & Communications Engineering"
DEFAULT_CERTIFICATE = "Thanaweya Amma"
DEFAULT_PASSWORD = "Test1234"  # same password for every test account, on purpose
DEFAULT_EMAIL_DOMAIN = "example.com"


def slugify_name(name: str) -> str:
    return name.strip().lower().replace(" ", ".")


def make_unique_username(name: str, used_usernames: set) -> str:
    base = slugify_name(name)
    username = base
    counter = 1
    while username in used_usernames:
        counter += 1
        username = f"{base}{counter}"
    used_usernames.add(username)
    return username


def main():
    init_db()

    with open(STUDENTS_JSON_PATH, "r", encoding="utf-8") as f:
        students = json.load(f)

    used_usernames = set()
    credentials = []
    failures = []

    for student in students:
        student_id = student["student_id"]
        name = student["name"]
        username = make_unique_username(name, used_usernames)
        
        email = f"{username}@{DEFAULT_EMAIL_DOMAIN}"

        try:
            register(
                username=username,
                password=DEFAULT_PASSWORD,
                name=name,
                age=DEFAULT_AGE,
                university=DEFAULT_UNIVERSITY,
                faculty=DEFAULT_FACULTY,
                certificate=DEFAULT_CERTIFICATE,
                email=email,
                student_id=student_id,  # reuse the ID from dummy_data.json
            )
            credentials.append({
                "student_id": student_id,
                "name": name,
                "username": username,
                "password": DEFAULT_PASSWORD,
                "email": email,
            })
        except (UsernameTakenError, WeakPasswordError, AuthError, TypeError) as error:
            failures.append({
                "student_id": student_id,
                "name": name,
                "error": str(error),
            })

    with open(CREDENTIALS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(credentials, f, indent=2, ensure_ascii=False)

    print(f"Registered {len(credentials)} students successfully.")
    print(f"Credentials saved to {CREDENTIALS_OUTPUT_PATH}")

    if failures:
        print(f"\n{len(failures)} failed:")
        for failure in failures:
            print(f"  - {failure['student_id']} ({failure['name']}): {failure['error']}")


if __name__ == "__main__":
    main()