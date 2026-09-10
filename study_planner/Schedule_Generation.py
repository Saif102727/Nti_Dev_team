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
from pathlib import Path
from study_planner import Priority_Calculation
from study_planner import Studyhour_Allocation


# ==========================================================
# CONSTANTS
# ==========================================================
WEEKDAYS = 5
WEEKEND_DAYS = 2

DAYS = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]

WEEKDAY_NAMES = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
]

WEEKEND_NAMES = [
    "Friday",
    "Saturday",
]

DAY_START = 8 * 60
DAY_END = 22 * 60

# This is a safety limit only.  It prevents an accidental infinite search.
MAX_SEARCH_NODES = 20000
DAILY_FLEXIBILITY_MINUTES = 60

# ==========================================================
# TIME FUNCTIONS
# ==========================================================
def time_to_minutes(time_string):
    hours, minutes = map(int, time_string.split(":"))
    return hours * 60 + minutes


def minutes_to_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def overlaps(start1, end1, start2, end2):
    return start1 < end2 and start2 < end1


# ==========================================================
# HARD CONSTRAINTS
# ==========================================================
def is_slot_available(day, start, end, unavailable):
    for constraint in unavailable:
        if constraint["day"] != day:
            continue

        constraint_start = time_to_minutes(constraint["start"])
        constraint_end = time_to_minutes(constraint["end"])

        if overlaps(
            start,
            end,
            constraint_start,
            constraint_end,
        ):
            return False

    return True


def is_slot_free(day, start, end, schedule):
    for session in schedule:
        if session["day"] != day:
            continue

        session_start = time_to_minutes(session["start"])
        session_end = time_to_minutes(session["end"])

        if overlaps(
            start,
            end,
            session_start,
            session_end,
        ):
            return False

    return True


# ==========================================================
# UNIVERSITY SCHEDULE
# ==========================================================
def get_student_schedule(student_id, university_data):
    """
    Group A's schedule.json uses:

        "student_assignments": {
            "STUDENT_ID": "SCHEDULE_ID"
        }

    Return the schedule assigned to the requested student.
    """
    schedule_id = university_data.get("student_assignments", {}).get(
        student_id
    )

    if schedule_id is None:
        return None

    for schedule in university_data.get("schedules", []):
        if schedule.get("schedule_id") == schedule_id:
            return schedule

    return None


def get_university_sessions(university_schedule):
    """
    Convert Group A's format into Task 4's internal format.

    Group A:
        course_id
        session_type
        start_time
        end_time

    Task 4:
        course
        type
        start
        end
    """
    sessions = []

    if university_schedule is None:
        return sessions

    for session in university_schedule.get("sessions", []):
        sessions.append(
            {
                "day": session["day"],
                "start": session["start_time"],
                "end": session["end_time"],
                "course": session["course_id"],
                "type": session["session_type"],
                "study_session": False,
            }
        )

    return sessions


# ==========================================================
# BUILD HARD CONSTRAINTS
# ==========================================================
def build_hard_constraints(student, university_schedule):
    hard_constraints = []

    student_constraints = (
        student.get("unavailable_periods", {})
        .get("hard_constraints", [])
    )

    for constraint in student_constraints:
        hard_constraints.append(
            {
                "day": constraint["day"],
                "start": constraint["start"],
                "end": constraint["end"],
                "reason": constraint.get("reason", "Unavailable"),
            }
        )

    # University classes are hard constraints too.
    if university_schedule is not None:
        for session in university_schedule.get("sessions", []):
            hard_constraints.append(
                {
                    "day": session["day"],
                    "start": session["start_time"],
                    "end": session["end_time"],
                    "reason": "University class",
                }
            )

    return hard_constraints


# ==========================================================
# SOFT CONSTRAINT SCORE
# ==========================================================
def calculate_soft_penalty(
    day,
    start,
    end,
    soft_constraints,
):
    penalty = 0

    for constraint in soft_constraints:
        if constraint["day"] != day:
            continue

        constraint_start = time_to_minutes(constraint["start"])
        constraint_end = time_to_minutes(constraint["end"])

        if overlaps(
            start,
            end,
            constraint_start,
            constraint_end,
        ):
            penalty += 3

    return penalty


