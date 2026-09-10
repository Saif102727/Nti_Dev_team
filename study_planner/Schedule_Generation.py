"""
Schedule Generation
======================
STATUS: Not implemented yet.

Intended purpose:
    Build a concrete day-by-day study schedule for a student by combining:
      - Student.daily_study_hours / free_days (see model.py)
      - Course priorities (see Priority_Calculation.py)
      - Existing class Sessions and free-time gaps
        (see dataclass/schedule.py -> Schedule.calculate_gaps)

Suggested signature:

    def generate_schedule(student, courses, academic_events) -> dict:
        ...
"""

# import auth_service
"""
Schedule Generation
===================

Task 4:
    Generate multiple feasible weekly study schedules.

Hard constraints:
    - University classes
    - Student hard constraints
    - No overlapping study sessions
    - Daily allocated-hour limits

Task 5 will evaluate the generated schedules and
select the best one.
"""

import json

import Priority_Calculation
import Studyhour_Allocation


# ============================================================
# CONSTANTS
# ============================================================

WEEKDAYS = 5
WEEKEND_DAYS = 2

DAYS = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday"
]

WEEKDAY_NAMES = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday"
]

WEEKEND_NAMES = [
    "Friday",
    "Saturday"
]


# ============================================================
# TIME HELPERS
# ============================================================

def time_to_minutes(time_string):

    hours, minutes = map(
        int,
        time_string.split(":")
    )

    return hours * 60 + minutes


def minutes_to_time(minutes):

    hours = minutes // 60
    mins = minutes % 60

    return f"{hours:02d}:{mins:02d}"


def overlaps(start1, end1, start2, end2):

    return start1 < end2 and start2 < end1


# ============================================================
# HARD CONSTRAINTS
# ============================================================

def is_slot_available(
    day,
    start,
    end,
    unavailable
):

    for period in unavailable:

        if period["day"] != day:
            continue

        blocked_start = time_to_minutes(
            period["start"]
        )

        blocked_end = time_to_minutes(
            period["end"]
        )

        if overlaps(
            start,
            end,
            blocked_start,
            blocked_end
        ):
            return False

    return True


def is_slot_free(
    day,
    start,
    end,
    schedule
):

    for session in schedule:

        if session["day"] != day:
            continue

        existing_start = time_to_minutes(
            session["start"]
        )

        existing_end = time_to_minutes(
            session["end"]
        )

        if overlaps(
            start,
            end,
            existing_start,
            existing_end
        ):
            return False

    return True


# ============================================================
# UNIVERSITY SCHEDULE
# ============================================================

def get_student_schedule(
    student_id,
    university_data
):

    assignments = university_data[
        "student_assignments"
    ]

    schedule_id = assignments.get(
        student_id
    )

    if schedule_id is None:

        raise ValueError(
            f"No university schedule found "
            f"for student {student_id}"
        )

    for schedule in university_data[
        "schedules"
    ]:

        if schedule["schedule_id"] == schedule_id:

            return schedule

    raise ValueError(
        f"Schedule {schedule_id} "
        f"was not found."
    )


def get_university_sessions(
    university_schedule
):

    sessions = []

    for session in university_schedule[
        "sessions"
    ]:

        sessions.append({
            "day": session["day"],
            "start": session["start_time"],
            "end": session["end_time"],
            "course": session["course_id"],
            "type": session["session_type"]
        })

    return sessions


# ============================================================
# CREATE HARD CONSTRAINT LIST
# ============================================================

def build_hard_constraints(
    student,
    university_schedule
):

    hard_constraints = []

    # --------------------------------------------------------
    # Student hard constraints
    # --------------------------------------------------------

    unavailable_periods = student[
        "unavailable_periods"
    ].get(
        "hard_constraints",
        []
    )

    for period in unavailable_periods:

        hard_constraints.append({
            "day": period["day"],
            "start": period["start"],
            "end": period["end"],
            "reason": period.get(
                "reason",
                "Student unavailable"
            )
        })

    # --------------------------------------------------------
    # University classes
    # --------------------------------------------------------

    for session in university_schedule[
        "sessions"
    ]:

        hard_constraints.append({
            "day": session["day"],
            "start": session["start_time"],
            "end": session["end_time"],
            "reason": (
                f"University "
                f"{session['session_type']}: "
                f"{session['course_id']}"
            )
        })

    return hard_constraints


