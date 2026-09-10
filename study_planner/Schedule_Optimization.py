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



# import math


# # ============================================================
# # TASK 5 — SCHEDULE OPTIMIZATION
# # ============================================================


# # ------------------------------------------------------------
# # 1. AHP WEIGHT CALCULATION
# # ------------------------------------------------------------

# def calculate_ahp_weights(matrix):
#     n = len(matrix)

#     # Step 1: Calculate column sums
#     column_sums = []

#     for j in range(n):
#         total = 0

#         for i in range(n):
#             total += matrix[i][j]

#         column_sums.append(total)

#     # Step 2: Normalize the matrix
#     normalized_matrix = []

#     for i in range(n):
#         row = []

#         for j in range(n):
#             value = matrix[i][j] / column_sums[j]
#             row.append(value)

#         normalized_matrix.append(row)

#     # Step 3: Calculate row averages
#     weights = []

#     for i in range(n):
#         row_average = sum(normalized_matrix[i]) / n
#         weights.append(row_average)

#     return weights


# # ------------------------------------------------------------
# # 2. TASK 5 AHP COMPARISON MATRIX
# # ------------------------------------------------------------

# # Order:
# # P = Priority Satisfaction
# # E = Deadline/Event Satisfaction
# # R = Preference Satisfaction
# # B = Workload Balance

# comparison_matrix = [

#     #    P    E    R    B
#     [   1,  1/2,  3,   3 ],   # P
#     [   2,   1,  5,   5 ],   # E
#     [ 1/3, 1/5,  1, 1/2 ],   # R
#     [ 1/3, 1/5,  2,   1 ]     # B
# ]


# weights = calculate_ahp_weights(comparison_matrix)

# wP = weights[0]
# wE = weights[1]
# wR = weights[2]
# wB = weights[3]


# print("Task 5 AHP Weights")
# print("------------------")
# print(f"Priority:   {wP:.3f}")
# print(f"Deadline:   {wE:.3f}")
# print(f"Preference: {wR:.3f}")
# print(f"Balance:    {wB:.3f}")
# print(f"Total:      {sum(weights):.3f}")


# # ------------------------------------------------------------
# # 3. PRIORITY SATISFACTION
# # ------------------------------------------------------------

# def calculate_priority_satisfaction(schedule, courses):
#     """
#     schedule:
#         dictionary containing study hours for each course

#         Example:
#         {
#             "Math": 6,
#             "Programming": 4,
#             "Physics": 2
#         }

#     courses:
#         dictionary containing course priorities

#         Example:
#         {
#             "Math": 0.8,
#             "Programming": 0.5,
#             "Physics": 0.3
#         }
#     """

#     total_study_hours = sum(schedule.values())

#     if total_study_hours == 0:
#         return 0

#     numerator = 0

#     for course in courses:
#         priority = courses[course]
#         hours = schedule.get(course, 0)

#         numerator += priority * hours

#     denominator = total_study_hours * sum(courses.values())

#     if denominator == 0:
#         return 0

#     score = numerator / denominator

#     return min(score, 1)


# # ------------------------------------------------------------
# # 4. DEADLINE / EVENT SATISFACTION
# # ------------------------------------------------------------

# def calculate_deadline_satisfaction(events):
#     """
#     events is a list of dictionaries.

#     Example:

#     [
#         {
#             "required_hours": 4,
#             "scheduled_before_deadline": 4
#         },
#         {
#             "required_hours": 6,
#             "scheduled_before_deadline": 5
#         }
#     ]
#     """

#     total_required = 0
#     total_completed = 0

#     for event in events:

#         required = event["required_hours"]
#         completed = event["scheduled_before_deadline"]

#         total_required += required
#         total_completed += min(completed, required)

#     if total_required == 0:
#         return 1

#     score = total_completed / total_required

#     return min(score, 1)


# # ------------------------------------------------------------
# # 5. PREFERENCE SATISFACTION
# # ------------------------------------------------------------

# def calculate_preference_satisfaction(sessions):
#     """
#     sessions is a list of study sessions.