# ==========================================================
# STUDY TIME PREFERENCE SCORE
# ==========================================================
def calculate_preference_score(
    day,
    start,
    end,
    preferred_times,
):
    score = 0

    if not preferred_times:
        return score

    if start >= 8 * 60 and end <= 12 * 60:
        current_time = "Morning"
    elif start >= 12 * 60 and end <= 17 * 60:
        current_time = "Afternoon"
    elif start >= 17 * 60 and end <= 21 * 60:
        current_time = "Evening"
    elif start >= 21 * 60 and end <= 24 * 60:
        current_time = "Night"
    else:
        current_time = None

    for preference in preferred_times:
        if (
            preference["day"] == day
            and preference["time"] == current_time
        ):
            score += 2

    return score


# ==========================================================
# STUDY PLACE SCORE
# ==========================================================
def calculate_study_place_score(
    day,
    start,
    end,
    study_place,
    university_schedule,
):
    if study_place in ("Either", "Both"):
        return 1

    university_gap = False

    if university_schedule is not None:
        day_sessions = []

        for session in university_schedule.get("sessions", []):
            if session["day"] == day:
                day_sessions.append(
                    {
                        "start": time_to_minutes(session["start_time"]),
                        "end": time_to_minutes(session["end_time"]),
                    }
                )

        day_sessions.sort(key=lambda x: x["start"])

        previous_end = DAY_START

        for session in day_sessions:
            if start >= previous_end and end <= session["start"]:
                university_gap = True
                break

            previous_end = max(previous_end, session["end"])

        if start >= previous_end and end <= DAY_END:
            university_gap = True

    if study_place == "University Only":
        return 3 if university_gap else -3

    if study_place == "Home Only":
        return -1 if university_gap else 2

    return 0


# ==========================================================
# SPLIT ALLOCATION INTO STUDY SESSIONS
# ==========================================================
def split_into_sessions(hours, session_minutes=90):
    """
    Split a course allocation into sessions.

    The preferred session length is a preference, not a hard requirement.
    The final session may therefore be shorter.
    """
    total_minutes = round(hours * 60)
    sessions = []

    while total_minutes > 0:
        current_session = min(session_minutes, total_minutes)
        sessions.append(current_session)
        total_minutes -= current_session

    return sessions


# ==========================================================
# DAILY STUDY TARGETS
# ==========================================================
def calculate_daily_targets(student, allocations):
    total_allocated_hours = sum(
        allocation["allocated_hours"]
        for allocation in allocations
    )

    weekday_hours_per_day = student["study_preferences"][
        "weekday_hours_per_day"
    ]
    weekend_hours_per_day = student["study_preferences"][
        "weekend_hours_per_day"
    ]

    weekday_capacity = weekday_hours_per_day * WEEKDAYS
    weekend_capacity = weekend_hours_per_day * WEEKEND_DAYS

    # Use weekday capacity first, then weekend capacity.
    weekday_hours = min(
        total_allocated_hours,
        weekday_capacity,
    )

    remaining_hours = total_allocated_hours - weekday_hours

    weekend_hours = min(
        remaining_hours,
        weekend_capacity,
    )

    daily_targets = {}

    weekday_daily_hours = (
        weekday_hours / WEEKDAYS
        if WEEKDAYS > 0
        else 0
    )

    for day in WEEKDAY_NAMES:
        daily_targets[day] = weekday_daily_hours

    weekend_daily_hours = (
        weekend_hours / WEEKEND_DAYS
        if WEEKEND_DAYS > 0
        else 0
    )

    for day in WEEKEND_NAMES:
        daily_targets[day] = weekend_daily_hours

    return daily_targets


# ==========================================================
# CREATE BASE SCHEDULE
# ==========================================================
def create_base_schedule(university_schedule):
    return get_university_sessions(university_schedule)


