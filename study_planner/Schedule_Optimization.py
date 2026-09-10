

# import Schedule_Generation


# # ============================================================
# # SCORING WEIGHTS
# # ============================================================

# HARD_CONSTRAINT_WEIGHT = 30
# SOFT_CONSTRAINT_WEIGHT = 20
# PREFERRED_TIME_WEIGHT = 25
# STUDY_PLACE_WEIGHT = 15
# BALANCE_WEIGHT = 10


# # ============================================================
# # GET STUDY SESSIONS
# # ============================================================

# def get_study_sessions(
#     schedule
# ):

#     return [
#         session
#         for session in schedule
#         if session.get(
#             "study_session",
#             False
#         )
#     ]


# # ============================================================
# # CHECK HARD CONSTRAINTS
# # ============================================================

# def count_hard_constraint_violations(
#     schedule,
#     student,
#     university_schedule
# ):

#     hard_constraints = (
#         Schedule_Generation
#         .build_hard_constraints(
#             student,
#             university_schedule
#         )
#     )

#     violations = 0

#     study_sessions = (
#         get_study_sessions(
#             schedule
#         )
#     )

#     for session in study_sessions:

#         start = (
#             Schedule_Generation
#             .time_to_minutes(
#                 session["start"]
#             )
#         )

#         end = (
#             Schedule_Generation
#             .time_to_minutes(
#                 session["end"]
#             )
#         )

#         day = session[
#             "day"
#         ]

#         if not (
#             Schedule_Generation
#             .is_slot_available(
#                 day,
#                 start,
#                 end,
#                 hard_constraints
#             )
#         ):

#             violations += 1

#     # --------------------------------------------------------
#     # Also check study-session overlap.
#     # --------------------------------------------------------

#     for i in range(
#         len(study_sessions)
#     ):

#         first = study_sessions[i]

#         first_start = (
#             Schedule_Generation
#             .time_to_minutes(
#                 first["start"]
#             )
#         )

#         first_end = (
#             Schedule_Generation
#             .time_to_minutes(
#                 first["end"]
#             )
#         )

#         for j in range(
#             i + 1,
#             len(study_sessions)
#         ):

#             second = study_sessions[j]

#             if (
#                 first["day"]
#                 != second["day"]
#             ):

#                 continue

#             second_start = (
#                 Schedule_Generation
#                 .time_to_minutes(
#                     second["start"]
#                 )
#             )

#             second_end = (
#                 Schedule_Generation
#                 .time_to_minutes(
#                     second["end"]
#                 )
#             )

#             if Schedule_Generation.overlaps(
#                 first_start,
#                 first_end,
#                 second_start,
#                 second_end
#             ):

#                 violations += 1

#     return violations


# # ============================================================
# # HARD CONSTRAINT SCORE
# # ============================================================

# def calculate_hard_constraint_score(
#     schedule,
#     student,
#     university_schedule
# ):

#     violations = (
#         count_hard_constraint_violations(
#             schedule,
#             student,
#             university_schedule
#         )
#     )

#     if violations == 0:
#         return 100

#     return 0


# # ============================================================
# # SOFT CONSTRAINT SCORE
# # ============================================================

# def calculate_soft_constraint_score(
#     schedule,
#     student
# ):

#     study_sessions = (
#         get_study_sessions(
#             schedule
#         )
#     )

#     soft_constraints = (
#         student[
#             "unavailable_periods"
#         ].get(
#             "soft_constraints",
#             []
#         )
#     )

#     if not study_sessions:
#         return 100

#     total_penalty = 0

#     for session in study_sessions:

#         start = (
#             Schedule_Generation
#             .time_to_minutes(
#                 session["start"]
#             )
#         )

#         end = (
#             Schedule_Generation
#             .time_to_minutes(
#                 session["end"]
#             )
#         )

#         penalty = (
#             Schedule_Generation
#             .calculate_soft_penalty(
#                 session["day"],
#                 start,
#                 end,
#                 soft_constraints
#             )
#         )

#         total_penalty += penalty

#     # --------------------------------------------------------
#     # Maximum possible penalty:
#     # one penalty for every study session.
#     # --------------------------------------------------------

#     maximum_penalty = len(
#         study_sessions
#     )

#     if maximum_penalty == 0:
#         return 100

#     score = (
#         1
#         - (
#             total_penalty
#             / maximum_penalty
#         )
#     ) * 100