# ============================================================
# SOFT CONSTRAINT SCORE
# ============================================================

def calculate_soft_penalty(
    day,
    start,
    end,
    soft_constraints
):

    penalty = 0

    for period in soft_constraints:

        if period["day"] != day:
            continue

        blocked_start = time_to_minutes(
            period["start"]
        )

        blocked_end = time_to_minutes(
            period["end"]
        )

        if overlaps(
            start,
            end,
            blocked_start,
            blocked_end
        ):

            penalty += 1

    return penalty


# ============================================================
# PREFERRED STUDY TIME
# ============================================================

def calculate_preference_score(
    day,
    start,
    end,
    preferred_times
):

    if not preferred_times:
        return 0

    score = 0

    preferred_ranges = {

        "Morning": (
            8 * 60,
            12 * 60
        ),

        "Afternoon": (
            12 * 60,
            17 * 60
        ),

        "Evening": (
            17 * 60,
            21 * 60
        ),

        "Night": (
            21 * 60,
            24 * 60
        )
    }

    for preference in preferred_times:

        if preference["day"] != day:
            continue

        preferred_time = preference["time"]

        if preferred_time not in preferred_ranges:
            continue

        preferred_start, preferred_end = (
            preferred_ranges[preferred_time]
        )

        if (
            start >= preferred_start
            and end <= preferred_end
        ):

            score += 2

    return score


# ============================================================
# STUDY PLACE SCORE
# ============================================================

def calculate_study_place_score(
    day,
    start,
    end,
    study_place,
    university_schedule
):

    university_gap = False

    for gap in university_schedule.get(
        "gaps",
        []
    ):

        if gap["day"] != day:
            continue

        gap_start = time_to_minutes(
            gap["start_time"]
        )

        gap_end = time_to_minutes(
            gap["end_time"]
        )

        if (
            start >= gap_start
            and end <= gap_end
        ):

            university_gap = True
            break

    # --------------------------------------------------------
    # University Only
    # --------------------------------------------------------

    if study_place == "University Only":

        if university_gap:
            return 3

        return -3

    # --------------------------------------------------------
    # Home Only
    # --------------------------------------------------------

    if study_place == "Home Only":

        if university_gap:
            return -1

        return 2

    # --------------------------------------------------------
    # University or Home
    # --------------------------------------------------------

    if study_place in [
        "University or Home",
        "Both",
        "Either"
    ]:

        return 1

    return 0


# ============================================================
# SESSION SPLITTING
# ============================================================

def split_into_sessions(
    hours,
    session_minutes=90
):

    total_minutes = int(
        round(hours * 60)
    )

    sessions = []

    while total_minutes > 0:

        current_minutes = min(
            session_minutes,
            total_minutes
        )

        sessions.append(
            current_minutes
        )

        total_minutes -= current_minutes

    return sessions


# ============================================================
# DAILY TARGET HOURS
# ============================================================

def calculate_daily_targets(
    student,
    allocations
):

    total_allocated_hours = sum(
        allocation["allocated_hours"]
        for allocation in allocations
    )

    weekday_hours_per_day = student[
        "study_preferences"
    ]["weekday_hours_per_day"]

    # --------------------------------------------------------
    # Egypt:
    # Sunday -> Thursday = weekdays
    # Friday + Saturday = weekend
    # --------------------------------------------------------

    weekday_capacity = (
        weekday_hours_per_day
        * WEEKDAYS
    )

    weekday_hours = min(
        total_allocated_hours,
        weekday_capacity
    )

    weekend_hours = (
        total_allocated_hours
        - weekday_hours
    )

    friday_hours = weekend_hours / 2
    saturday_hours = weekend_hours / 2

    daily_targets = {

        "Sunday":
            weekday_hours / WEEKDAYS,

        "Monday":
            weekday_hours / WEEKDAYS,

        "Tuesday":
            weekday_hours / WEEKDAYS,

        "Wednesday":
            weekday_hours / WEEKDAYS,

        "Thursday":
            weekday_hours / WEEKDAYS,

        "Friday":
            friday_hours,

        "Saturday":
            saturday_hours
    }

    return daily_targets