# ==========================================================
# FREE INTERVALS
# ==========================================================
def get_free_intervals(day, schedule, hard_constraints):
    """
    Return continuous free intervals between 08:00 and 22:00.

    University classes and hard unavailable periods are treated as occupied.
    """
    occupied = []

    for session in schedule:
        if session["day"] != day:
            continue

        occupied.append(
            (
                time_to_minutes(session["start"]),
                time_to_minutes(session["end"]),
            )
        )

    for constraint in hard_constraints:
        if constraint["day"] != day:
            continue

        occupied.append(
            (
                time_to_minutes(constraint["start"]),
                time_to_minutes(constraint["end"]),
            )
        )

    occupied = [
        (
            max(start, DAY_START),
            min(end, DAY_END),
        )
        for start, end in occupied
        if end > DAY_START and start < DAY_END
    ]

    occupied.sort()

    # Merge overlapping occupied intervals.
    merged = []

    for start, end in occupied:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)

    free_intervals = []
    current = DAY_START

    for start, end in merged:
        if current < start:
            free_intervals.append((current, start))
        current = max(current, end)

    if current < DAY_END:
        free_intervals.append((current, DAY_END))

    return free_intervals


# ==========================================================
# FIND CANDIDATE STUDY SLOTS
# ==========================================================
def find_candidate_slots(
    student,
    university_schedule,
    schedule,
    duration,
    daily_allocated,
    daily_targets,
):
    """
    Generate a SMALL but useful set of candidate positions.

    The old version tested every 30-minute start from 08:00 to 22:00.
    That created a huge recursive search tree.

    This version works with actual free intervals and checks only useful
    packing positions inside those intervals.
    """
    candidates = []

    hard_constraints = build_hard_constraints(
        student,
        university_schedule,
    )

    soft_constraints = (
        student.get("unavailable_periods", {})
        .get("soft_constraints", [])
    )

    preferred_times = (
        student.get("study_preferences", {})
        .get("preferred_study_times", [])
    )

    study_place = (
        student.get("study_preferences", {})
        .get("study_place", "Either")
    )

    for day in DAYS:

        preferred_remaining = (
            daily_targets[day] - daily_allocated[day]
        )

        # Daily study hours are preferences, not hard constraints.
        # Allow Task 4 to borrow up to a small amount of time from
        # another day when necessary to make a feasible schedule.
        maximum_daily_hours = (
            daily_targets[day]
            + DAILY_FLEXIBILITY_MINUTES / 60
        )

        remaining_daily_capacity = (
            maximum_daily_hours - daily_allocated[day]
        )

        if duration > remaining_daily_capacity * 60 + 1e-9:
            continue

        free_intervals = get_free_intervals(
            day,
            schedule,
            hard_constraints,
        )

        for interval_start, interval_end in free_intervals:
            interval_length = interval_end - interval_start

            if duration > interval_length:
                continue

            # Always consider the beginning and end of the free interval.
            possible_starts = {
                interval_start,
                interval_end - duration,
            }

            # Add 30-minute positions inside the interval, but only when
            # useful.  This keeps the search small while still allowing
            # alternative schedules.
            start = interval_start
            while start + duration <= interval_end:
                possible_starts.add(start)
                start += 30

            for start in sorted(possible_starts):
                end = start + duration

                if end > interval_end:
                    continue

                if not is_slot_available(
                    day,
                    start,
                    end,
                    hard_constraints,
                ):
                    continue

                if not is_slot_free(
                    day,
                    start,
                    end,
                    schedule,
                ):
                    continue

                preference_score = calculate_preference_score(
                    day,
                    start,
                    end,
                    preferred_times,
                )

                place_score = calculate_study_place_score(
                    day,
                    start,
                    end,
                    study_place,
                    university_schedule,
                )

                soft_penalty = calculate_soft_penalty(
                    day,
                    start,
                    end,
                    soft_constraints,
                )

                # Prefer using days with more remaining target capacity,
                # but only as a soft preference.
                balance_score = (
                    daily_targets[day] - daily_allocated[day]
                )

                # Prefer earlier positions when scores are otherwise equal.
                early_slot_score = -start / 10000

                total_score = (
                    preference_score
                    + place_score
                    + balance_score
                    - soft_penalty
                    + early_slot_score
                )

                candidates.append(
                    {
                        "day": day,
                        "start": start,
                        "end": end,
                        "score": total_score,
                    }
                )

    candidates.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return candidates