#     return max(
#         0,
#         score
#     )


# # ============================================================
# # PREFERRED STUDY TIME SCORE
# # ============================================================

# def calculate_preferred_time_score(
#     schedule,
#     student
# ):

#     study_sessions = (
#         get_study_sessions(
#             schedule
#         )
#     )

#     preferred_times = (
#         student[
#             "study_preferences"
#         ].get(
#             "preferred_study_times",
#             []
#         )
#     )

#     if not study_sessions:
#         return 100

#     total_score = 0

#     maximum_score = (
#         len(study_sessions) * 2
#     )

#     for session in study_sessions:

#         start = (
#             Schedule_Generation
#             .time_to_minutes(
#                 session["start"]
#             )
#         )

#         end = (
#             Schedule_Generation
#             .time_to_minutes(
#                 session["end"]
#             )
#         )

#         total_score += (
#             Schedule_Generation
#             .calculate_preference_score(
#                 session["day"],
#                 start,
#                 end,
#                 preferred_times
#             )
#         )

#     if maximum_score == 0:
#         return 100

#     return (
#         total_score
#         / maximum_score
#     ) * 100


# # ============================================================
# # STUDY PLACE SCORE
# # ============================================================

# def calculate_study_place_score(
#     schedule,
#     student,
#     university_schedule
# ):

#     study_sessions = (
#         get_study_sessions(
#             schedule
#         )
#     )

#     study_place = (
#         student[
#             "study_preferences"
#         ].get(
#             "study_place",
#             ""
#         )
#     )

#     if not study_sessions:
#         return 100

#     total_score = 0
#     maximum_score = 3 * len(
#         study_sessions
#     )

#     for session in study_sessions:

#         start = (
#             Schedule_Generation
#             .time_to_minutes(
#                 session["start"]
#             )
#         )

#         end = (
#             Schedule_Generation
#             .time_to_minutes(
#                 session["end"]
#             )
#         )

#         score = (
#             Schedule_Generation
#             .calculate_study_place_score(
#                 session["day"],
#                 start,
#                 end,
#                 study_place,
#                 university_schedule
#             )
#         )

#         # ----------------------------------------------------
#         # Convert the possible -3 to +3 range
#         # into a 0 to 6 range.
#         # ----------------------------------------------------

#         normalized_score = (
#             score + 3
#         )

#         total_score += (
#             normalized_score
#         )

#     maximum_normalized = (
#         6 * len(study_sessions)
#     )

#     if maximum_normalized == 0:
#         return 100

#     return (
#         total_score
#         / maximum_normalized
#     ) * 100


# # ============================================================
# # BALANCE SCORE
# # ============================================================

# def calculate_balance_score(
#     schedule,
#     student,
#     allocations
# ):

#     daily_targets = (
#         Schedule_Generation
#         .calculate_daily_targets(
#             student,
#             allocations
#         )
#     )

#     daily_hours = {
#         day: 0
#         for day in Schedule_Generation.DAYS
#     }

#     study_sessions = (
#         get_study_sessions(
#             schedule
#         )
#     )

#     for session in study_sessions:

#         start = (
#             Schedule_Generation
#             .time_to_minutes(
#                 session["start"]
#             )
#         )

#         end = (
#             Schedule_Generation
#             .time_to_minutes(
#                 session["end"]
#             )
#         )

#         duration = (
#             end - start
#         ) / 60

#         daily_hours[
#             session["day"]
#         ] += duration

#     # --------------------------------------------------------
#     # Compare actual hours against the target.
#     # --------------------------------------------------------

#     total_difference = 0
#     total_target = 0

#     for day in (
#         Schedule_Generation.DAYS
#     ):

#         target = daily_targets[
#             day
#         ]

#         actual = daily_hours[
#             day
#         ]

#         total_difference += abs(
#             actual - target
#         )

#         total_target += target

#     if total_target == 0:
#         return 100

#     balance_ratio = max(
#         0,
#         1 - (
#             total_difference
#             / total_target
#         )
#     )

#     return balance_ratio * 100


# # ============================================================
# # FINAL SCHEDULE SCORE
# # ============================================================

# def calculate_schedule_score(
#     schedule,
#     student,
#     university_schedule,
#     allocations
# ):

#     # --------------------------------------------------------
#     # 1. Hard constraints
#     # --------------------------------------------------------

