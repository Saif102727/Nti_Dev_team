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
# from Login_systemV2 import auth_service

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


def load_students(filename=r"data\dummy_data.json"):
    """
    Load Group A's student data.
    """

    with open(filename, "r", encoding="utf-8") as file:
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

if __name__ == "__main__":

    students = load_students()

    student = get_student(
        students,
        "STU-2026-001"
    )

    difficulties = estimate_student_difficulties(student)

    print("\nDifficulty Estimation")
    print("=====================")

    for course, data in difficulties.items():

        print(
            f"{course}: "
            f"{data['difficulty']:.2f}/10"
        )


# if __name__ == "__main__":

#     username = input("Username: ")
#     password = input("Password: ")

#     authenticated_user = auth_service.authenticate(
#         username,
#         password
#     )

#     student_id = authenticated_user["student_id"]

#     student, difficulties = estimate_difficulties_for_student(
#         student_id
#     )

#     print("\nDifficulty Estimation")
#     print("=====================")

#     print(f"Student: {student['name']}")
#     print(f"Student ID: {student['student_id']}")

#     for course, data in difficulties.items():

#         print(
#             f"{course}: "
#             f"{data['difficulty']:.2f}/10"
#         )