# ==========================================================
# SCHEDULE SIGNATURE
# ==========================================================
def schedule_signature(schedule):
    study_sessions = []

    for session in schedule:
        if not session.get("study_session", False):
            continue

        study_sessions.append(
            (
                session["day"],
                session["start"],
                session["end"],
                session["course"],
            )
        )

    return tuple(sorted(study_sessions))


# ==========================================================
# MOST CONSTRAINED SESSION FIRST SEARCH
# ==========================================================
def _search_schedule(
    student,
    university_schedule,
    sessions_to_place,
    remaining_indices,
    schedule,
    daily_allocated,
    daily_targets,
    generated_schedules,
    signatures,
    max_schedules,
    search_state,
):
    """Backtracking search using MRV (Most Restricted Variable)."""

    # Enough schedules already generated.
    if len(generated_schedules) >= max_schedules:
        return True

    # Safety stop.  This guarantees that the search cannot run forever.
    if search_state["nodes"] >= search_state["max_nodes"]:
        return False

    search_state["nodes"] += 1

    # ------------------------------------------------------
    # BASE CASE
    # ------------------------------------------------------
    if not remaining_indices:
        signature = schedule_signature(schedule)

        if signature not in signatures:
            signatures.add(signature)
            generated_schedules.append(
                [session.copy() for session in schedule]
            )

        return len(generated_schedules) >= max_schedules

    # ------------------------------------------------------
    # TOTAL REMAINING CAPACITY PRUNING
    # ------------------------------------------------------
    remaining_session_minutes = sum(
        sessions_to_place[i][1]
        for i in remaining_indices
    )

    remaining_capacity_minutes = sum(
    max(
        0,
        (
            daily_targets[day]
            + DAILY_FLEXIBILITY_MINUTES / 60
        )
        - daily_allocated[day],
    ) * 60
    for day in DAYS
)

    if remaining_capacity_minutes + 1e-9 < remaining_session_minutes:
        return False

    # ------------------------------------------------------
    # MRV: FIND THE SESSION WITH FEWEST CANDIDATES
    # ------------------------------------------------------
    selected_index = None
    selected_candidates = []

    for session_index in remaining_indices:
        course_name, duration = sessions_to_place[session_index]

        candidates = find_candidate_slots(
            student,
            university_schedule,
            schedule,
            duration,
            daily_allocated,
            daily_targets,
        )

        # No legal slot means this branch is impossible.
        if not candidates:
            return False

        if (
            selected_index is None
            or len(candidates) < len(selected_candidates)
        ):
            selected_index = session_index
            selected_candidates = candidates

    if selected_index is None or not selected_candidates:
        return False

    course_name, duration = sessions_to_place[selected_index]
    duration_hours = duration / 60

    # ------------------------------------------------------
    # TRY CANDIDATES
    # ------------------------------------------------------
    for candidate in selected_candidates:
        if len(generated_schedules) >= max_schedules:
            return True

        if search_state["nodes"] >= search_state["max_nodes"]:
            return False

        day = candidate["day"]
        start = candidate["start"]
        end = candidate["end"]

        study_session = {
            "day": day,
            "start": minutes_to_time(start),
            "end": minutes_to_time(end),
            "course": course_name,
            "type": "Study",
            "study_session": True,
        }

        schedule.append(study_session)
        daily_allocated[day] += duration_hours

        new_remaining_indices = [
            i
            for i in remaining_indices
            if i != selected_index
        ]

        stop_search = _search_schedule(
            student,
            university_schedule,
            sessions_to_place,
            new_remaining_indices,
            schedule,
            daily_allocated,
            daily_targets,
            generated_schedules,
            signatures,
            max_schedules,
            search_state,
        )

        # Backtrack.
        daily_allocated[day] -= duration_hours
        schedule.pop()

        if stop_search:
            return True

    return False


