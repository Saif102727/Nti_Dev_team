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


# def allocate_study_hours(courses, weekday_hours, weekdays, weekend_hours, weekend_days, min_hours):

#     weekday_total = weekday_hours * weekdays
#     weekend_total = weekend_hours * weekend_days

#     total_hours = weekday_total + weekend_total
#     n = len(courses)
#     if n == 0:
#         return []
#     remaining_hours = total_hours - (n * min_hours)

 
#     if remaining_hours < 0:
#         raise ValueError(
#             "There are not enough available study hours "
#             "to give every course its minimum allocation."
#         )
#     total_priority = sum(course["priority"] for course in courses)

#     allocations = []

#     for course in courses:

#         if total_priority == 0:
#             priority_share = 0
#         else:
#             priority_share = course["priority"] / total_priority

#         allocated_hours = min_hours + (
#             remaining_hours * priority_share
#         )

#         allocations.append({
#             "course": course["course"],
#             "priority": course["priority"],
#             "allocated_hours": allocated_hours
#         })

#     return allocations


import Priority_Calculation

def allocate_study_hours(
    courses,
    weekday_hours,
    weekdays,
    weekend_hours,
    weekend_days,
    min_hours
):
    # Calculate total available study hours
    weekday_total = weekday_hours * weekdays
    weekend_total = weekend_hours * weekend_days

    total_hours = weekday_total + weekend_total

    # Number of courses
    n = len(courses)

    if n == 0:
        return []

    # Hours that remain after giving every course
    # the minimum required allocation
    remaining_hours = total_hours - (n * min_hours)

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
                course["priority"] / total_priority
            )

        allocated_hours = (
            min_hours
            + remaining_hours * priority_share
        )

        allocations.append({
            "course": course["course"],
            "priority": course["priority"],
            "allocated_hours": allocated_hours
        })

    return allocations


def prepare_courses_from_Priority_Calculation(student):
    """
    Take the courses after Task 2 has calculated
    their priorities and prepare them for Task 3.
    """

    courses = []

    for course_name, course in student["courses"].items():

        courses.append({
            "course": course_name,
            "priority": course["priority"]
        })

    return courses


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

    # There are 5 weekdays and 2 weekend days
    weekdays = 5
    weekend_days = 2

    # Minimum study hours for each course
    min_hours = 1

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