# ============================================================
# CREATE BASE SCHEDULE
# ============================================================

def create_base_schedule(
    university_schedule
):

    schedule = []

    for session in university_schedule[
        "sessions"
    ]:

        schedule.append({

            "day":
                session["day"],

            "start":
                session["start_time"],

            "end":
                session["end_time"],

            "course":
                session["course_id"],

            "type":
                session["session_type"],

            "study_session":
                False
        })

    return schedule


# ============================================================
# FIND CANDIDATE SLOTS
# ============================================================

def find_candidate_slots(
    student,
    university_schedule,
    schedule,
    duration,
    daily_allocated,
    daily_targets
):

    candidates = []

    hard_constraints = build_hard_constraints(
        student,
        university_schedule
    )

    soft_constraints = student[
        "unavailable_periods"
    ].get(
        "soft_constraints",
        []
    )

    preferred_times = student[
        "study_preferences"
    ].get(
        "preferred_study_times",
        []
    )

    study_place = student[
        "study_preferences"
    ].get(
        "study_place",
        ""
    )

    day_start = 8 * 60
    day_end = 22 * 60

    duration_hours = duration / 60

    for day in DAYS:

        remaining_target = (
            daily_targets[day]
            - daily_allocated[day]
        )

        if duration_hours > remaining_target:
            continue

        current = day_start

        while current + duration <= day_end:

            start = current
            end = current + duration

            # ------------------------------------------------
            # HARD CONSTRAINT
            # ------------------------------------------------

            if not is_slot_available(
                day,
                start,
                end,
                hard_constraints
            ):

                current += 30
                continue

            # ------------------------------------------------
            # HARD CONSTRAINT:
            # no overlap with existing schedule
            # ------------------------------------------------

            if not is_slot_free(
                day,
                start,
                end,
                schedule
            ):

                current += 30
                continue

            # ------------------------------------------------
            # SOFT CONSTRAINT
            # ------------------------------------------------

            soft_penalty = (
                calculate_soft_penalty(
                    day,
                    start,
                    end,
                    soft_constraints
                )
            )

            # ------------------------------------------------
            # PREFERRED TIME
            # ------------------------------------------------

            preference_score = (
                calculate_preference_score(
                    day,
                    start,
                    end,
                    preferred_times
                )
            )

            # ------------------------------------------------
            # STUDY PLACE
            # ------------------------------------------------

            study_place_score = (
                calculate_study_place_score(
                    day,
                    start,
                    end,
                    study_place,
                    university_schedule
                )
            )

            # ------------------------------------------------
            # BALANCE
            # ------------------------------------------------

            target = daily_targets[day]

            if target > 0:

                usage_ratio = (
                    daily_allocated[day]
                    / target
                )

            else:

                usage_ratio = 1

            balance_score = (
                2 * (1 - usage_ratio)
            )

            # ------------------------------------------------
            # LOCAL SLOT SCORE
            #
            # Task 4 only uses this to order candidates.
            # Task 5 makes the FINAL decision.
            # ------------------------------------------------

            local_score = (
                preference_score
                + study_place_score
                + balance_score
                - soft_penalty
            )

            candidates.append({

                "day": day,

                "start": start,

                "end": end,

                "score": local_score
            })

            current += 30

    candidates.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return candidates


# ============================================================
# SCHEDULE SIGNATURE
# ============================================================

def schedule_signature(schedule):

    study_sessions = []

    for session in schedule:

        if not session.get(
            "study_session",
            False
        ):
            continue

        study_sessions.append(
            (
                session["day"],
                session["start"],
                session["end"],
                session["course"]
            )
        )

    return tuple(
        sorted(study_sessions)
    )


