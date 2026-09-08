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


from datetime import datetime, timedelta

def time_to_minutes(time_string):

    hours, minutes = map(int, time_string.split(":"))

    return hours * 60 + minutes

def minutes_to_time(minutes):

    hours = minutes // 60
    mins = minutes % 60

    return f"{hours:02d}:{mins:02d}"


def overlaps(start1, end1, start2, end2):
    """
    Check whether two time periods overlap.
    """

    return start1 < end2 and start2 < end1


def is_slot_available(day, start, end, unavailable):

    for period in unavailable:

        if period["day"] != day:
            continue

        blocked_start = time_to_minutes(period["start"])
        blocked_end = time_to_minutes(period["end"])

        if overlaps(start, end, blocked_start, blocked_end):
            return False

    return True


def is_slot_free(day, start, end, schedule):

    for session in schedule:

        if session["day"] != day:
            continue

        existing_start = time_to_minutes(session["start"])
        existing_end = time_to_minutes(session["end"])

        if overlaps(start, end, existing_start, existing_end):
            return False

    return True


def split_into_sessions(hours, session_length=2):

    sessions = []

    remaining = hours

    while remaining > 0:

        current_session = min(session_length, remaining)

        sessions.append(current_session)

        remaining -= current_session

    return sessions


def generate_available_slots(
    availability,
    unavailable,
    classes,
    session_duration
):


    slots = []

    duration_minutes = int(session_duration * 60)

    for day, periods in availability.items():

        for period in periods:

            available_start = time_to_minutes(period["start"])
            available_end = time_to_minutes(period["end"])

            current_start = available_start

            while current_start + duration_minutes <= available_end:

                current_end = current_start + duration_minutes

                class_conflict = False

                for university_class in classes:

                    if university_class["day"] != day:
                        continue

                    class_start = time_to_minutes(
                        university_class["start"]
                    )

                    class_end = time_to_minutes(
                        university_class["end"]
                    )

                    if overlaps(
                        current_start,
                        current_end,
                        class_start,
                        class_end
                    ):
                        class_conflict = True
                        break

                unavailable_conflict = not is_slot_available(
                    day,
                    current_start,
                    current_end,
                    unavailable
                )

                if not class_conflict and not unavailable_conflict:

                    slots.append({
                        "day": day,
                        "start": minutes_to_time(current_start),
                        "end": minutes_to_time(current_end)
                    })

                current_start += duration_minutes

    return slots


def preferred_slot_score(slot, preferred_times):


    score = 0

    slot_start = time_to_minutes(slot["start"])
    slot_end = time_to_minutes(slot["end"])

    for preferred in preferred_times:

        if preferred["day"] != slot["day"]:
            continue

        preferred_start = time_to_minutes(
            preferred["start"]
        )

        preferred_end = time_to_minutes(
            preferred["end"]
        )

        if (
            slot_start >= preferred_start
            and slot_end <= preferred_end
        ):
            score += 1

    return score


def generate_schedule(
    courses,
    availability,
    classes,
    unavailable,
    preferred_times=None,
    session_length=2
):


    if preferred_times is None:
        preferred_times = []

    day_order = {
        "Sunday": 0,
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6
    }

    def course_sort_key(course):

        deadline = course.get("deadline")

        if deadline is None:
            deadline_value = 999
        else:
            deadline_value = day_order.get(
                deadline,
                999
            )

        return (
            deadline_value,
            -course["priority"]
        )

    courses = sorted(
        courses,
        key=course_sort_key
    )

    sessions = []
    for course in courses:

        course_sessions = split_into_sessions(
            course["allocated_hours"],
            session_length
        )

        for duration in course_sessions:

            sessions.append({
                "course": course["course"],
                "priority": course["priority"],
                "duration": duration,
                "deadline": course.get("deadline")
            })

    schedule = []
    for session in sessions:

        slots = generate_available_slots(
            availability,
            unavailable,
            classes,
            session["duration"]
        )

        possible_slots = []

        for slot in slots:

            slot_start = time_to_minutes(
                slot["start"]
            )

            slot_end = time_to_minutes(
                slot["end"]
            )

            if not is_slot_free(
                slot["day"],
                slot_start,
                slot_end,
                schedule
            ):
                continue

            deadline = session["deadline"]

            if deadline is not None:

                slot_day_number = day_order[
                    slot["day"]
                ]

                deadline_day_number = day_order[
                    deadline
                ]

                if slot_day_number > deadline_day_number:
                    continue

            preference_score = preferred_slot_score(
                slot,
                preferred_times
            )

            possible_slots.append(
                (
                    preference_score,
                    slot
                )
            )

        if len(possible_slots) == 0:

            print(
                "Error: No feasible schedule exists "
                "under the current constraints."
            )

            return []

        possible_slots.sort(
            key=lambda x: x[0],
            reverse=True
        )

        selected_slot = possible_slots[0][1]

        schedule.append({
            "course": session["course"],
            "day": selected_slot["day"],
            "start": selected_slot["start"],
            "end": selected_slot["end"],
            "duration": session["duration"],
            "priority": session["priority"]
        })

    for course in courses:

        required_hours = course["allocated_hours"]

        scheduled_hours = 0

        for session in schedule:

            if session["course"] == course["course"]:

                scheduled_hours += session["duration"]

        if scheduled_hours < required_hours:

            print(
                f"Error: Could not schedule all required "
                f"hours for {course['course']}."
            )

            return []

    schedule.sort(
        key=lambda session: (
            day_order[session["day"]],
            time_to_minutes(session["start"])
        )
    )

    return schedule


# schedule = generate_schedule(
#     courses,
#     availability,
#     classes,
#     unavailable,
#     preferred_times,
#     session_length=2
# )


# if schedule:

#     print("\nGenerated Study Schedule")
#     print("------------------------")

#     for session in schedule:

#         print(
#             f"{session['day']} | "
#             f"{session['start']} - {session['end']} | "
#             f"{session['course']} | "
#             f"{session['duration']} hours"
#         )