# ==========================================================
# GENERATE MULTIPLE SCHEDULES
# ==========================================================
def generate_multiple_schedules(
    student,
    university_schedule,
    allocations,
    number_of_schedules=10,
):
    # ------------------------------------------------------
    # Calculate daily study targets.
    # ------------------------------------------------------
    daily_targets = calculate_daily_targets(
        student,
        allocations,
    )

    # ------------------------------------------------------
    # Create university-only base schedule.
    # ------------------------------------------------------
    base_schedule = create_base_schedule(
        university_schedule
    )

    # ------------------------------------------------------
    # Track daily study allocation.
    # ------------------------------------------------------
    daily_allocated = {
        day: 0.0
        for day in DAYS
    }

    # ------------------------------------------------------
    # Courses are initially sorted by priority.
    # MRV will decide the actual search order later.
    # ------------------------------------------------------
    sorted_allocations = sorted(
        allocations,
        key=lambda x: x["priority"],
        reverse=True,
    )

    # ------------------------------------------------------
    # Determine session length.
    # ------------------------------------------------------
    preferred_session_minutes = (
        student["study_preferences"]
        .get("preferred_session_minutes", 90)
    )

    weekday_hours = (
        student["study_preferences"]
        .get("weekday_hours_per_day", 0)
    )

    max_weekday_session_minutes = int(
        weekday_hours * 60
    )

    # Preferred length is NOT a hard constraint.
    # If 90 minutes cannot fit into a normal weekday, use the
    # available weekday length (60 minutes in the current test).
    session_minutes = min(
        preferred_session_minutes,
        max_weekday_session_minutes,
    )

    if session_minutes <= 0:
        session_minutes = min(
            preferred_session_minutes,
            int(
                student["study_preferences"].get(
                    "weekend_hours_per_day",
                    1,
                )
                * 60
            ),
        )

    if session_minutes <= 0:
        session_minutes = 60

    # ------------------------------------------------------
    # Create individual study sessions.
    # ------------------------------------------------------
    sessions_to_place = []

    for allocation in sorted_allocations:
        course_name = allocation["course"]
        allocated_hours = allocation["allocated_hours"]

        course_sessions = split_into_sessions(
            allocated_hours,
            session_minutes,
        )

        for duration in course_sessions:
            sessions_to_place.append(
                (
                    course_name,
                    duration,
                )
            )

    # Largest sessions first gives MRV a useful tie-break order.
    sessions_to_place.sort(
        key=lambda x: x[1],
        reverse=True,
    )

    # ------------------------------------------------------
    # Search state.
    # ------------------------------------------------------
    search_state = {
        "nodes": 0,
        "max_nodes": MAX_SEARCH_NODES,
    }

    generated_schedules = []
    signatures = set()

    remaining_indices = list(
        range(len(sessions_to_place))
    )

    # ------------------------------------------------------
    # Start MRV backtracking search.
    # ------------------------------------------------------
    _search_schedule(
        student,
        university_schedule,
        sessions_to_place,
        remaining_indices,
        base_schedule.copy(),
        daily_allocated,
        daily_targets,
        generated_schedules,
        signatures,
        number_of_schedules,
        search_state,
    )

    return generated_schedules


# ==========================================================
# GENERATE ONE SCHEDULE
# ==========================================================
def generate_schedule(
    student,
    university_schedule,
    allocations,
):
    schedules = generate_multiple_schedules(
        student,
        university_schedule,
        allocations,
        number_of_schedules=1,
    )

    if schedules:
        return schedules[0]

    return None