#     Example:

#     [
#         {"preferred": True},
#         {"preferred": True},
#         {"preferred": False}
#     ]
#     """

#     if len(sessions) == 0:
#         return 1

#     preferred_sessions = 0

#     for session in sessions:

#         if session["preferred"]:
#             preferred_sessions += 1

#     score = preferred_sessions / len(sessions)

#     return score


# # ------------------------------------------------------------
# # 6. WORKLOAD BALANCE
# # ------------------------------------------------------------

# def calculate_workload_balance(daily_hours):
#     """
#     daily_hours is a list containing study hours for each day.

#     Example:

#     [3, 4, 3, 2, 4, 3, 3]
#     """

#     if len(daily_hours) == 0:
#         return 1

#     average = sum(daily_hours) / len(daily_hours)

#     variance = 0

#     for hours in daily_hours:
#         variance += (hours - average) ** 2

#     variance = variance / len(daily_hours)

#     standard_deviation = math.sqrt(variance)

#     score = 1 / (1 + standard_deviation)

#     return score


# # ------------------------------------------------------------
# # 7. FINAL SCHEDULE SCORE
# # ------------------------------------------------------------

# def calculate_schedule_score(
#         schedule,
#         courses,
#         events,
#         sessions,
#         daily_hours
#     ):

#     # Calculate the four criteria

#     P = calculate_priority_satisfaction(
#         schedule,
#         courses
#     )

#     E = calculate_deadline_satisfaction(
#         events
#     )

#     R = calculate_preference_satisfaction(
#         sessions
#     )

#     B = calculate_workload_balance(
#         daily_hours
#     )

#     # Final weighted score

#     score = (
#         wP * P
#         + wE * E
#         + wR * R
#         + wB * B
#     )

#     return score


# # ------------------------------------------------------------
# # 8. CHECK HARD CONSTRAINTS
# # ------------------------------------------------------------

# def is_valid_schedule(schedule_data):
#     """
#     Hard constraint violations make a schedule invalid.

#     schedule_data should contain:

#         {
#             "has_conflict": False,
#             "deadline_violation": False,
#             "unavailable_time_used": False
#         }
#     """

#     if schedule_data["has_conflict"]:
#         return False

#     if schedule_data["deadline_violation"]:
#         return False

#     if schedule_data["unavailable_time_used"]:
#         return False

#     return True


# # ------------------------------------------------------------
# # 9. OPTIMIZE / RANK SCHEDULES
# # ------------------------------------------------------------

# def optimize_schedules(schedules):

#     valid_schedules = []

#     for schedule in schedules:

#         if not is_valid_schedule(schedule):
#             continue

#         score = calculate_schedule_score(
#             schedule["course_hours"],
#             schedule["courses"],
#             schedule["events"],
#             schedule["sessions"],
#             schedule["daily_hours"]
#         )

#         schedule["score"] = score

#         valid_schedules.append(schedule)

#     # Highest score first
#     valid_schedules.sort(
#         key=lambda x: x["score"],
#         reverse=True
#     )

#     return valid_schedules



"""
Schedule Optimization
=====================

Task 5:

    Receive multiple feasible schedules from Task 4.

    Score every schedule out of 100.

    Select the schedule with the highest score.

Scoring priorities:

    1. Hard constraint compliance
    2. Soft constraints
    3. Preferred study times
    4. Study-place preference
    5. Daily balance
"""


import json

import Schedule_Generation


# ============================================================
# SCORING WEIGHTS
# ============================================================

HARD_CONSTRAINT_WEIGHT = 30
SOFT_CONSTRAINT_WEIGHT = 20
PREFERRED_TIME_WEIGHT = 25
STUDY_PLACE_WEIGHT = 15
BALANCE_WEIGHT = 10


# ============================================================
# GET STUDY SESSIONS
# ============================================================

def get_study_sessions(
    schedule
):

    return [
        session
        for session in schedule
        if session.get(
            "study_session",
            False
        )
    ]


