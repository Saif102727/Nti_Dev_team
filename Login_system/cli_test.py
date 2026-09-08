"""
Temporary command-line wrapper, just to test the auth system
before the GUI exists.

This file is disposable — none of the real logic is here.
When the Streamlit GUI is ready, this file can be deleted
and auth_service.py will be called from there instead.
"""

from db import init_db
from auth_service import (
    register,
    authenticate,
    UsernameTakenError,
    WeakPasswordError,
    InvalidCredentialsError,
    AuthError,
)


def run_register() -> None:
    print("\n--- Register ---")
    username = input("Choose a username: ")
    password = input("Choose a password: ")
    name = input("Full name: ")

    try:
        age = int(input("Age: "))
    except ValueError:
        print("Age must be a number.")
        return

    university = input("University: ")
    faculty = input("Faculty: ")
    certificate = input("Certificate: ")

    try:
        student_id = register(
            username, password, name, age, university, faculty, certificate
        )
        print(f"Account created. Your student ID is: {student_id}")
    except (UsernameTakenError, WeakPasswordError, AuthError) as error:
        print(f"Registration failed: {error}")


def run_login() -> None:
    print("\n--- Login ---")
    username = input("Username: ")
    password = input("Password: ")

    try:
        student = authenticate(username, password)
        print(f"Welcome back, {student['name']}! (ID: {student['student_id']})")
        print(f"Points: {student['points']}")
    except InvalidCredentialsError as error:
        print(f"Login failed: {error}")


def main() -> None:
    init_db()

    while True:
        print("\n1) Register\n2) Login\n3) Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            run_register()
        elif choice == "2":
            run_login()
        elif choice == "3":
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