# ==========================================================
# GET ALLOCATIONS FROM TASK 3
# ==========================================================
def get_allocations_from_task3(student):
    # ------------------------------------------------------
    # Task 2: calculate all course priorities.
    # ------------------------------------------------------
    student_with_priorities = (
        Priority_Calculation
        .calculate_student_priorities(student)
    )

    # ------------------------------------------------------
    # Prepare Task 3 input.
    # ------------------------------------------------------
    courses_for_allocation = []

    for course_name, course in (
        student_with_priorities["courses"].items()
    ):
        courses_for_allocation.append(
            {
                "course": course_name,
                "priority": course["priority"],
            }
        )

    # ------------------------------------------------------
    # Student study hours.
    # ------------------------------------------------------
    weekday_hours = (
        student["study_preferences"]
        ["weekday_hours_per_day"]
    )

    weekend_hours = (
        student["study_preferences"]
        ["weekend_hours_per_day"]
    )

    # ------------------------------------------------------
    # Task 3.
    # IMPORTANT: positional arguments match the actual
    # allocate_study_hours() interface used by the project.
    # ------------------------------------------------------
    allocations = (
        Studyhour_Allocation
        .allocate_study_hours(
            courses_for_allocation,
            weekday_hours,
            WEEKDAYS,
            weekend_hours,
            WEEKEND_DAYS,
            1,
        )
    )

    return allocations


# ==========================================================
# PRINT SCHEDULE
# ==========================================================
def print_schedule(schedule):
    if schedule is None:
        print("\nNo feasible schedule found.")
        return

    print("\n==============================")
    print("GENERATED STUDY SCHEDULE")
    print("==============================")

    for day in DAYS:
        day_sessions = [
            session
            for session in schedule
            if session["day"] == day
        ]

        day_sessions.sort(
            key=lambda x: time_to_minutes(x["start"])
        )

        print(f"\n{day}:")

        for session in day_sessions:
            if session.get("study_session", False):
                print(
                    f"  {session['start']} - "
                    f"{session['end']} | "
                    f"{session['course']} | STUDY"
                )
            else:
                print(
                    f"  {session['start']} - "
                    f"{session['end']} | "
                    f"{session['course']} | "
                    f"{session['type']}"
                )


def run_task4(student_id, number_of_schedules=10):

    # ------------------------------------------------------
    # Task 3: calculate study-hour allocations
    # ------------------------------------------------------
    min_hours = 1

    student, allocations = (
        Studyhour_Allocation
        .generate_study_hour_allocations(
            student_id,
            min_hours
        )
    )

    # ------------------------------------------------------
    # Load university schedule data
    # ------------------------------------------------------
    with open(
        "data/schedule.json",
        "r",
        encoding="utf-8"
    ) as file:
        university_data = json.load(file)

    # ------------------------------------------------------
    # Get this student's university schedule
    # ------------------------------------------------------
    university_schedule = get_student_schedule(
        student_id,
        university_data
    )

    if university_schedule is None:
        raise ValueError(
            f"No university schedule found for {student_id}."
        )

    # ------------------------------------------------------
    # Generate multiple schedules
    # ------------------------------------------------------
    schedules = generate_multiple_schedules(
        student,
        university_schedule,
        allocations,
        number_of_schedules=number_of_schedules
    )

    return student, schedules

# ==========================================================
# REAL-DATA INTEGRATION
# ==========================================================
#
# run_task4() above is Group A's original Task 4 entry point: it looks
# a student_id up in data/schedule.json's "student_assignments" map,
# which only lists Group A's own sample students (STU-2026-001, ...).
# Real accounts created through Login_systemV2 get a fresh
# STU-<uuid> id that was never assigned a schedule there, and their
# study preferences live on the real Student record, not
# dummy_data.json's "study_preferences" dict.
#
# The functions below reuse every scheduling function above unchanged
# (time math, constraint checks, the MRV backtracking search) and only
# replace how the *inputs* to that search are built.

DEFAULT_UNIVERSITY_SCHEDULE_FILE = (
    Path(__file__).resolve().parent.parent / "data" / "schedule.json"
)