# ============================================================
# CHECK HARD CONSTRAINTS
# ============================================================

def count_hard_constraint_violations(
    schedule,
    student,
    university_schedule
):

    hard_constraints = (
        Schedule_Generation
        .build_hard_constraints(
            student,
            university_schedule
        )
    )

    violations = 0

    study_sessions = (
        get_study_sessions(
            schedule
        )
    )

    for session in study_sessions:

        start = (
            Schedule_Generation
            .time_to_minutes(
                session["start"]
            )
        )

        end = (
            Schedule_Generation
            .time_to_minutes(
                session["end"]
            )
        )

        day = session[
            "day"
        ]

        if not (
            Schedule_Generation
            .is_slot_available(
                day,
                start,
                end,
                hard_constraints
            )
        ):

            violations += 1

    # --------------------------------------------------------
    # Also check study-session overlap.
    # --------------------------------------------------------

    for i in range(
        len(study_sessions)
    ):

        first = study_sessions[i]

        first_start = (
            Schedule_Generation
            .time_to_minutes(
                first["start"]
            )
        )

        first_end = (
            Schedule_Generation
            .time_to_minutes(
                first["end"]
            )
        )

        for j in range(
            i + 1,
            len(study_sessions)
        ):

            second = study_sessions[j]

            if (
                first["day"]
                != second["day"]
            ):

                continue

            second_start = (
                Schedule_Generation
                .time_to_minutes(
                    second["start"]
                )
            )

            second_end = (
                Schedule_Generation
                .time_to_minutes(
                    second["end"]
                )
            )

            if Schedule_Generation.overlaps(
                first_start,
                first_end,
                second_start,
                second_end
            ):

                violations += 1

    return violations


# ============================================================
# HARD CONSTRAINT SCORE
# ============================================================

def calculate_hard_constraint_score(
    schedule,
    student,
    university_schedule
):

    violations = (
        count_hard_constraint_violations(
            schedule,
            student,
            university_schedule
        )
    )

    if violations == 0:
        return 100

    return 0


# ============================================================
# SOFT CONSTRAINT SCORE
# ============================================================

def calculate_soft_constraint_score(
    schedule,
    student
):

    study_sessions = (
        get_study_sessions(
            schedule
        )
    )

    soft_constraints = (
        student[
            "unavailable_periods"
        ].get(
            "soft_constraints",
            []
        )
    )

    if not study_sessions:
        return 100

    total_penalty = 0

    for session in study_sessions:

        start = (
            Schedule_Generation
            .time_to_minutes(
                session["start"]
            )
        )

        end = (
            Schedule_Generation
            .time_to_minutes(
                session["end"]
            )
        )

        penalty = (
            Schedule_Generation
            .calculate_soft_penalty(
                session["day"],
                start,
                end,
                soft_constraints
            )
        )

        total_penalty += penalty

    # --------------------------------------------------------
    # Maximum possible penalty:
    # one penalty for every study session.
    # --------------------------------------------------------

    maximum_penalty = len(
        study_sessions
    )

    if maximum_penalty == 0:
        return 100

    score = (
        1
        - (
            total_penalty
            / maximum_penalty
        )
    ) * 100

    return max(
        0,
        score
    )


# ============================================================
# PREFERRED STUDY TIME SCORE
# ============================================================

def calculate_preferred_time_score(
    schedule,
    student
):

    study_sessions = (
        get_study_sessions(
            schedule
        )
    )

    preferred_times = (
        student[
            "study_preferences"
        ].get(
            "preferred_study_times",
            []
        )
    )

    if not study_sessions:
        return 100

    total_score = 0

    maximum_score = (
        len(study_sessions) * 2
    )

    for session in study_sessions:

        start = (
            Schedule_Generation
            .time_to_minutes(
                session["start"]
            )
        )

        end = (
            Schedule_Generation
            .time_to_minutes(
                session["end"]
            )
        )

        total_score += (
            Schedule_Generation
            .calculate_preference_score(
                session["day"],
                start,
                end,
                preferred_times
            )
        )

    if maximum_score == 0:
        return 100

    return (
        total_score
        / maximum_score
    ) * 100


