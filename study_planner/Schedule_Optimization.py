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
from itertools import product
import schedule_generation

def calculate_ahp_weights(matrix):

    n = len(matrix)

    # Sum each column
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

    # Average each row
    weights = []

    for i in range(n):

        row_average = sum(normalized_matrix[i]) / n

        weights.append(row_average)

    return weights

comparison_matrix = [

    [1,   1/2, 3,   3],

    [2,   1,   5,   5],

    [1/3, 1/5, 1,   1/2],

    [1/3, 1/5, 2,   1]

]


weights = calculate_ahp_weights(comparison_matrix)

wP = weights[0]
wE = weights[1]
wR = weights[2]
wB = weights[3]


print("\nTask 5 AHP Weights")
print("------------------")

print(f"Priority:   {wP:.3f}")
print(f"Deadline:   {wE:.3f}")
print(f"Preference: {wR:.3f}")
print(f"Balance:    {wB:.3f}")
print(f"Total:      {sum(weights):.3f}")

def calculate_priority_satisfaction(schedule, courses):

    total_hours = 0
    weighted_hours = 0
    total_priority = 0

    for course in courses:

        priority = course["priority"]

        total_priority += priority

        for session in schedule:

            if session["course"] == course["course"]:

                hours = session["duration"]

                total_hours += hours

                weighted_hours += priority * hours

    if total_hours == 0 or total_priority == 0:
        return 0

    score = weighted_hours / (total_hours * total_priority)

    return min(score, 1)

def calculate_deadline_satisfaction(schedule, courses):

    total_required = 0
    completed_before_deadline = 0

    day_order = {
        "Sunday": 0,
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6
    }

    for course in courses:

        deadline = course.get("deadline")

        if deadline is None:
            continue

        required_hours = course["allocated_hours"]

        total_required += required_hours

        deadline_number = day_order[deadline]

        for session in schedule:

            if session["course"] != course["course"]:
                continue

            session_day = day_order[session["day"]]

            if session_day <= deadline_number:

                completed_before_deadline += session["duration"]

    if total_required == 0:
        return 1

    score = completed_before_deadline / total_required

    return min(score, 1)

def calculate_preference_satisfaction(schedule, preferred_times):

    if len(schedule) == 0:
        return 1

    preferred_sessions = 0

    for session in schedule:

        session_start = schedule_generation.time_to_minutes(
            session["start"]
        )

        session_end = schedule_generation.time_to_minutes(
            session["end"]
        )

        preferred = False

        for preference in preferred_times:

            if preference["day"] != session["day"]:
                continue

            preference_start = schedule_generation.time_to_minutes(
                preference["start"]
            )

            preference_end = schedule_generation.time_to_minutes(
                preference["end"]
            )

            if (
                session_start >= preference_start
                and
                session_end <= preference_end
            ):

                preferred = True
                break

        if preferred:
            preferred_sessions += 1

    score = preferred_sessions / len(schedule)

    return score

def calculate_workload_balance(schedule):

    day_hours = {}

    for session in schedule:

        day = session["day"]

        if day not in day_hours:
            day_hours[day] = 0

        day_hours[day] += session["duration"]

    if len(day_hours) == 0:
        return 1

    daily_hours = list(day_hours.values())

    average = sum(daily_hours) / len(daily_hours)

    variance = 0

    for hours in daily_hours:

        variance += (hours - average) ** 2

    variance = variance / len(daily_hours)

    standard_deviation = math.sqrt(variance)

    score = 1 / (1 + standard_deviation)

    return score

def calculate_schedule_score(
        schedule,
        courses,
        preferred_times
):

    P = calculate_priority_satisfaction(
        schedule,
        courses
    )

    E = calculate_deadline_satisfaction(
        schedule,
        courses
    )

    R = calculate_preference_satisfaction(
        schedule,
        preferred_times
    )

    B = calculate_workload_balance(
        schedule
    )

    final_score = (

        wP * P
        +
        wE * E
        +
        wR * R
        +
        wB * B

    )

    return final_score, P, E, R, B

