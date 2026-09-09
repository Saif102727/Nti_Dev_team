"""
Priority Calculation
======================
STATUS: Not implemented yet.

Intended purpose:
    Rank a student's courses/sessions by priority so the scheduler knows
    what to study first. Priority should likely combine:
      - course difficulty (see Difficulty_Estimation.py)
      - proximity of upcoming academic_events (exams, quizzes, deadlines)
      - how little time remains before the next related session

Suggested signature:

    def calculate_priority(course, academic_events, current_week: int) -> float:
        ...
"""

import Difficulty_Estimation
from datetime import datetime, date, timedelta


# ============================================================
# AHP WEIGHTS
# ============================================================

AHP_WEIGHTS = {
    "difficulty": 0.169,
    "weakness": 0.300,
    "urgency": 0.458,
    "remaining_material": 0.073
}


# ============================================================
# NORMALIZE PERSONALIZED DIFFICULTY
# ============================================================

def normalize_difficulty(personalized_difficulty):
    """
    Convert personalized difficulty from a 1-10 scale
    to a 0-1 scale.

    Formula:

        D' = (D - 1) / 9
    """

    return (personalized_difficulty - 1) / 9


# ============================================================
# WEAKNESS
# ============================================================

def calculate_weakness(current_grade):
    """
    Calculate weakness using the student's current grade.

    The current grade is out of 50.

    Formula:

        W' = 1 - (current_grade / 50)

    A lower grade produces a higher weakness value.
    """

    weakness = 1 - (current_grade / 50)

    return max(0, min(1, weakness))


# ============================================================
# REMAINING MATERIAL
# ============================================================

def calculate_remaining_material(
    total_material,
    completed_material
):
    """
    Calculate the remaining-material ratio.

    Group A provides total_material.

    The student provides how many chapters they
    have completed.

    Formula:

        Remaining chapters =
            Total chapters - Completed chapters

        M' =
            Remaining chapters / Total chapters
    """

    if total_material <= 0:
        return 0

    remaining_material = (
        total_material - completed_material
    )

    # Prevent impossible values
    remaining_material = max(
        0,
        min(total_material, remaining_material)
    )

    material_ratio = (
        remaining_material / total_material
    )

    return material_ratio


# ============================================================
# DATE CONVERSION
# ============================================================

def convert_date(date_string):
    """
    Convert a date written as:

        YYYY-MM-DD

    into a Python date object.
    """

    return datetime.strptime(
        date_string,
        "%Y-%m-%d"
    ).date()


# ============================================================
# SEMESTER WEEK
# ============================================================