def load_default_university_schedule(schedule_file=None):
    """
    Real accounts aren't assigned one of Group A's sample schedules, so —
    the same way loader.load_courses_and_events() treats the course
    catalog as shared across every student — fall back to the first
    shared class timetable in data/schedule.json.
    """

    path = schedule_file or DEFAULT_UNIVERSITY_SCHEDULE_FILE

    with open(path, "r", encoding="utf-8") as file:
        university_data = json.load(file)

    schedules = university_data.get("schedules", [])

    return schedules[0] if schedules else None


def infer_study_place(student):
    """
    The real Student record stores a free-text preferred_study_location
    (e.g. "Home", "Library"), not this pipeline's "University Only" /
    "Home Only" / "Either" categories. Map it with a simple keyword
    guess and fall back to the neutral "Either".
    """

    if isinstance(student, dict):
        location = student.get("preferred_study_location", "") or ""
    else:
        location = getattr(student, "preferred_study_location", "") or ""

    location = location.lower()

    if any(word in location for word in ("univ", "campus", "college", "faculty")):
        return "University Only"

    if any(word in location for word in ("home", "house", "dorm")):
        return "Home Only"

    return "Either"


def build_pseudo_student(student, weekday_hours, weekend_hours):
    """
    generate_multiple_schedules()/optimize_schedules() expect a
    student["study_preferences"] dict (Group A's shape). Build a minimal
    one from real data so the rest of the pipeline doesn't need to
    change.
    """

    student_id = (
        student.get("student_id", "")
        if isinstance(student, dict)
        else getattr(student, "student_id", "")
    )

    return {
        "student_id": student_id,
        "study_preferences": {
            "weekday_hours_per_day": weekday_hours,
            "weekend_hours_per_day": weekend_hours,
            "preferred_session_minutes": 90,
            # No time-of-day or study-place preference is collected by
            # the login/registration forms yet, beyond
            # preferred_study_location -> infer_study_place().
            "preferred_study_times": [],
            "study_place": infer_study_place(student),
        },
        # No "unavailable periods" (personal commitments) are collected
        # yet either; only real hard constraint is the university
        # timetable itself, already handled via `university_schedule`.
        "unavailable_periods": {
            "hard_constraints": [],
            "soft_constraints": [],
        },
    }


def run_task4_from_real_data(
    student,
    courses,
    academic_events,
    number_of_schedules=5,
    min_hours=1,
    today=None,
    semester_start=None,
    university_schedule=None,
):
    """
    Real-data equivalent of run_task4(): Task 3's allocations feed the
    same MRV backtracking search generate_multiple_schedules() uses,
    driven by the authenticated student + shared catalog instead of
    dummy_data.json / a student_id lookup.

    Returns (pseudo_student, schedules, allocations, priorities).
    """

    priorities, allocations = (
        Studyhour_Allocation
        .generate_study_hour_allocations_from_real_data(
            student,
            courses,
            academic_events,
            min_hours=min_hours,
            today=today,
            semester_start=semester_start,
        )
    )

    daily_study_hours = (
        student.get("daily_study_hours", {})
        if isinstance(student, dict)
        else getattr(student, "daily_study_hours", {})
    )

    weekday_hours, weekend_hours = (
        Studyhour_Allocation.split_weekday_weekend_hours(
            daily_study_hours
        )
    )

    pseudo_student = build_pseudo_student(
        student,
        weekday_hours,
        weekend_hours,
    )

    if university_schedule is None:
        university_schedule = load_default_university_schedule()

    schedules = generate_multiple_schedules(
        pseudo_student,
        university_schedule,
        allocations,
        number_of_schedules=number_of_schedules,
    )

    return pseudo_student, schedules, allocations, priorities


# ==========================================================
# MAIN TEST
# ==========================================================

if __name__ == "__main__":
    student_id = "STU-2026-001"

    student, schedules = run_task4(
        student_id,
        number_of_schedules=10
    )

    print(f"Generated {len(schedules)} schedules.")