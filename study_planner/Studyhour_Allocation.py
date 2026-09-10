"""
Study-Hour Allocation
======================

Distributes the student's available study hours across
courses according to the priorities calculated by Task 2.

The authenticated student's ID is passed to Task 2 so the
correct student's data is used throughout the pipeline.
"""

import Priority_Calculation
# from Login_systemV2 import auth_service


# ============================================================
# STUDY-HOUR ALLOCATION
# ============================================================

def allocate_study_hours(
    courses,
    weekday_hours,
    weekdays,
    weekend_hours,
    weekend_days,
    min_hours
):

    # Calculate total available study hours
    weekday_total = (
        weekday_hours * weekdays
    )

    weekend_total = (
        weekend_hours * weekend_days
    )

    total_hours = (
        weekday_total
        + weekend_total
    )

    # Number of courses
    n = len(courses)

    if n == 0:
        return []

    # Hours remaining after giving every course
    # the minimum required allocation
    remaining_hours = (
        total_hours
        - (n * min_hours)
    )

    if remaining_hours < 0:

        raise ValueError(
            "There are not enough available study hours "
            "to give every course its minimum allocation."
        )

    # Priorities come directly from Task 2
    total_priority = sum(
        course["priority"]
        for course in courses
    )

    allocations = []

    for course in courses:

        if total_priority == 0:

            priority_share = 0

        else:

            priority_share = (
                course["priority"]
                / total_priority
            )

        allocated_hours = (
            min_hours
            + remaining_hours
            * priority_share
        )

        allocations.append({

            "course":
                course["course"],

            "priority":
                course["priority"],

            "allocated_hours":
                allocated_hours
        })

    return allocations


# ============================================================
# PREPARE COURSES FROM TASK 2
# ============================================================

def prepare_courses_from_Priority_Calculation(
    student
):

    """
    Take the courses after Task 2 has calculated
    their priorities and prepare them for Task 3.
    """

    courses = []

    for course_name, course in (
        student["courses"].items()
    ):

        courses.append({

            "course":
                course_name,

            "priority":
                course["priority"]
        })

    return courses


# ============================================================
# AUTHENTICATED STUDENT → TASK 2 → TASK 3
# ============================================================

def generate_study_hour_allocations(
    student_id,
    min_hours
):

    """
    Start Task 3 using the authenticated student's ID.

    Flow:

        student_id
            ↓
        Task 2
            ↓
        priorities
            ↓
        Task 3
            ↓
        study-hour allocation
    """

    # Task 2 finds the correct student and calculates
    # their course priorities.
    student = (
        Priority_Calculation
        .calculate_student_priorities(
            student_id
        )
    )

    # Get courses with Task 2 priorities
    courses = (
        prepare_courses_from_Priority_Calculation(
            student
        )
    )

    # Get actual study-hour preferences
    # from Group A's dummy data.
    weekday_hours = (
        student[
            "study_preferences"
        ][
            "weekday_hours_per_day"
        ]
    )

    weekend_hours = (
        student[
            "study_preferences"
        ][
            "weekend_hours_per_day"
        ]
    )

    # Project scheduling setup:
    #
    # 5 weekdays
    # 2 weekend days
    weekdays = 5
    weekend_days = 2

    allocations = allocate_study_hours(

        courses,

        weekday_hours,
        weekdays,

        weekend_hours,
        weekend_days,

        min_hours
    )

    return student, allocations


# ============================================================
# TEST
# ============================================================


if __name__ == "__main__":
    import json

    # Load the actual dummy data
    with open("data/dummy_data.json", "r") as file:
        students = json.load(file)

    # Use George Wilson from the dummy data
    student = students[0]

    # Run Task 2 to calculate the course priorities
    student = Priority_Calculation.calculate_student_priorities(student)

    # Get courses with their Task 2 priorities
    courses = prepare_courses_from_Priority_Calculation(student)

    # Get study-hour preferences directly from dummy data
    weekday_hours = student["study_preferences"]["weekday_hours_per_day"]
    weekend_hours = student["study_preferences"]["weekend_hours_per_day"]

    # There are 4 weekdays and 3 weekend days
    weekdays = 4
    weekend_days = 3

    # Minimum study hours for each course
    min_hours = 2

    # Run Task 3
    allocations = allocate_study_hours(
        courses,
        weekday_hours,
        weekdays,
        weekend_hours,
        weekend_days,
        min_hours
    )

    # Display results
    print("\n========================================")
    print("STUDY HOUR ALLOCATION")
    print("========================================")

    for allocation in allocations:
        print(
            f"{allocation['course']}: "
            f"{allocation['allocated_hours']:.2f} hours "
            f"(Priority: {allocation['priority']:.3f})"
        )




# if __name__ == "__main__":

#     username = input("Username: ")
#     password = input("Password: ")

#     authenticated_user = (
#         auth_service.authenticate(
#             username,
#             password
#         )
#     )

#     student_id = authenticated_user[
#         "student_id"
#     ]

#     print(
#         f"\nLogged in as: "
#         f"{authenticated_user['name']}"
#     )

#     print(
#         f"Student ID: "
#         f"{student_id}"
#     )

#     # Minimum study hours per course.
#     #
#     # This is an algorithm parameter, not a value
#     # taken from Group A's dummy data.
#     min_hours = 1

#     student, allocations = (
#         generate_study_hour_allocations(
#             student_id,
#             min_hours
#         )
#     )

#     # Display results
#     print(
#         "\n========================================"
#     )

#     print(
#         "STUDY HOUR ALLOCATION"
#     )

#     print(
#         "========================================"
#     )

#     for allocation in allocations:

#         print(
#             f"{allocation['course']}: "
#             f"{allocation['allocated_hours']:.2f} hours "
#             f"(Priority: "
#             f"{allocation['priority']:.3f})"
#         )
