import Difficulty_Estimation
# from Login_systemV2 import auth_service
from datetime import datetime, date, timedelta


# ==========================================
# AHP WEIGHTS
# ==========================================

AHP_WEIGHTS = {
    "difficulty": 0.169,
    "weakness": 0.300,
    "urgency": 0.458,
    "remaining_material": 0.073
}


# ==========================================
# DIFFICULTY NORMALIZATION
# ==========================================

def normalize_difficulty(personalized_difficulty):

    return (personalized_difficulty - 1) / 9


# ==========================================
# WEAKNESS
# ==========================================

def calculate_weakness(current_grade):

    weakness = 1 - (current_grade / 50)

    return max(0, min(1, weakness))


# ==========================================
# REMAINING MATERIAL
# ==========================================

def calculate_remaining_material(total_material, completed_material):

    if total_material <= 0:
        return 0

    remaining_material = total_material - completed_material

    remaining_material = max(
        0,
        min(total_material, remaining_material)
    )

    material_ratio = remaining_material / total_material

    return material_ratio


# ==========================================
# DATE CONVERSION
# ==========================================

def convert_date(date_string):

    return datetime.strptime(
        date_string,
        "%Y-%m-%d"
    ).date()


# ==========================================
# SEMESTER WEEK
# ==========================================