#     hard_score = (
#         calculate_hard_constraint_score(
#             schedule,
#             student,
#             university_schedule
#         )
#     )

#     # A schedule violating a hard constraint
#     # is automatically rejected.

#     if hard_score == 0:

#         return 0

#     # --------------------------------------------------------
#     # 2. Soft constraints
#     # --------------------------------------------------------

#     soft_score = (
#         calculate_soft_constraint_score(
#             schedule,
#             student
#         )
#     )

#     # --------------------------------------------------------
#     # 3. Preferred study times
#     # --------------------------------------------------------

#     preferred_score = (
#         calculate_preferred_time_score(
#             schedule,
#             student
#         )
#     )

#     # --------------------------------------------------------
#     # 4. Study place
#     # --------------------------------------------------------

#     place_score = (
#         calculate_study_place_score(
#             schedule,
#             student,
#             university_schedule
#         )
#     )

#     # --------------------------------------------------------
#     # 5. Balance
#     # --------------------------------------------------------

#     balance_score = (
#         calculate_balance_score(
#             schedule,
#             student,
#             allocations
#         )
#     )

#     # --------------------------------------------------------
#     # FINAL SCORE / 100
#     # --------------------------------------------------------

#     final_score = (

#         (
#             hard_score
#             * HARD_CONSTRAINT_WEIGHT
#         )

#         / 100

#         +

#         (
#             soft_score
#             * SOFT_CONSTRAINT_WEIGHT
#         )

#         / 100

#         +

#         (
#             preferred_score
#             * PREFERRED_TIME_WEIGHT
#         )

#         / 100

#         +

#         (
#             place_score
#             * STUDY_PLACE_WEIGHT
#         )

#         / 100

#         +

#         (
#             balance_score
#             * BALANCE_WEIGHT
#         )

#         / 100
#     )

#     return final_score


# # ============================================================
# # OPTIMIZE SCHEDULES
# # ============================================================

# def optimize_schedules(
#     schedules,
#     student,
#     university_schedule,
#     allocations
# ):

#     if not schedules:

#         raise ValueError(
#             "No schedules were provided "
#             "for optimization."
#         )

#     best_schedule = None
#     best_score = -1

#     scored_schedules = []

#     for index, schedule in enumerate(
#         schedules,
#         start=1
#     ):

#         score = (
#             calculate_schedule_score(
#                 schedule,
#                 student,
#                 university_schedule,
#                 allocations
#             )
#         )

#         scored_schedules.append({

#             "schedule_number":
#                 index,

#             "score":
#                 score,

#             "schedule":
#                 schedule
#         })

#         # ----------------------------------------------------
#         # Keep highest score
#         # ----------------------------------------------------

#         if score > best_score:

#             best_score = score

#             best_schedule = schedule

#     return {

#         "schedule":
#             best_schedule,

#         "score":
#             best_score,

#         "all_scores":
#             scored_schedules
#     }


# # ============================================================
# # PRINT OPTIMIZATION RESULTS
# # ============================================================

# def print_optimization_results(
#     result
# ):

#     print("\n")
#     print("=" * 70)
#     print("SCHEDULE OPTIMIZATION RESULTS")
#     print("=" * 70)

#     for item in result[
#         "all_scores"
#     ]:

#         print(
#             f"Schedule "
#             f"#{item['schedule_number']}: "
#             f"{item['score']:.2f}/100"
#         )

#     print("\n" + "=" * 70)

#     print(
#         f"BEST SCHEDULE SCORE: "
#         f"{result['score']:.2f}/100"
#     )

#     print("=" * 70)

#     Schedule_Generation.print_schedule(
#         result["schedule"]
#     )


# # ============================================================
# # TEST 1
# # FIRST STUDENT
# # ============================================================

# if __name__ == "__main__":

#     print("\n")
#     print("=" * 70)
#     print("TASK 5 - FIRST STUDENT")
#     print("=" * 70)

#     # --------------------------------------------------------
#     # Load student data
#     # --------------------------------------------------------

#     with open(
#         "data/dummy_data.json",
#         "r"
#     ) as file:

#         students = json.load(file)

#     student = students[0]

#     # --------------------------------------------------------
#     # Task 2 -> Task 3
#     # --------------------------------------------------------

#     student, allocations = (
#         Schedule_Generation
#         .get_allocations_from_task3(
#             student
#         )
#     )

#     # --------------------------------------------------------
#     # Load university schedule
#     # --------------------------------------------------------