# ============================================================
# STUDY PLACE SCORE
# ============================================================

def calculate_study_place_score(
    schedule,
    student,
    university_schedule
):

    study_sessions = (
        get_study_sessions(
            schedule
        )
    )

    study_place = (
        student[
            "study_preferences"
        ].get(
            "study_place",
            ""
        )
    )

    if not study_sessions:
        return 100

    total_score = 0
    maximum_score = 3 * len(
        study_sessions
    )

    for session in study_sessions:

        start = (
            Schedule_Generation
            .time_to_minutes(
                session["start"]
            )
        )

        end = (
            Schedule_Generation
            .time_to_minutes(
                session["end"]
            )
        )

        score = (
            Schedule_Generation
            .calculate_study_place_score(
                session["day"],
                start,
                end,
                study_place,
                university_schedule
            )
        )

        # ----------------------------------------------------
        # Convert the possible -3 to +3 range
        # into a 0 to 6 range.
        # ----------------------------------------------------

        normalized_score = (
            score + 3
        )

        total_score += (
            normalized_score
        )

    maximum_normalized = (
        6 * len(study_sessions)
    )

    if maximum_normalized == 0:
        return 100

    return (
        total_score
        / maximum_normalized
    ) * 100


# ============================================================
# BALANCE SCORE
# ============================================================

def calculate_balance_score(
    schedule,
    student,
    allocations
):

    daily_targets = (
        Schedule_Generation
        .calculate_daily_targets(
            student,
            allocations
        )
    )

    daily_hours = {
        day: 0
        for day in Schedule_Generation.DAYS
    }

    study_sessions = (
        get_study_sessions(
            schedule
        )
    )

    for session in study_sessions:

        start = (
            Schedule_Generation
            .time_to_minutes(
                session["start"]
            )
        )

        end = (
            Schedule_Generation
            .time_to_minutes(
                session["end"]
            )
        )

        duration = (
            end - start
        ) / 60

        daily_hours[
            session["day"]
        ] += duration

    # --------------------------------------------------------
    # Compare actual hours against the target.
    # --------------------------------------------------------

    total_difference = 0
    total_target = 0

    for day in (
        Schedule_Generation.DAYS
    ):

        target = daily_targets[
            day
        ]

        actual = daily_hours[
            day
        ]

        total_difference += abs(
            actual - target
        )

        total_target += target

    if total_target == 0:
        return 100

    balance_ratio = max(
        0,
        1 - (
            total_difference
            / total_target
        )
    )

    return balance_ratio * 100


# ============================================================
# FINAL SCHEDULE SCORE
# ============================================================

def calculate_schedule_score(
    schedule,
    student,
    university_schedule,
    allocations
):

    # --------------------------------------------------------
    # 1. Hard constraints
    # --------------------------------------------------------

    hard_score = (
        calculate_hard_constraint_score(
            schedule,
            student,
            university_schedule
        )
    )

    # A schedule violating a hard constraint
    # is automatically rejected.

    if hard_score == 0:

        return 0

    # --------------------------------------------------------
    # 2. Soft constraints
    # --------------------------------------------------------

    soft_score = (
        calculate_soft_constraint_score(
            schedule,
            student
        )
    )

    # --------------------------------------------------------
    # 3. Preferred study times
    # --------------------------------------------------------

    preferred_score = (
        calculate_preferred_time_score(
            schedule,
            student
        )
    )

    # --------------------------------------------------------
    # 4. Study place
    # --------------------------------------------------------

    place_score = (
        calculate_study_place_score(
            schedule,
            student,
            university_schedule
        )
    )

    # --------------------------------------------------------
    # 5. Balance
    # --------------------------------------------------------

    balance_score = (
        calculate_balance_score(
            schedule,
            student,
            allocations
        )
    )

    # --------------------------------------------------------
    # FINAL SCORE / 100
    # --------------------------------------------------------

    final_score = (

        (
            hard_score
            * HARD_CONSTRAINT_WEIGHT
        )

        / 100

        +

        (
            soft_score
            * SOFT_CONSTRAINT_WEIGHT
        )

        / 100

        +

        (
            preferred_score
            * PREFERRED_TIME_WEIGHT
        )

        / 100

        +

        (
            place_score
            * STUDY_PLACE_WEIGHT
        )

        / 100

        +

        (
            balance_score
            * BALANCE_WEIGHT
        )

        / 100
    )

    return final_score