# ============================================================
# GENERATE ONE FEASIBLE SCHEDULE USING BACKTRACKING
# ============================================================

def _search_schedule(
    student,
    university_schedule,
    sessions_to_place,
    index,
    schedule,
    daily_allocated,
    daily_targets,
    generated_schedules,
    signatures,
    max_schedules,
    search_state
):
    # ========================================================
    # STOP CONDITIONS
    # ========================================================

    # We already have enough schedules
    if len(generated_schedules) >= max_schedules:
        return True

    # Safety limit so the algorithm can NEVER run forever
    if search_state["nodes"] >= search_state["max_nodes"]:
        return False

    search_state["nodes"] += 1

    # ========================================================
    # ALL SESSIONS HAVE BEEN PLACED
    # ========================================================

    if index >= len(sessions_to_place):

        signature = schedule_signature(schedule)

        if signature not in signatures:
            signatures.add(signature)

            generated_schedules.append(
                [session.copy() for session in schedule]
            )

        return (
            len(generated_schedules) >= max_schedules
        )

    # ========================================================
    # CURRENT SESSION
    # ========================================================

    course_name, duration = sessions_to_place[index]

    # ========================================================
    # FIND FEASIBLE CANDIDATES
    # ========================================================

    candidates = find_candidate_slots(
        student,
        university_schedule,
        schedule,
        duration,
        daily_allocated,
        daily_targets
    )

    if not candidates:
        print(
            f"\nNO CANDIDATES:"
            f" {course_name}"
            f" - {duration} minutes"
            f" - session {index + 1}/"
            f"{len(sessions_to_place)}"
    )
    # ========================================================
    # IMPORTANT:
    # Don't explore hundreds of possible slots.
    # Only try the best few.
    # ========================================================

    MAX_CANDIDATES_PER_SESSION = 8

    candidates = candidates[
        :MAX_CANDIDATES_PER_SESSION
    ]

    # ========================================================
    # TRY EACH CANDIDATE
    # ========================================================

    for candidate in candidates:

        if len(generated_schedules) >= max_schedules:
            return True

        if (
            search_state["nodes"]
            >= search_state["max_nodes"]
        ):
            return False

        day = candidate["day"]
        start = candidate["start"]
        end = candidate["end"]

        duration_hours = duration / 60

        # ====================================================
        # CREATE STUDY SESSION
        # ====================================================

        study_session = {
            "day": day,
            "start": minutes_to_time(start),
            "end": minutes_to_time(end),
            "course": course_name,
            "type": "Study",
            "study_session": True
        }

        # ====================================================
        # ADD SESSION
        # ====================================================

        schedule.append(study_session)

        daily_allocated[day] += duration_hours

        # ====================================================
        # RECURSIVE SEARCH
        # ====================================================

        stop_search = _search_schedule(
            student,
            university_schedule,
            sessions_to_place,
            index + 1,
            schedule,
            daily_allocated,
            daily_targets,
            generated_schedules,
            signatures,
            max_schedules,
            search_state
        )

        # ====================================================
        # BACKTRACK
        # ====================================================

        daily_allocated[day] -= duration_hours

        schedule.pop()

        if stop_search:
            return True

    return False


# ============================================================
# GENERATE MULTIPLE FEASIBLE SCHEDULES
# ============================================================

