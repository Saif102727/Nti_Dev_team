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



def normalize_difficulty(difficulty):
    return (difficulty - 1) / 9


def calculate_weakness(grade):
    return 1 - (grade / 100)


def calculate_urgency(days_remaining, k=7):
    return 1 / (1 + days_remaining / k)


def calculate_remaining_material(total_material, completed_material):
    remaining_material = total_material - completed_material
    return remaining_material / total_material


def calculate_priority(difficulty, grade, total_material,
                       completed_material, days_remaining,
                       weights):

    D = normalize_difficulty(difficulty)

    W = calculate_weakness(grade)

    U = calculate_urgency(days_remaining)

    M = calculate_remaining_material(
        total_material,
        completed_material
    )

    priority = (
        weights[0] * D
        + weights[1] * W
        + weights[2] * U
        + weights[3] * M
    )

    return priority

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


comparison_matrix = [
    [1,   1/2, 1/3, 2],
    [2,   1,   1/2, 3],
    [3,   2,   1,   4],
    [1/2, 1/3, 1/4, 1]
]

weights = calculate_ahp_weights(comparison_matrix)

# print("Difficulty:", weights[0])
# print("Weakness:", weights[1])
# print("Urgency:", weights[2])
# print("Material:", weights[3])
# print("Total:", sum(weights))

# priority = calculate_priority(
#     difficulty=7.0,
#     grade=70,
#     total_material=20,
#     completed_material=10,
#     days_remaining=14,
#     weights=weights
# )



# priority = calculate_priority(
#     difficulty=9.0,
#     grade=50,
#     total_material=20,
#     completed_material=5,
#     days_remaining=14,
#     weights=weights
# )


# priority = calculate_priority(
#     difficulty=3.0,
#     grade=90,
#     total_material=20,
#     completed_material=15,
#     days_remaining=30,
#     weights=weights
# )


# priority = calculate_priority(
#     difficulty=7.0,
#     grade=70,
#     total_material=20,
#     completed_material=10,
#     days_remaining=1,
#     weights=weights
# )


# priority = calculate_priority(
#     difficulty=8.0,
#     grade=75,
#     total_material=20,
#     completed_material=20,
#     days_remaining=14,
#     weights=weights
# )


# print(f"Priority: {priority:.2f}")