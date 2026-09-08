"""
Priority Calculation
======================
STATUS: Not implemented yet.

Intended purpose:
    Rank a student's courses/sessions by priority so the scheduler knows
    what to study first. Priority should likely combine:
      - course difficulty (see Difficulty_Estimation.py)
      - proximity of upcoming academic_events (exams, quizzes, deadlines)
      - how little time remains before the next related session

Suggested signature:

    def calculate_priority(course, academic_events, current_week: int) -> float:
        ...
"""

# import Difficulty_Estimation

# def normalize_difficulty(difficulty):
#     return (difficulty - 1) / 9


# def calculate_weakness(grade):
#     return 1 - (grade / 100)


# def calculate_urgency(days_remaining, k=7):
#     return 1 / (1 + days_remaining / k)


# def calculate_remaining_material(total_material, completed_material):
#     remaining_material = total_material - completed_material
#     return remaining_material / total_material


# def calculate_priority(difficulty, grade, total_material,
#                        completed_material, days_remaining,
#                        weights):

#     D = normalize_difficulty(difficulty)

#     W = calculate_weakness(grade)

#     U = calculate_urgency(days_remaining)

#     M = calculate_remaining_material(
#         total_material,
#         completed_material
#     )

#     priority = (
#         weights[0] * D
#         + weights[1] * W
#         + weights[2] * U
#         + weights[3] * M
#     )

#     return priority

# def calculate_ahp_weights(matrix):

#     n = len(matrix)

#     column_sums = []

#     for j in range(n):
#         total = 0

#         for i in range(n):
#             total += matrix[i][j]

#         column_sums.append(total)

#     normalized_matrix = []

#     for i in range(n):
#         row = []

#         for j in range(n):
#             value = matrix[i][j] / column_sums[j]
#             row.append(value)

#         normalized_matrix.append(row)

#     weights = []

#     for i in range(n):
#         row_average = sum(normalized_matrix[i]) / n
#         weights.append(row_average)

#     return weights


# comparison_matrix = [
#     [1,   1/2, 1/3, 2],
#     [2,   1,   1/2, 3],
#     [3,   2,   1,   4],
#     [1/2, 1/3, 1/4, 1]
# ]


# weights = calculate_ahp_weights(comparison_matrix)
# # print("Difficulty:", weights[0])
# # print("Weakness:", weights[1])
# # print("Urgency:", weights[2])
# # print("Material:", weights[3])
# # print("Total:", sum(weights))


# priority = calculate_priority(
#     difficulty=7.0,
#     grade=70,
#     total_material=20,
#     completed_material=10,
#     days_remaining=14,
#     weights=weights
# )
# print(f"Priority: {priority:.2f}")




# ============================================================
# TASK 2 - PRIORITY CALCULATION
# ============================================================

import Difficulty_Estimation


# ============================================================
# AHP WEIGHTS
# ============================================================

def calculate_ahp_weights(matrix):

    n = len(matrix)

    column_sums = []

    for j in range(n):

        total = 0

        for i in range(n):
            total += matrix[i][j]

        column_sums.append(total)

    normalized_matrix = []

    for i in range(n):

        row = []

        for j in range(n):

            value = matrix[i][j] / column_sums[j]

            row.append(value)

        normalized_matrix.append(row)

    weights = []

    for i in range(n):

        row_average = sum(normalized_matrix[i]) / n

        weights.append(row_average)

    return weights


# Order:
# Difficulty, Weakness, Urgency, Material

comparison_matrix = [

    [1,   1/2, 1/3, 2],

    [2,   1,   1/2, 3],

    [3,   2,   1,   4],

    [1/2, 1/3, 1/4, 1]

]

weights = calculate_ahp_weights(
    comparison_matrix
)

wD = weights[0]
wW = weights[1]
wU = weights[2]
wM = weights[3]


# ============================================================
# NORMALIZE DIFFICULTY
# ============================================================

def normalize_difficulty(difficulty):

    return (difficulty - 1) / 9


# ============================================================
# WEAKNESS
# ============================================================

def calculate_weakness(grade):

    return 1 - (grade / 100)


# ============================================================
# URGENCY
# ============================================================

def calculate_urgency(days_remaining, k=7):

    return 1 / (1 + days_remaining / k)


# ============================================================
# REMAINING MATERIAL
# ============================================================

def calculate_remaining_material(
        total_material,
        completed_material
):

    if total_material <= 0:
        return 0

    remaining = total_material - completed_material

    return max(
        0,
        remaining / total_material
    )


# ============================================================
# PRIORITY
# ============================================================

def calculate_priority(
        difficulty,
        grade,
        total_material,
        completed_material,
        days_remaining
):

    D = normalize_difficulty(
        difficulty
    )

    W = calculate_weakness(
        grade
    )

    U = calculate_urgency(
        days_remaining
    )

    M = calculate_remaining_material(
        total_material,
        completed_material
    )

    priority = (

        wD * D
        +
        wW * W
        +
        wU * U
        +
        wM * M

    )

    return priority


# ============================================================
# TASK 1 -> TASK 2
# ============================================================

def calculate_student_priorities(student):

    # --------------------------------------------
    # GET DIFFICULTIES FROM TASK 1
    # --------------------------------------------

    courses = Difficulty_Estimation.estimate_student_difficulties(
        student
    )

    prioritized_courses = {}

    for course_name, course in courses.items():

        # ------------------------------------------------
        # Task 2 requires these fields from Group A.
        # ------------------------------------------------

        required_fields = [
            "grade",
            "total_material",
            "completed_material",
            "days_remaining"
        ]

        missing = []

        for field in required_fields:

            if field not in course:
                missing.append(field)

        if missing:

            raise ValueError(
                f"{course_name} is missing Task 2 data: "
                f"{', '.join(missing)}"
            )

        priority = calculate_priority(

            course["difficulty"],

            course["grade"],

            course["total_material"],

            course["completed_material"],

            course["days_remaining"]

        )

        prioritized_courses[course_name] = course.copy()

        prioritized_courses[course_name]["priority"] = priority

    return prioritized_courses


# ============================================================
# TEST / MAIN
# ============================================================

if __name__ == "__main__":

    students = Difficulty_Estimation.load_students()

    student = Difficulty_Estimation.get_student(
        students,
        "STU-2026-001"
    )

    priorities = calculate_student_priorities(
        student
    )

    print("\nPriority Calculation")
    print("====================")

    for course, data in priorities.items():

        print(
            f"{course}: "
            f"{data['priority']:.3f}"
        )