def generate_multiple_schedules(
    student,
    allocations,
    university_schedule,
    number_of_schedules=10
):

    # --------------------------------------------------------
    # Daily target hours
    # --------------------------------------------------------

    daily_targets = calculate_daily_targets(
        student,
        allocations
    )

    # --------------------------------------------------------
    # Start with university classes.
    # --------------------------------------------------------

    base_schedule = create_base_schedule(
        university_schedule
    )

    # --------------------------------------------------------
    # Sort courses by priority.
    #
    # Higher priority courses are placed first because
    # they are more important and should get the first
    # opportunity to obtain available slots.
    # --------------------------------------------------------

    sorted_allocations = sorted(
        allocations,
        key=lambda x: x["priority"],
        reverse=True
    )

    # --------------------------------------------------------
    # Convert course allocations into study sessions.
    # --------------------------------------------------------

    sessions_to_place = []

    session_minutes = student[
        "study_preferences"
    ].get(
        "preferred_session_minutes",
        90
    )

    for allocation in sorted_allocations:

        course_name = allocation[
            "course"
        ]

        allocated_hours = allocation[
            "allocated_hours"
        ]

        session_lengths = split_into_sessions(
            allocated_hours,
            session_minutes
        )

        for duration in session_lengths:

            sessions_to_place.append(
                (
                    course_name,
                    duration
                )
            )

    # --------------------------------------------------------
    # Generate multiple schedules.
    # --------------------------------------------------------

    generated_schedules = []

    signatures = set()

    daily_allocated = {
        day: 0
        for day in DAYS
    }

    search_state = {
        "nodes": 0,
        "max_nodes": 5000
    }

    _search_schedule(
        student,
        university_schedule,
        sessions_to_place,
        0,
        base_schedule.copy(),
        daily_allocated,
        daily_targets,
        generated_schedules,
        signatures,
        number_of_schedules,
        search_state
    )

    print("\nDAILY TARGETS:")

    for day, hours in daily_targets.items():
        print(f"{day}: {hours:.2f} hours")

    print(
        f"\nTOTAL ALLOCATED: "
        f"{sum(a['allocated_hours'] for a in allocations):.2f} hours"
    )


    # --------------------------------------------------------
    # If no schedule exists, return empty list.
    # --------------------------------------------------------

    return generated_schedules


# ============================================================
# BACKWARD-COMPATIBLE SINGLE SCHEDULE FUNCTION
# ============================================================

def generate_schedule(
    student,
    allocations,
    university_schedule
):

    schedules = generate_multiple_schedules(
        student,
        allocations,
        university_schedule,
        number_of_schedules=1
    )

    if not schedules:

        raise ValueError(
            "No feasible schedule could be generated."
        )

    return schedules[0]


# ============================================================
# PRINT ONE SCHEDULE
# ============================================================

def print_schedule(schedule):

    print("\n")
    print("=" * 65)
    print("GENERATED WEEKLY STUDY SCHEDULE")
    print("=" * 65)

    current_day = None

    for session in schedule:

        if session["day"] != current_day:

            current_day = session["day"]

            print(
                f"\n--- {current_day} ---"
            )

        session_type = session[
            "type"
        ]

        print(
            f"{session['start']} - "
            f"{session['end']} | "
            f"{session['course']} "
            f"({session_type})"
        )

    print("\n" + "=" * 65)


# ============================================================
# PRINT MULTIPLE SCHEDULES
# ============================================================

def print_multiple_schedules(
    schedules
):

    for index, schedule in enumerate(
        schedules,
        start=1
    ):

        print("\n")
        print("#" * 70)
        print(
            f"FEASIBLE SCHEDULE #{index}"
        )
        print("#" * 70)

        print_schedule(
            schedule
        )


# ============================================================
# PREPARE TASK 3 ALLOCATIONS
# ============================================================

def get_allocations_from_task3(
    student
):

    # --------------------------------------------------------
    # Task 2
    # --------------------------------------------------------

    student = (
        Priority_Calculation
        .calculate_student_priorities(
            student
        )
    )

    # --------------------------------------------------------
    # Prepare courses for Task 3
    # --------------------------------------------------------

    courses = (
        Studyhour_Allocation
        .prepare_courses_from_Priority_Calculation(
            student
        )
    )

    weekday_hours = student[
        "study_preferences"
    ][
        "weekday_hours_per_day"
    ]

    weekend_hours = student[
        "study_preferences"
    ][
        "weekend_hours_per_day"
    ]

    # --------------------------------------------------------
    # Egypt:
    # Sunday -> Thursday = 5 weekdays
    # Friday + Saturday = 2 weekend days
    # --------------------------------------------------------

    weekdays = 5
    weekend_days = 2

    # Algorithm parameter.
    min_hours = 1

    allocations = (
        Studyhour_Allocation
        .allocate_study_hours(

            courses,

            weekday_hours,

            weekdays,

            weekend_hours,

            weekend_days,

            min_hours
        )
    )

    return student, allocations