#     with open(
#         "data/schedule.json",
#         "r"
#     ) as file:

#         university_data = json.load(file)

#     # --------------------------------------------------------
#     # Get student's university schedule
#     # --------------------------------------------------------

#     university_schedule = (
#         Schedule_Generation
#         .get_student_schedule(
#             student["student_id"],
#             university_data
#         )
#     )

#     print(
#         f"\nStudent: "
#         f"{student['name']}"
#     )

#     print(
#         f"Student ID: "
#         f"{student['student_id']}"
#     )

#     print(
#         f"University Schedule: "
#         f"{university_schedule['schedule_id']}"
#     )

#     # --------------------------------------------------------
#     # Generate multiple schedules using Task 4
#     # --------------------------------------------------------

#     schedules = (
#         Schedule_Generation
#         .generate_multiple_schedules(

#             student,

#             allocations,

#             university_schedule,

#             number_of_schedules=10
#         )
#     )

#     print(
#         f"\nTask 4 generated "
#         f"{len(schedules)} "
#         f"feasible schedules."
#     )

#     # --------------------------------------------------------
#     # Task 5 optimization
#     # --------------------------------------------------------

#     result = optimize_schedules(

#         schedules,

#         student,

#         university_schedule,

#         allocations
#     )

#     # --------------------------------------------------------
#     # Show results
#     # --------------------------------------------------------

#     print_optimization_results(
#         result
#     )