# ============================================================
# OPTIMIZE SCHEDULES
# ============================================================

def optimize_schedules(
    schedules,
    student,
    university_schedule,
    allocations
):

    if not schedules:

        raise ValueError(
            "No schedules were provided "
            "for optimization."
        )

    best_schedule = None
    best_score = -1

    scored_schedules = []

    for index, schedule in enumerate(
        schedules,
        start=1
    ):

        score = (
            calculate_schedule_score(
                schedule,
                student,
                university_schedule,
                allocations
            )
        )

        scored_schedules.append({

            "schedule_number":
                index,

            "score":
                score,

            "schedule":
                schedule
        })

        # ----------------------------------------------------
        # Keep highest score
        # ----------------------------------------------------

        if score > best_score:

            best_score = score

            best_schedule = schedule

    return {

        "schedule":
            best_schedule,

        "score":
            best_score,

        "all_scores":
            scored_schedules
    }


# ============================================================
# PRINT OPTIMIZATION RESULTS
# ============================================================

def print_optimization_results(
    result
):

    print("\n")
    print("=" * 70)
    print("SCHEDULE OPTIMIZATION RESULTS")
    print("=" * 70)

    for item in result[
        "all_scores"
    ]:

        print(
            f"Schedule "
            f"#{item['schedule_number']}: "
            f"{item['score']:.2f}/100"
        )

    print("\n" + "=" * 70)

    print(
        f"BEST SCHEDULE SCORE: "
        f"{result['score']:.2f}/100"
    )

    print("=" * 70)

    Schedule_Generation.print_schedule(
        result["schedule"]
    )


# ============================================================
# TEST 1
# FIRST STUDENT
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 70)
    print("TASK 5 - FIRST STUDENT")
    print("=" * 70)

    # --------------------------------------------------------
    # Load student data
    # --------------------------------------------------------

    with open(
        "data/dummy_data.json",
        "r"
    ) as file:

        students = json.load(file)

    student = students[0]

    # --------------------------------------------------------
    # Task 2 -> Task 3
    # --------------------------------------------------------

    student, allocations = (
        Schedule_Generation
        .get_allocations_from_task3(
            student
        )
    )

    # --------------------------------------------------------
    # Load university schedule
    # --------------------------------------------------------

    with open(
        "data/schedule.json",
        "r"
    ) as file:

        university_data = json.load(file)

    # --------------------------------------------------------
    # Get student's university schedule
    # --------------------------------------------------------

    university_schedule = (
        Schedule_Generation
        .get_student_schedule(
            student["student_id"],
            university_data
        )
    )

    print(
        f"\nStudent: "
        f"{student['name']}"
    )

    print(
        f"Student ID: "
        f"{student['student_id']}"
    )

    print(
        f"University Schedule: "
        f"{university_schedule['schedule_id']}"
    )

    # --------------------------------------------------------
    # Generate multiple schedules using Task 4
    # --------------------------------------------------------

    schedules = (
        Schedule_Generation
        .generate_multiple_schedules(

            student,

            allocations,

            university_schedule,

            number_of_schedules=10
        )
    )

    print(
        f"\nTask 4 generated "
        f"{len(schedules)} "
        f"feasible schedules."
    )

    # --------------------------------------------------------
    # Task 5 optimization
    # --------------------------------------------------------

    result = optimize_schedules(

        schedules,

        student,

        university_schedule,

        allocations
    )

    # --------------------------------------------------------
    # Show results
    # --------------------------------------------------------

    print_optimization_results(
        result
    )