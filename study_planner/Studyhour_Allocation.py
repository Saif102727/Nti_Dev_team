"""
Study-Hour Allocation
======================

Distributes the student's available study hours across
courses according to the priorities calculated by Task 2.

The authenticated student's ID is passed to Task 2 so the
correct student's data is used throughout the pipeline.
"""

from study_planner import Priority_Calculation

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

    # Task 2 finds the correct student and calculates
    # their course priorities.
    student = (
        Priority_Calculation
        .calculate_student_priorities_by_id(
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
    # 5 weekdays, 2 weekend days
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
# REAL-DATA INTEGRATION
# ============================================================
#
# generate_study_hour_allocations() above is Group A's original Task 3
# code: it pulls student_id -> dummy_data.json's "study_preferences"
# dict (weekday_hours_per_day / weekend_hours_per_day already split).
#
# The real Student record (Login_systemV2.auth_service / model.py)
# instead stores availability as daily_study_hours: a dict keyed by
# exact day name ("Sunday": 3, "Monday": 2, ...). The functions below
# adapt that shape without touching dummy_data.json.

WEEKDAY_NAMES = (
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday",
)
WEEKEND_NAMES = (
    "Friday", "Saturday",
)


def _get_field(student, field, default=None):
    if isinstance(student, dict):
        return student.get(field, default)

    return getattr(student, field, default)


def split_weekday_weekend_hours(daily_study_hours):
    """
    This pipeline (Task 3/4/5, inherited from Group A) is built around a
    single weekday rate + a single weekend rate, not per-day granularity.
    Average the real per-day availability (Sunday-Thursday / Friday-Saturday,
    the Egypt academic week) into that shape.
    """

    daily_study_hours = daily_study_hours or {}

    weekday_values = [
        float(daily_study_hours.get(day, 0) or 0)
        for day in WEEKDAY_NAMES
    ]
    weekend_values = [
        float(daily_study_hours.get(day, 0) or 0)
        for day in WEEKEND_NAMES
    ]

    weekday_hours = (
        sum(weekday_values) / len(WEEKDAY_NAMES)
        if WEEKDAY_NAMES else 0.0
    )
    weekend_hours = (
        sum(weekend_values) / len(WEEKEND_NAMES)
        if WEEKEND_NAMES else 0.0
    )

    return weekday_hours, weekend_hours


def generate_study_hour_allocations_from_real_data(
    student,
    courses,
    academic_events,
    min_hours=1,
    today=None,
    semester_start=None,
):
    """
    Real-data equivalent of generate_study_hour_allocations(): Task 2's
    priorities + Task 3's allocation, driven by the authenticated
    student's real daily_study_hours instead of dummy_data.json.

    Returns (priorities, allocations).
    """

    from datetime import date as _date

    if semester_start is None:
        semester_start = _date(2026, 9, 1)

    priorities = Priority_Calculation.calculate_priorities_for_real_student(
        student,
        courses,
        academic_events,
        today=today,
        semester_start=semester_start,
    )

    courses_for_allocation = [
        {
            "course": priority["course_id"],
            "priority": priority["priority"],
        }
        for priority in priorities
    ]

    daily_study_hours = _get_field(student, "daily_study_hours", {})
    weekday_hours, weekend_hours = split_weekday_weekend_hours(
        daily_study_hours
    )

    allocations = allocate_study_hours(
        courses_for_allocation,
        weekday_hours,
        len(WEEKDAY_NAMES),
        weekend_hours,
        len(WEEKEND_NAMES),
        min_hours,
    )

    return priorities, allocations


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    student_id = "STU-2026-001"

    min_hours = 2

    student, allocations = (
        generate_study_hour_allocations(
            student_id,
            min_hours
        )
    )

    print("\n========================================")
    print("STUDY HOUR ALLOCATION")
    print("========================================")

    for allocation in allocations:
        print(
            f"{allocation['course']}: "
            f"{allocation['allocated_hours']:.2f} hours "
            f"(Priority: {allocation['priority']:.3f})"
        )