"""
Schedule Optimization
======================

Task 5:
    Evaluate the schedules generated by Task 4,
    rank them according to optimization criteria,
    select the best schedule,
    and display only the best schedule to the user.

Optimization criteria:
    - Hard constraints
    - Soft constraints
    - Preferred study times
    - Study place
    - Balanced study distribution
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

def get_study_sessions(schedule):

    return [
        session
        for session in schedule
        if session.get("study_session", False)
    ]


# ============================================================
# HARD CONSTRAINTS
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

    study_sessions = get_study_sessions(schedule)

    violations = 0

    # --------------------------------------------------------
    # Check hard constraint violations
    # --------------------------------------------------------

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

        day = session["day"]

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
    # Check study-session overlaps
    # --------------------------------------------------------

    for i in range(len(study_sessions)):

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

            if first["day"] != second["day"]:
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

    study_sessions = get_study_sessions(schedule)

    soft_constraints = (
        student
        .get("unavailable_periods", {})
        .get("soft_constraints", [])
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

        total_penalty += (
            Schedule_Generation
            .calculate_soft_penalty(
                session["day"],
                start,
                end,
                soft_constraints
            )
        )

    # Each soft conflict has a penalty of 3.
    maximum_penalty = (
        len(study_sessions) * 3
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

    return max(0, score)


# ============================================================
# PREFERRED STUDY TIME SCORE
# ============================================================

def calculate_preferred_time_score(
    schedule,
    student
):

    study_sessions = get_study_sessions(schedule)

    preferred_times = (
        student
        .get("study_preferences", {})
        .get("preferred_study_times", [])
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

    study_sessions = get_study_sessions(schedule)

    study_place = (
        student
        .get("study_preferences", {})
        .get("study_place", "Either")
    )

    if not study_sessions:
        return 100

    total_score = 0

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

        # Convert -3 ... +3 into 0 ... 6
        normalized_score = score + 3

        total_score += normalized_score

    maximum_score = (
        6 * len(study_sessions)
    )

    if maximum_score == 0:
        return 100

    return (
        total_score
        / maximum_score
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

    study_sessions = get_study_sessions(schedule)

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
    # Compare actual study time with target study time
    # --------------------------------------------------------

    total_difference = 0
    total_target = 0

    for day in Schedule_Generation.DAYS:

        target = daily_targets[day]
        actual = daily_hours[day]

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
    # 1. HARD CONSTRAINTS
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
    # 2. SOFT CONSTRAINTS
    # --------------------------------------------------------

    soft_score = (
        calculate_soft_constraint_score(
            schedule,
            student
        )
    )

    # --------------------------------------------------------
    # 3. PREFERRED STUDY TIMES
    # --------------------------------------------------------

    preferred_score = (
        calculate_preferred_time_score(
            schedule,
            student
        )
    )

    # --------------------------------------------------------
    # 4. STUDY PLACE
    # --------------------------------------------------------

    place_score = (
        calculate_study_place_score(
            schedule,
            student,
            university_schedule
        )
    )

    # --------------------------------------------------------
    # 5. BALANCE
    # --------------------------------------------------------

    balance_score = (
        calculate_balance_score(
            schedule,
            student,
            allocations
        )
    )

    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    final_score = (

        (
            hard_score
            * HARD_CONSTRAINT_WEIGHT
        ) / 100

        +

        (
            soft_score
            * SOFT_CONSTRAINT_WEIGHT
        ) / 100

        +

        (
            preferred_score
            * PREFERRED_TIME_WEIGHT
        ) / 100

        +

        (
            place_score
            * STUDY_PLACE_WEIGHT
        ) / 100

        +

        (
            balance_score
            * BALANCE_WEIGHT
        ) / 100
    )

    return final_score


# ============================================================
# RANK AND SELECT BEST SCHEDULE
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

    scored_schedules = []

    # --------------------------------------------------------
    # Evaluate every schedule
    # --------------------------------------------------------

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

        scored_schedules.append(
            {
                "schedule_number": index,
                "score": score,
                "schedule": schedule
            }
        )

    # --------------------------------------------------------
    # Rank schedules from highest score to lowest score
    # --------------------------------------------------------

    scored_schedules.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # --------------------------------------------------------
    # Best schedule is now first
    # --------------------------------------------------------

    best = scored_schedules[0]

    return {
        "schedule": best["schedule"],
        "score": best["score"],
        "schedule_number": best["schedule_number"]
    }


# ============================================================
# DISPLAY ONLY BEST SCHEDULE
# ============================================================

def display_best_schedule(result):

    print("\n")
    print("=" * 70)
    print("TASK 5 - SCHEDULE OPTIMIZATION")
    print("=" * 70)

    print(
        f"\nBest Schedule: "
        f"Schedule #{result['schedule_number']}"
    )

    print(
        f"Optimization Score: "
        f"{result['score']:.2f}/100"
    )

    print("\n")
    print("=" * 70)
    print("BEST SCHEDULE")
    print("=" * 70)

    Schedule_Generation.print_schedule(
        result["schedule"]
    )


# ============================================================
# MAIN TEST
# ============================================================

# ==========================================================
# MAIN TEST
# ==========================================================
if __name__ == "__main__":

    # ------------------------------------------------------
    # Load dummy student data
    # ------------------------------------------------------
    with open("data/dummy_data.json", "r", encoding="utf-8") as file:
        students = json.load(file)

    # First student from dummy_data.json
    student = students[0]

    print("\n========================================")
    print("TASK 5 - SCHEDULE OPTIMIZATION")
    print("========================================")

    print(f"Student: {student['name']}")
    print(f"Student ID: {student['student_id']}")

    # ------------------------------------------------------
    # Task 2 -> Task 3
    # ------------------------------------------------------
    allocations = (
        Schedule_Generation
        .get_allocations_from_task3(student)
    )

    # ------------------------------------------------------
    # Load university schedule
    # ------------------------------------------------------
    with open(
        "data/schedule.json",
        "r",
        encoding="utf-8"
    ) as file:

        university_data = json.load(file)

    # ------------------------------------------------------
    # Get student's assigned university schedule
    # ------------------------------------------------------
    university_schedule = (
        Schedule_Generation
        .get_student_schedule(
            student["student_id"],
            university_data
        )
    )

    if university_schedule is None:

        print(
            "\nNo university schedule found for "
            f"{student['student_id']}."
        )

    else:

        print(
            "\nUniversity Schedule: "
            f"{university_schedule['schedule_id']}"
        )

        # --------------------------------------------------
        # Task 4
        # Generate candidate schedules
        # --------------------------------------------------
        schedules = (
            Schedule_Generation
            .generate_multiple_schedules(
                student,
                university_schedule,
                allocations,
                number_of_schedules=10
            )
        )

        print(
            "\nSchedules received from Task 4: "
            f"{len(schedules)}"
        )

        # --------------------------------------------------
        # Task 5
        # Optimize the schedules
        # --------------------------------------------------
        if not schedules:

            print("\nTask 4 generated no schedules.")
            print("Task 5 cannot optimize anything.")

        else:

            best_result = optimize_schedules(
                schedules,
                student,
                university_schedule,
                allocations
            )

            # ------------------------------------------------
            # Display ONLY the best schedule
            # ------------------------------------------------
            display_best_schedule(best_result)