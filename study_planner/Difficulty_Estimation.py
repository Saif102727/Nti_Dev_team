"""
Difficulty Estimation
======================

Estimates the effective difficulty of a course for a specific student by
blending the course's base difficulty with how hard the student found its
prerequisites (weighted by how strongly each prerequisite influences the
new course).

The student is selected using the student_id received from authentication.
"""

import json
from pathlib import Path
from Login_systemV2 import auth_service

DEFAULT_DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "dummy_data.json"

def calculate_difficulty(base_difficulty, prerequisites, w=0.6):
    """
    Formula:

    D_C = (1 - w) * B_C
          + w * (sum(D_i * R_i) / sum(R_i))

    B_C = base course difficulty
    D_i = student's personal difficulty in prerequisite
    R_i = influence of prerequisite
    w   = weight given to prerequisite history
    """

    if not prerequisites:
        return base_difficulty

    weighted_sum = 0
    influence_sum = 0

    for prerequisite in prerequisites.values():

        difficulty = prerequisite["personal_difficulty"]
        influence = prerequisite["influence"]

        weighted_sum += difficulty * influence
        influence_sum += influence

    prerequisite_difficulty = weighted_sum / influence_sum

    final_difficulty = (
        (1 - w) * base_difficulty
        + w * prerequisite_difficulty
    )

    return final_difficulty


def estimate_student_difficulties(student):
    """
    Calculate the personalized difficulty of every course
    belonging to the selected student.
    """

    courses = {}

    for course_name, course_data in student["courses"].items():

        difficulty = calculate_difficulty(
            course_data["base_difficulty"],
            course_data["completed_prerequisites"]
        )

        courses[course_name] = course_data.copy()

        courses[course_name]["difficulty"] = difficulty

    return courses


def load_students(filename=None):
    """
    Load Group A's student data.
    """

    path = filename or DEFAULT_DATA_FILE

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_student(students, student_id):
    """
    Find the student whose student_id matches the ID received
    from authentication.
    """

    for student in students:

        if student["student_id"] == student_id:
            return student

    raise ValueError(
        f"Student {student_id} was not found."
    )


def estimate_difficulties_for_student(student_id):
    """
    Main Task 1 function for integration with authentication.

    Receives the authenticated student's ID, finds that student
    in Group A's dummy data, and calculates their course difficulties.
    """

    students = load_students()

    student = get_student(
        students,
        student_id
    )

    difficulties = estimate_student_difficulties(student)

    return student, difficulties

# ==========================================================
# REAL-DATA INTEGRATION
# ==========================================================
#
# Everything above this point is Group A's original Task 1 code,
# built around data/dummy_data.json (one student_id -> a "courses"
# dict with base_difficulty / completed_prerequisites per course).
#
# The live app doesn't have that per-student shape: real students
# come from Login_systemV2.auth_service (a SQLite row -> completed
# course IDs only, no personal grade per prerequisite), and the
# course catalog comes from loader.load_courses_and_events() (a list
# of model.py Course objects shared by every student). The functions
# below adapt that real shape to calculate_difficulty() without
# touching dummy_data.json.

def _get_field(student, field, default=None):
    """Works whether `student` is an auth_service dict or a model.py-style object."""

    if isinstance(student, dict):
        return student.get(field, default)

    return getattr(student, field, default)


def build_course_difficulty_inputs(course, completed_course_ids):
    """
    Build the (base_difficulty, prerequisites) pair calculate_difficulty()
    expects, from a real Course (model.py) instead of a dummy_data.json
    course dict.

    Course.difficulty_level is 1-5 (see loader.py); calculate_difficulty()
    was designed around a 0-10 scale, so it's doubled here to match.

    There's no historical per-prerequisite grade for real students (the
    students table doesn't track one), so a completed prerequisite's
    "personal_difficulty" falls back to that prerequisite's own catalog
    difficulty, with equal influence across all completed prerequisites.
    """

    base_difficulty = course.difficulty_level * 2

    prerequisites = {}

    for prereq_id in course.prerequisites:

        if prereq_id in completed_course_ids:
            prerequisites[prereq_id] = {
                "personal_difficulty": base_difficulty,
                "influence": 1.0,
            }

    return base_difficulty, prerequisites


def estimate_difficulties_for_real_student(student, courses):
    """
    Real-data equivalent of estimate_difficulties_for_student(): takes the
    authenticated student (dict from Login_systemV2.auth_service.authenticate)
    and the shared course catalog (list[Course] from
    loader.load_courses_and_events), and returns
    {course_id: {"course_id", "name", "base_difficulty", "difficulty"}}.
    """

    completed_course_ids = set(
        _get_field(student, "completed_courses", []) or []
    )

    difficulties = {}

    for course in courses:

        base_difficulty, prerequisites = build_course_difficulty_inputs(
            course,
            completed_course_ids,
        )

        difficulty = calculate_difficulty(
            base_difficulty,
            prerequisites,
        )

        difficulties[course.course_id] = {
            "course_id": course.course_id,
            "name": course.name,
            "base_difficulty": base_difficulty,
            "difficulty": difficulty,
        }

    return difficulties


def _run_cli():
    """
    Manual/interactive test entry point. This only runs when the file is
    executed directly (`python Difficulty_Estimation.py`) — it must NOT run
    on import, otherwise importing this module (e.g. from main.py) would
    block waiting for terminal input.
    """

    username = input("Username: ")
    password = input("Password: ")

    authenticated_user = auth_service.authenticate(
        username,
        password
    )

    student_id = authenticated_user["student_id"]

    student, difficulties = estimate_difficulties_for_student(
        student_id
    )

    print("\nDifficulty Estimation")
    print("=====================")

    print(f"Student: {student['name']}")
    print(f"Student ID: {student['student_id']}")

    for course, data in difficulties.items():

        print(
            f"{course}: "
            f"{data['difficulty']:.2f}/10"
        )


if __name__ == "__main__":
    _run_cli()