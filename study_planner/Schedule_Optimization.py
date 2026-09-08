"""
Schedule Optimization
======================
STATUS: Not implemented yet.

Intended purpose:
    Take a raw generated schedule (see Schedule_Generation.py) and optimize
    the allocation of study hours across courses, respecting the student's
    max daily hours and each course's priority/difficulty, instead of the
    temporary "equal split" logic currently used in Main/main.py.

Suggested signature:

    def optimize_schedule(schedule, max_daily_hours: float) -> dict:
        ...
"""



import math


# ============================================================
# TASK 5 — SCHEDULE OPTIMIZATION
# ============================================================


# ------------------------------------------------------------
# 1. AHP WEIGHT CALCULATION
# ------------------------------------------------------------

def calculate_ahp_weights(matrix):
    n = len(matrix)

    # Step 1: Calculate column sums
    column_sums = []

    for j in range(n):
        total = 0

        for i in range(n):
            total += matrix[i][j]

        column_sums.append(total)

    # Step 2: Normalize the matrix
    normalized_matrix = []

    for i in range(n):
        row = []

        for j in range(n):
            value = matrix[i][j] / column_sums[j]
            row.append(value)

        normalized_matrix.append(row)

    # Step 3: Calculate row averages
    weights = []

    for i in range(n):
        row_average = sum(normalized_matrix[i]) / n
        weights.append(row_average)

    return weights


# ------------------------------------------------------------
# 2. TASK 5 AHP COMPARISON MATRIX
# ------------------------------------------------------------

# Order:
# P = Priority Satisfaction
# E = Deadline/Event Satisfaction
# R = Preference Satisfaction
# B = Workload Balance

comparison_matrix = [

    #    P    E    R    B
    [   1,  1/2,  3,   3 ],   # P
    [   2,   1,  5,   5 ],   # E
    [ 1/3, 1/5,  1, 1/2 ],   # R
    [ 1/3, 1/5,  2,   1 ]     # B
]


weights = calculate_ahp_weights(comparison_matrix)

wP = weights[0]
wE = weights[1]
wR = weights[2]
wB = weights[3]


print("Task 5 AHP Weights")
print("------------------")
print(f"Priority:   {wP:.3f}")
print(f"Deadline:   {wE:.3f}")
print(f"Preference: {wR:.3f}")
print(f"Balance:    {wB:.3f}")
print(f"Total:      {sum(weights):.3f}")


# ------------------------------------------------------------
# 3. PRIORITY SATISFACTION
# ------------------------------------------------------------

def calculate_priority_satisfaction(schedule, courses):
    """
    schedule:
        dictionary containing study hours for each course

        Example:
        {
            "Math": 6,
            "Programming": 4,
            "Physics": 2
        }

    courses:
        dictionary containing course priorities

        Example:
        {
            "Math": 0.8,
            "Programming": 0.5,
            "Physics": 0.3
        }
    """

    total_study_hours = sum(schedule.values())

    if total_study_hours == 0:
        return 0

    numerator = 0

    for course in courses:
        priority = courses[course]
        hours = schedule.get(course, 0)

        numerator += priority * hours

    denominator = total_study_hours * sum(courses.values())

    if denominator == 0:
        return 0

    score = numerator / denominator

    return min(score, 1)


# ------------------------------------------------------------
# 4. DEADLINE / EVENT SATISFACTION
# ------------------------------------------------------------

def calculate_deadline_satisfaction(events):
    """
    events is a list of dictionaries.

    Example:

    [
        {
            "required_hours": 4,
            "scheduled_before_deadline": 4
        },
        {
            "required_hours": 6,
            "scheduled_before_deadline": 5
        }
    ]
    """

    total_required = 0
    total_completed = 0

    for event in events:

        required = event["required_hours"]
        completed = event["scheduled_before_deadline"]

        total_required += required
        total_completed += min(completed, required)

    if total_required == 0:
        return 1

    score = total_completed / total_required

    return min(score, 1)


# ------------------------------------------------------------
# 5. PREFERENCE SATISFACTION
# ------------------------------------------------------------

def calculate_preference_satisfaction(sessions):
    """
    sessions is a list of study sessions.

    Example:

    [
        {"preferred": True},
        {"preferred": True},
        {"preferred": False}
    ]
    """

    if len(sessions) == 0:
        return 1

    preferred_sessions = 0

    for session in sessions:

        if session["preferred"]:
            preferred_sessions += 1

    score = preferred_sessions / len(sessions)

    return score


# ------------------------------------------------------------
# 6. WORKLOAD BALANCE
# ------------------------------------------------------------

def calculate_workload_balance(daily_hours):
    """
    daily_hours is a list containing study hours for each day.

    Example:

    [3, 4, 3, 2, 4, 3, 3]
    """

    if len(daily_hours) == 0:
        return 1

    average = sum(daily_hours) / len(daily_hours)

    variance = 0

    for hours in daily_hours:
        variance += (hours - average) ** 2

    variance = variance / len(daily_hours)

    standard_deviation = math.sqrt(variance)

    score = 1 / (1 + standard_deviation)

    return score


# ------------------------------------------------------------
# 7. FINAL SCHEDULE SCORE
# ------------------------------------------------------------

def calculate_schedule_score(
        schedule,
        courses,
        events,
        sessions,
        daily_hours
    ):

    # Calculate the four criteria

    P = calculate_priority_satisfaction(
        schedule,
        courses
    )

    E = calculate_deadline_satisfaction(
        events
    )

    R = calculate_preference_satisfaction(
        sessions
    )

    B = calculate_workload_balance(
        daily_hours
    )

    # Final weighted score

    score = (
        wP * P
        + wE * E
        + wR * R
        + wB * B
    )

    return score


# ------------------------------------------------------------
# 8. CHECK HARD CONSTRAINTS
# ------------------------------------------------------------

def is_valid_schedule(schedule_data):
    """
    Hard constraint violations make a schedule invalid.

    schedule_data should contain:

        {
            "has_conflict": False,
            "deadline_violation": False,
            "unavailable_time_used": False
        }
    """

    if schedule_data["has_conflict"]:
        return False

    if schedule_data["deadline_violation"]:
        return False

    if schedule_data["unavailable_time_used"]:
        return False

    return True


# ------------------------------------------------------------
# 9. OPTIMIZE / RANK SCHEDULES
# ------------------------------------------------------------

def optimize_schedules(schedules):

    valid_schedules = []

    for schedule in schedules:

        if not is_valid_schedule(schedule):
            continue

        score = calculate_schedule_score(
            schedule["course_hours"],
            schedule["courses"],
            schedule["events"],
            schedule["sessions"],
            schedule["daily_hours"]
        )

        schedule["score"] = score

        valid_schedules.append(schedule)

    # Highest score first
    valid_schedules.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return valid_schedules