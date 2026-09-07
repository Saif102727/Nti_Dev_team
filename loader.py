import json
from pathlib import Path
from typing import Any

from model import (
    Student,
    Course,
    Session,
    Time,
    AcademicEvent,
)


# =========================================================
# LOAD JSON
# =========================================================

def load_json(file_path: str | Path) -> dict[str, Any]:
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Data file not found: {file_path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Data path is not a file: {file_path}"
        )

    with file_path.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "Root JSON structure must be an object."
        )

    return data


# =========================================================
# TIME
# =========================================================

def load_time(data: dict[str, Any]) -> Time:
    if not isinstance(data, dict):
        raise ValueError("Invalid time data.")

    return Time(
        day=str(data.get("day", "Unknown")),
        start_time=str(data.get("start_time", "00:00")),
        end_time=str(data.get("end_time", "00:00")),
    )


# =========================================================
# SESSION
# =========================================================

def load_session(data: dict[str, Any]) -> Session:
    if not isinstance(data, dict):
        raise ValueError("Invalid session data.")

    return Session(
        session_id=str(
            data.get("session_id", "")
        ),
        course_id=str(
            data.get("course_id", "")
        ),
        session_type=str(
            data.get("session_type", "Session")
        ),
        time_slot=load_time(
            data.get("time_slot", {})
        ),
    )


# =========================================================
# COURSE
# =========================================================

def load_course(data: dict[str, Any]) -> Course:
    if not isinstance(data, dict):
        raise ValueError("Invalid course data.")

    raw_sessions = data.get("sessions", [])

    if not isinstance(raw_sessions, list):
        raw_sessions = []

    sessions = [
        load_session(session)
        for session in raw_sessions
        if isinstance(session, dict)
    ]

    prerequisites = data.get(
        "prerequisites",
        [],
    )

    if not isinstance(prerequisites, list):
        prerequisites = []

    try:
        difficulty = int(
            data.get("difficulty_level", 1)
        )
    except (TypeError, ValueError):
        difficulty = 1

    difficulty = max(
        1,
        min(5, difficulty)
    )

    return Course(
        course_id=str(
            data.get("course_id", "")
        ),
        name=str(
            data.get("name", "Unnamed Course")
        ),
        difficulty_level=difficulty,
        prerequisites=[
            str(item)
            for item in prerequisites
        ],
        sessions=sessions,
    )


# =========================================================
# STUDENT
# =========================================================

def load_student(data: dict[str, Any]) -> Student:
    if not isinstance(data, dict):
        raise ValueError("Invalid student data.")

    completed_courses = data.get(
        "completed_courses",
        [],
    )

    if not isinstance(completed_courses, list):
        completed_courses = []

    daily_study_hours = data.get(
        "daily_study_hours",
        {},
    )

    if not isinstance(daily_study_hours, dict):
        daily_study_hours = {}

    normalized_hours = {}

    for day, hours in daily_study_hours.items():
        try:
            normalized_hours[str(day)] = max(
                0.0,
                float(hours),
            )
        except (TypeError, ValueError):
            normalized_hours[str(day)] = 0.0

    free_days = data.get(
        "free_days",
        [],
    )

    if not isinstance(free_days, list):
        free_days = []

    try:
        points = int(
            data.get("points", 0)
        )
    except (TypeError, ValueError):
        points = 0

    return Student(
        student_id=str(
            data.get("student_id", "UNKNOWN")
        ),
        completed_courses=[
            str(course)
            for course in completed_courses
        ],
        preferred_study_location=str(
            data.get(
                "preferred_study_location",
                "Unknown",
            )
        ),
        daily_study_hours=normalized_hours,
        free_days=[
            str(day)
            for day in free_days
        ],
        points=max(0, points),
    )


# =========================================================
# ACADEMIC EVENT
# =========================================================

def load_academic_event(
    data: dict[str, Any],
) -> AcademicEvent:

    if not isinstance(data, dict):
        raise ValueError(
            "Invalid academic event data."
        )

    try:
        week_number = int(
            data.get("week_number", 0)
        )
    except (TypeError, ValueError):
        week_number = 0

    return AcademicEvent(
        event_name=str(
            data.get(
                "event_name",
                "Academic Event",
            )
        ),
        week_number=max(
            0,
            week_number,
        ),
        course_id=str(
            data.get(
                "course_id",
                "",
            )
        ),
    )


# =========================================================
# LOAD ALL DATA
# =========================================================

def load_all_data(
    file_path: str | Path,
):
    data = load_json(file_path)

    student_data = data.get(
        "student",
        {},
    )

    courses_data = data.get(
        "courses",
        [],
    )

    events_data = data.get(
        "academic_events",
        [],
    )

    if not isinstance(courses_data, list):
        courses_data = []

    if not isinstance(events_data, list):
        events_data = []

    student = load_student(
        student_data
    )

    courses = [
        load_course(course)
        for course in courses_data
        if isinstance(course, dict)
    ]

    academic_events = [
        load_academic_event(event)
        for event in events_data
        if isinstance(event, dict)
    ]

    return (
        student,
        courses,
        academic_events,
    )