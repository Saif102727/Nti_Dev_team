"""
Study-Hour Allocation
======================
STATUS: Not implemented yet.

Intended purpose:
    Distribute a student's available daily study hours across their
    courses proportionally to priority/difficulty, replacing the
    "recommended_time = total_hours / course_count" placeholder currently
    in Main/main.py (Study Plan tab).

Suggested signature:

    def allocate_study_hours(courses, total_hours: float) -> dict:
        # returns {course_id: allocated_hours}
        ...
"""


def allocate_study_hours(courses, weekday_hours, weekdays, weekend_hours, weekend_days, min_hours):

    weekday_total = weekday_hours * weekdays
    weekend_total = weekend_hours * weekend_days

    total_hours = weekday_total + weekend_total
    n = len(courses)
    if n == 0:
        return []
    remaining_hours = total_hours - (n * min_hours)

 
    if remaining_hours < 0:
        raise ValueError(
            "There are not enough available study hours "
            "to give every course its minimum allocation."
        )
    total_priority = sum(course["priority"] for course in courses)

    allocations = []

    for course in courses:

        if total_priority == 0:
            priority_share = 0
        else:
            priority_share = course["priority"] / total_priority

        allocated_hours = min_hours + (
            remaining_hours * priority_share
        )

        allocations.append({
            "course": course["course"],
            "priority": course["priority"],
            "allocated_hours": allocated_hours
        })

    return allocations

courses = [
    {"course": "Math", "priority": 0.30},
    {"course": "Physics", "priority": 0.20},
    {"course": "Programming", "priority": 0.20},
    {"course": "Circuits", "priority": 0.20},
    {"course": "Electronics", "priority": 0.10}
]

allocations = allocate_study_hours(
    courses,
    weekday_hours=2,
    weekdays=4,
    weekend_hours=0,
    weekend_days=2,
    min_hours=2
)

print(allocations)