def get_semester_week(today, semester_start):
    """
    Determine the current week of the semester.

    Week 1 starts on semester_start.
    """

    days_passed = (
        today - semester_start
    ).days

    if days_passed < 0:
        return 0

    return (days_passed // 7) + 1

# ============================================================
# CALENDAR DATE
# ============================================================

def get_event_date(semester_start, week):
    """
    Convert an event's semester week into its
    actual calendar deadline.

    Events are semester-wide, meaning the same
    event applies to every course.

    The event deadline is considered to be the
    end of that week (Saturday).

    Example:

        Semester starts: Sunday, 2026-10-04
        Week 1: Oct 4 - Oct 10
        Week 2: Oct 11 - Oct 17

        Week 2 event deadline = Oct 17
    """

    week_end = semester_start + timedelta(
        days=(week * 7) - 1
    )

    return week_end

# ============================================================
# CURRENT GRADE
# ============================================================

def get_current_grade():
    """
    Ask the student for their current marks out of 50.

    Current coursework structure:

        Quizzes       = 10
        Assignments   = 10
        Project       = 10
        Midterm       = 20
        -----------------
        Total         = 50

    The final exam is NOT included because the final
    has not happened when the study plan is being created.
    """

    while True:

        try:

            grade = float(
                input(
                    "\nHow many marks have you obtained "
                    "so far out of 50? "
                )
            )

            if 0 <= grade <= 50:
                return grade

            print(
                "The grade must be between 0 and 50."
            )

        except ValueError:

            print(
                "Please enter a valid number."
            )


# ============================================================
# COMPLETED CHAPTERS
# ============================================================

def get_completed_chapters(total_material):
    """
    Ask the student how many chapters they have completed.

    The total number of chapters comes from Group A.

    Example:

        Total chapters = 8
        Completed      = 3

        Remaining      = 5
    """

    while True:

        try:

            completed = int(
                input(
                    f"\nHow many chapters have you "
                    f"completed out of {total_material}? "
                )
            )

            if 0 <= completed <= total_material:
                return completed

            print(
                f"Please enter a number between "
                f"0 and {total_material}."
            )

        except ValueError:

            print(
                "Please enter a whole number."
            )


# ============================================================
# URGENCY
# ============================================================

def calculate_urgency(today, deadline):
    """
    Calculate urgency based on the distance between
    today's date and the deadline.

    The program calculates the number of days internally.
    The user does NOT enter days_remaining.

    Formula:

        U' = 1 / (1 + days_left / 7)

    The closer the deadline, the higher the urgency.
    """

    days_left = (
        deadline - today
    ).days

    # Deadline is today or has passed
    if days_left <= 0:
        return 1.0

    urgency = 1 / (
        1 + (days_left / 7)
    )

    return min(1, urgency)


# ============================================================
# COURSE URGENCY
# ============================================================

def get_course_urgency(events, today, semester_start):
    if not events:
        return 0

    current_week = get_semester_week(today, semester_start)

    nearest_deadline = None

    for event in events:
        if "week" not in event:
            continue

        event_week = event["week"]

        # Skip events from previous weeks
        if event_week < current_week:
            continue

        event_date = get_event_date(
            semester_start,
            event_week
        )

        if event_date < today:
            continue

        if nearest_deadline is None or event_date < nearest_deadline:
            nearest_deadline = event_date

    if nearest_deadline is None:
        return 0

    return calculate_urgency(today, nearest_deadline)


# ============================================================
# COURSE DIFFICULTY
# ============================================================

def calculate_course_difficulty(course):
    """
    Use Task 1 to calculate personalized difficulty.

    Task 1 remains completely separate.

    Task 2 simply imports and uses its function.
    """

    prerequisites = course.get(
        "completed_prerequisites",
        {}
    )

    base_difficulty = course[
        "base_difficulty"
    ]

    personalized_difficulty = (
        Difficulty_Estimation.calculate_difficulty(
            base_difficulty,
            prerequisites
        )
    )

    return personalized_difficulty


# ============================================================
# START-OF-SEMESTER PRIORITY
# ============================================================

def calculate_start_priority(
    personalized_difficulty
):
    """
    At the start of the semester:

        Priority = Normalized Personalized Difficulty
    """

    normalized_difficulty = (
        normalize_difficulty(
            personalized_difficulty
        )
    )

    return normalized_difficulty


# ============================================================
# NORMAL PRIORITY
# ============================================================

def calculate_priority(
    difficulty,
    weakness,
    urgency,
    remaining_material
):
    """
    Calculate final course priority.

    Formula:

        P =
            wD * D'
          + wW * W'
          + wU * U'
          + wM * M'
    """

    priority = (

        AHP_WEIGHTS["difficulty"]
        * difficulty

        +

        AHP_WEIGHTS["weakness"]
        * weakness

        +

        AHP_WEIGHTS["urgency"]
        * urgency

        +

        AHP_WEIGHTS["remaining_material"]
        * remaining_material
    )

    return priority


# ============================================================
# MAIN STUDENT PRIORITY CALCULATION
# ============================================================

def calculate_student_priorities(student):
    """
    Calculate priorities for every course of a student.

    The user is first asked whether they are at the
    start of the semester.

    --------------------------------------------------------
    START OF SEMESTER
    --------------------------------------------------------

        Priority = Difficulty

    --------------------------------------------------------
    SEMESTER ALREADY STARTED
    --------------------------------------------------------

        Ask today's date.

        For every course:

            1. Personalized difficulty
            2. Current grade / 50
            3. Completed chapters
            4. Remaining material ratio
            5. Upcoming event urgency
            6. Final priority
    """

    answer = input(
        "Are you at the start of the semester? "
        "(yes/no): "
    ).strip().lower()


    # ========================================================
    # START OF SEMESTER
    # ========================================================

    if answer in ["yes", "y"]:

        print(
            "\nStart-of-semester mode selected."
        )

        print(
            "Priority will initially be based "
            "on personalized difficulty.\n"
        )

        for course_name, course in (
            student["courses"].items()
        ):

            personalized_difficulty = (
                calculate_course_difficulty(
                    course
                )
            )

            normalized_difficulty = (
                normalize_difficulty(
                    personalized_difficulty
                )
            )

            course[
                "personalized_difficulty"
            ] = personalized_difficulty

            course[
                "normalized_difficulty"
            ] = normalized_difficulty

            course[
                "priority"
            ] = normalized_difficulty

        return student


    # ========================================================
    # SEMESTER ALREADY STARTED
    # ========================================================

    print(
        "\nSemester-progress mode selected."
    )


    # --------------------------------------------------------
    # GET TODAY'S DATE
    # --------------------------------------------------------

    while True:

        today_string = input(
            "What is today's date? "
            "(YYYY-MM-DD): "
        ).strip()

        try:

            today = convert_date(
                today_string
            )

            break

        except ValueError:

            print(
                "Invalid date."
                " Please use YYYY-MM-DD."
            )


    # --------------------------------------------------------
    # SEMESTER START
    # --------------------------------------------------------

    semester_start = date(
        2026,
        10,
        4
    )

    semester_week = get_semester_week(
        today,
        semester_start
    )

    print(
        f"\nCurrent semester week: "
        f"{semester_week}"
    )


    # ========================================================
    # COURSE LOOP
    # ========================================================

    for course_name, course in (
        student["courses"].items()
    ):

        print(
            "\n========================================"
        )

        print(
            f"Course: {course_name}"
        )

        print(
            "========================================"
        )


        # ----------------------------------------------------
        # DIFFICULTY
        # ----------------------------------------------------

        personalized_difficulty = (
            calculate_course_difficulty(
                course
            )
        )

        normalized_difficulty = (
            normalize_difficulty(
                personalized_difficulty
            )
        )


        # ----------------------------------------------------
        # CURRENT GRADE
        # ----------------------------------------------------

        current_grade = get_current_grade()

        weakness = calculate_weakness(
            current_grade
        )


        # ----------------------------------------------------
        # TOTAL MATERIAL
        # ----------------------------------------------------

        total_material = course.get(
            "total_material"
        )

        if total_material is None:

            raise ValueError(
                f"total_material is missing "
                f"from Group A data for "
                f"{course_name}."
            )


        # ----------------------------------------------------
        # COMPLETED CHAPTERS
        # ----------------------------------------------------

        completed_material = (
            get_completed_chapters(
                total_material
            )
        )


        # ----------------------------------------------------
        # REMAINING MATERIAL
        # ----------------------------------------------------

        remaining_material = (
            total_material
            - completed_material
        )

        remaining_material_ratio = (
            calculate_remaining_material(
                total_material,
                completed_material
            )
        )


        # ----------------------------------------------------
        # URGENCY
        # ----------------------------------------------------

        urgency = get_course_urgency(
            student["events"],
            today,
            semester_start
        )

        # ----------------------------------------------------
        # FINAL PRIORITY
        # ----------------------------------------------------

        priority = calculate_priority(

            normalized_difficulty,

            weakness,

            urgency,

            remaining_material_ratio
        )


        # ----------------------------------------------------
        # STORE RESULTS
        # ----------------------------------------------------

        course[
            "personalized_difficulty"
        ] = personalized_difficulty

        course[
            "normalized_difficulty"
        ] = normalized_difficulty

        course[
            "current_grade"
        ] = current_grade

        course[
            "weakness"
        ] = weakness

        course[
            "completed_material"
        ] = completed_material

        course[
            "remaining_material"
        ] = remaining_material

        course[
            "remaining_material_ratio"
        ] = remaining_material_ratio

        course[
            "urgency"
        ] = urgency

        course[
            "priority"
        ] = priority


    return student


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_priorities(student):

    print(
        "\n\n========================================"
    )

    print(
        "COURSE PRIORITIES"
    )

    print(
        "========================================"
    )


    for course_name, course in (
        student["courses"].items()
    ):

        print(
            f"\n{course_name}"
        )

        print(
            f"Personalized Difficulty: "
            f"{course['personalized_difficulty']:.2f}"
        )

        print(
            f"Normalized Difficulty: "
            f"{course['normalized_difficulty']:.3f}"
        )

        if "current_grade" in course:

            print(
                f"Current Grade: "
                f"{course['current_grade']:.2f}/50"
            )

            print(
                f"Weakness: "
                f"{course['weakness']:.3f}"
            )

            print(
                f"Completed Chapters: "
                f"{course['completed_material']}"
            )

            print(
                f"Remaining Chapters: "
                f"{course['remaining_material']}"
            )

            print(
                f"Remaining Material Ratio: "
                f"{course['remaining_material_ratio']:.3f}"
            )

            print(
                f"Urgency: "
                f"{course['urgency']:.3f}"
            )

        print(
            f"Priority: "
            f"{course['priority']:.3f}"
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    import json

    with open(
        "data/dummy_data.json",
        "r"
    ) as file:

        students = json.load(file)


    student = students[0]


    student = calculate_student_priorities(
        student
    )


    display_priorities(
        student
    )