def get_semester_week(today, semester_start):

    days_passed = (today - semester_start).days

    if days_passed < 0:
        return 0

    return (days_passed // 7) + 1


# ==========================================
# GET DATE FROM WEEK
# ==========================================

def get_event_date(semester_start, week):

    return semester_start + timedelta(
        days=(week - 1) * 7
    )


# ==========================================
# EVENT IMPORTANCE
# ==========================================

EVENT_PRIORITY = {

    "assignment": 0.40,

    "quiz": 0.55,

    "project": 0.75,

    "midterm": 0.90,

    "final": 1.00
}


# ==========================================
# TIME URGENCY
# ==========================================

def calculate_urgency(today, deadline):

    days_left = (deadline - today).days

    if days_left <= 0:
        return 1.0

    urgency = 1 / (1 + (days_left / 7))

    return min(1, urgency)


# ==========================================
# COURSE URGENCY
# ==========================================

def get_course_urgency(events, today, semester_start):

    if not events:
        return 0

    current_week = get_semester_week(
        today,
        semester_start
    )

    highest_urgency = 0

    for event in events:

        if "week" not in event:
            continue

        event_week = event["week"]

        # Ignore events from previous weeks
        if event_week < current_week:
            continue

        event_date = get_event_date(
            semester_start,
            event_week
        )

        # Ignore events that already passed
        if event_date < today:
            continue

        event_type = event.get(
            "type",
            "assignment"
        ).lower()

        event_priority = EVENT_PRIORITY.get(
            event_type,
            0.40
        )

        time_urgency = calculate_urgency(
            today,
            event_date
        )

        event_urgency = (
            time_urgency *
            event_priority
        )

        if event_urgency > highest_urgency:

            highest_urgency = event_urgency

    return highest_urgency


# ==========================================
# CALCULATE PRIORITY FOR ONE COURSE
# ==========================================

def calculate_course_priority(
    personalized_difficulty,
    current_grade,
    total_material,
    completed_material,
    events,
    today,
    semester_start
):

    # D'
    difficulty = normalize_difficulty(
        personalized_difficulty
    )

    # W'
    weakness = calculate_weakness(
        current_grade
    )

    # M'
    remaining_material = calculate_remaining_material(
        total_material,
        completed_material
    )

    # U'
    urgency = get_course_urgency(
        events,
        today,
        semester_start
    )

    # Final priority formula
    priority = (
        AHP_WEIGHTS["difficulty"] * difficulty
        + AHP_WEIGHTS["weakness"] * weakness
        + AHP_WEIGHTS["urgency"] * urgency
        + AHP_WEIGHTS["remaining_material"] * remaining_material
    )

    return {
        "difficulty": difficulty,
        "weakness": weakness,
        "urgency": urgency,
        "remaining_material": remaining_material,
        "priority": priority
    }


# ==========================================
# CALCULATE ALL COURSE PRIORITIES
# ==========================================

def calculate_student_priorities(
    student,
    today=None,
    semester_start=date(2026, 10, 4)
):

    if today is None:
        today = date.today()

    for course_name, course in student["courses"].items():

        # --------------------------------------
        # PERSONALIZED DIFFICULTY
        # --------------------------------------

        prerequisites = course.get(
            "completed_prerequisites",
            {}
        )

        personalized_difficulty = (
            Difficulty_Estimation.calculate_difficulty(
                course["base_difficulty"],
                prerequisites
            )
        )

        # --------------------------------------
        # CURRENT GRADE
        # --------------------------------------

        if prerequisites:

            total_grade = 0
            total_influence = 0

            for prerequisite in prerequisites.values():

                total_grade += (
                    prerequisite["grade"]
                    * prerequisite["influence"]
                )

                total_influence += (
                    prerequisite["influence"]
                )

            current_grade = (
                total_grade / total_influence
                if total_influence > 0
                else 0
            )

        else:

            # No prerequisites
            current_grade = 50

        # --------------------------------------
        # COMPLETED MATERIAL
        # --------------------------------------

        completed_material = len(
            prerequisites
        )

        # --------------------------------------
        # EVENTS
        # --------------------------------------

        events = course.get(
            "events",
            []
        )

        # --------------------------------------
        # CALCULATE PRIORITY
        # --------------------------------------

        result = calculate_course_priority(

            personalized_difficulty,

            current_grade,

            course["total_material"],

            completed_material,

            events,

            today,

            semester_start
        )

        # --------------------------------------
        # SAVE RESULTS
        # --------------------------------------

        course["personal_difficulty"] = (
            personalized_difficulty
        )

        course["current_grade"] = current_grade

        course["completed_material"] = (
            completed_material
        )

        course["difficulty_normalized"] = (
            result["difficulty"]
        )

        course["weakness"] = (
            result["weakness"]
        )

        course["urgency"] = (
            result["urgency"]
        )

        course["remaining_material_ratio"] = (
            result["remaining_material"]
        )

        course["priority"] = (
            result["priority"]
        )

    return student


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    import json

    with open(
        "data/dummy_data.json",
        "r"
    ) as file:

        students = json.load(file)

    student = students[0]

    # Example testing date
    today = date(2026, 12, 5)

    student = calculate_student_priorities(
        student,
        today=today
    )

    print("\n========================================")
    print("TASK 2 - COURSE PRIORITIES")
    print("========================================")

    for course_name, course in student["courses"].items():

        print(f"\n{course_name}")

        print(
            f"Personal Difficulty: "
            f"{course['personal_difficulty']:.2f}"
        )

        print(
            f"Difficulty: "
            f"{course['difficulty_normalized']:.3f}"
        )

        print(
            f"Weakness: "
            f"{course['weakness']:.3f}"
        )

        print(
            f"Urgency: "
            f"{course['urgency']:.3f}"
        )

        print(
            f"Remaining Material: "
            f"{course['remaining_material_ratio']:.3f}"
        )

        print(
            f"FINAL PRIORITY: "
            f"{course['priority']:.3f}"
        )

# if __name__ == "__main__":

#     username = input("Username: ")
#     password = input("Password: ")

#     authenticated_user = (
#         auth_service.authenticate(
#             username,
#             password
#         )
#     )

#     student_id = authenticated_user[
#         "student_id"
#     ]

#     print(
#         f"\nLogged in as: "
#         f"{authenticated_user['name']}"
#     )

#     print(
#         f"Student ID: "
#         f"{student_id}"
#     )

#     student = calculate_student_priorities_by_id(
#         student_id
#     )

#     display_priorities(
#         student
#     )