def is_valid_schedule(schedule, courses):

    for course in courses:

        required_hours = course["allocated_hours"]

        scheduled_hours = 0

        for session in schedule:

            if session["course"] == course["course"]:

                scheduled_hours += session["duration"]

        if scheduled_hours < required_hours:

            return False

    for i in range(len(schedule)):

        for j in range(i + 1, len(schedule)):

            session1 = schedule[i]
            session2 = schedule[j]

            if session1["day"] != session2["day"]:
                continue

            start1 = schedule_generation.time_to_minutes(
                session1["start"]
            )

            end1 = schedule_generation.time_to_minutes(
                session1["end"]
            )

            start2 = schedule_generation.time_to_minutes(
                session2["start"]
            )

            end2 = schedule_generation.time_to_minutes(
                session2["end"]
            )

            if schedule_generation.overlaps(
                start1,
                end1,
                start2,
                end2
            ):

                return False

    day_order = {
        "Sunday": 0,
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6
    }

    for session in schedule:

        for course in courses:

            if session["course"] != course["course"]:
                continue

            deadline = course.get("deadline")

            if deadline is None:
                continue

            if day_order[session["day"]] > day_order[deadline]:

                return False

    return True

def generate_schedule_options(
        courses,
        availability,
        classes,
        unavailable,
        preferred_times=None,
        session_length=2,
        max_options=50
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

    courses = sorted(
        courses,
        key=lambda course: (
            day_order.get(course.get("deadline"), 999),
            -course["priority"]
        )
    )

    sessions = []

    for course in courses:

        course_sessions = schedule_generation.split_into_sessions(
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
    session_options = []

    for session in sessions:

        slots = schedule_generation.generate_available_slots(
            availability,
            unavailable,
            classes,
            session["duration"]
        )

        possible_slots = []

        for slot in slots:
            deadline = session["deadline"]

            if deadline is not None:

                if day_order[slot["day"]] > day_order[deadline]:

                    continue
            preference_score = schedule_generation.preferred_slot_score(
                slot,
                preferred_times
            )

            possible_slots.append(
                (preference_score, slot)
            )

        possible_slots.sort(
            key=lambda x: x[0],
            reverse=True
        )

        session_options.append(
            possible_slots[:10]
        )

    for options in session_options:

        if len(options) == 0:

            print(
                "Error: No feasible schedule exists "
                "under the current constraints."
            )

            return []

    schedules = []

    combinations = product(*session_options)

    for combination in combinations:

        schedule = []

        for session, selected in zip(
                sessions,
                combination
        ):

            slot = selected[1]

            schedule.append({

                "course": session["course"],

                "day": slot["day"],

                "start": slot["start"],

                "end": slot["end"],

                "duration": session["duration"],

                "priority": session["priority"]

            })

        if is_valid_schedule(schedule, courses):

            schedule.sort(
                key=lambda session: (
                    day_order[session["day"]],
                    schedule_generation.time_to_minutes(
                        session["start"]
                    )
                )
            )

            schedules.append(schedule)

        if len(schedules) >= max_options:

            break

    return schedules

def optimize_schedules(
        schedules,
        courses,
        preferred_times
):

    results = []

    for schedule in schedules:

        score, P, E, R, B = calculate_schedule_score(
            schedule,
            courses,
            preferred_times
        )

        results.append({

            "schedule": schedule,

            "score": score,

            "priority_score": P,

            "deadline_score": E,

            "preference_score": R,

            "balance_score": B

        })

    results.sort(
        key=lambda result: result["score"],
        reverse=True
    )

    return results


def print_best_schedule(results):

    if len(results) == 0:

        print("No valid schedules were found.")

        return

    best = results[0]

    print("\n====================================")
    print("BEST SCHEDULE")
    print("====================================")

    for session in best["schedule"]:

        print(
            f'{session["day"]} | '
            f'{session["start"]} - '
            f'{session["end"]} | '
            f'{session["course"]}'
        )

    print("\nScores")
    print("------------------------------------")

    print(
        f'Priority Satisfaction: '
        f'{best["priority_score"]:.3f}'
    )

    print(
        f'Deadline Satisfaction: '
        f'{best["deadline_score"]:.3f}'
    )

    print(
        f'Preference Satisfaction: '
        f'{best["preference_score"]:.3f}'
    )

    print(
        f'Workload Balance: '
        f'{best["balance_score"]:.3f}'
    )

    print("------------------------------------")

    print(
        f'FINAL SCORE: '
        f'{best["score"]:.3f}'
    )

    print("====================================")

schedules = generate_schedule_options(
    schedule_generation.courses,
    schedule_generation.availability,
    schedule_generation.classes,
    schedule_generation.unavailable,
    schedule_generation.preferred_times,
    session_length=2,
    max_options=50
)

results = optimize_schedules(
    schedules,
    schedule_generation.courses,
    schedule_generation.preferred_times
)

print_best_schedule(results)