# ============================================================
# TEST 1
# FIRST STUDENT
# ============================================================

if __name__ == "__main__":

    print("\n")
    print("=" * 65)
    print("TEST 1 - FIRST STUDENT")
    print("=" * 65)

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
        get_allocations_from_task3(
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
    # Find student's university schedule
    # --------------------------------------------------------

    university_schedule = (
        get_student_schedule(
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
    # Task 3 allocations
    # --------------------------------------------------------

    print(
        "\nALLOCATED STUDY HOURS"
    )

    for allocation in allocations:

        print(
            f"{allocation['course']}: "
            f"{allocation['allocated_hours']:.2f} "
            f"hours "
            f"(Priority: "
            f"{allocation['priority']:.3f})"
        )

    # --------------------------------------------------------
    # Task 4
    # Generate multiple feasible schedules
    # --------------------------------------------------------

    schedules = (
        generate_multiple_schedules(

            student,

            allocations,

            university_schedule,

            number_of_schedules=1
        )
    )

    print(
        f"\nGenerated "
        f"{len(schedules)} "
        f"feasible schedules."
    )

    print_multiple_schedules(
        schedules
    )


# ============================================================
# TEST 2
# AUTHENTICATION
# ============================================================

# if __name__ == "__main__":

#     print("\n")
#     print("=" * 65)
#     print("TEST 2 - AUTHENTICATED STUDENT")
#     print("=" * 65)

#     # --------------------------------------------------------
#     # TEST LOGIN CREDENTIALS
#     # --------------------------------------------------------
#     #
#     # Replace these with a test account that exists
#     # in your authentication database.
#     #

#     username = input(
#         "\nEnter username: "
#     )

#     password = input(
#         "Enter password: "
#     )

#     # --------------------------------------------------------
#     # AUTHENTICATE
#     # --------------------------------------------------------

#     authenticated_data = (
#         auth_service.authenticate(
#             username,
#             password
#         )
#     )

#     # --------------------------------------------------------
#     # Check login
#     # --------------------------------------------------------

#     if not authenticated_data:

#         print(
#             "\nAuthentication failed."
#         )

#     else:

#         student_id = authenticated_data[
#             "student_id"
#         ]

#         print(
#             f"\nAuthenticated student: "
#             f"{authenticated_data['name']}"
#         )

#         print(
#             f"Student ID: {student_id}"
#         )

#         # ----------------------------------------------------
#         # Load Group A dummy data
#         # ----------------------------------------------------

#         with open(
#             "data/dummy_data.json",
#             "r"
#         ) as file:

#             students = json.load(file)

#         # ----------------------------------------------------
#         # Find the authenticated student's actual
#         # Group A record using student_id.
#         # ----------------------------------------------------

#         student = None

#         for record in students:

#             if record["student_id"] == student_id:

#                 student = record
#                 break

#         if student is None:

#             print(
#                 f"\nStudent {student_id} "
#                 f"was not found in dummy_data.json."
#             )

#         else:

#             # ----------------------------------------------
#             # Task 2 -> Task 3
#             # ----------------------------------------------

#             student, allocations = (
#                 get_allocations_from_task3(
#                     student
#                 )
#             )

#             # ----------------------------------------------
#             # Load university schedule
#             # ----------------------------------------------

#             with open(
#                 "data/university_schedule.json",
#                 "r"
#             ) as file:

#                 university_data = json.load(file)

#             # ----------------------------------------------
#             # Get student's assigned schedule
#             # ----------------------------------------------

#             university_schedule = (
#                 get_student_schedule(
#                     student_id,
#                     university_data
#                 )
#             )

#             print(
#                 f"\nUniversity Schedule: "
#                 f"{university_schedule['schedule_id']}"
#             )

#             # ----------------------------------------------
#             # Generate Task 4 schedule
#             # ----------------------------------------------

#             schedule = generate_schedule(
#                 student,
#                 allocations,
#                 university_schedule
#             )

#             print_schedule(schedule)