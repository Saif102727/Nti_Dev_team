import json
from pathlib import Path

from model import (
    Student,
    Course,
    Session,
    Time,
    AcademicEvent
)


# ==========================================
# Load JSON File
# ==========================================

def load_json(file_path: str | Path) -> dict:

    file_path = Path(file_path)

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ==========================================
# Create Time Object
# ==========================================

def load_time(data: dict) -> Time:

    return Time(
        day=data["day"],
        start_time=data["start_time"],
        end_time=data["end_time"]
    )


# ==========================================
# Create Session Object
# ==========================================

def load_session(data: dict) -> Session:

    return Session(
        session_id=data["session_id"],
        course_id=data["course_id"],
        session_type=data["session_type"],
        time_slot=load_time(
            data["time_slot"]
        )
    )


# ==========================================
# Create Course Object
# ==========================================

def load_course(data: dict) -> Course:

    sessions = [
        load_session(session)
        for session in data.get(
            "sessions",
            []
        )
    ]

    return Course(
        course_id=data["course_id"],
        name=data["name"],
        difficulty_level=data["difficulty_level"],
        prerequisites=data.get(
            "prerequisites",
            []
        ),
        sessions=sessions
    )


# ==========================================
# Create Student Object
# ==========================================

def load_student(data: dict) -> Student:

    return Student(
        student_id=data["student_id"],
        completed_courses=data.get(
            "completed_courses",
            []
        ),
        preferred_study_location=data[
            "preferred_study_location"
        ],
        daily_study_hours=data.get(
            "daily_study_hours",
            {}
        ),
        free_days=data.get(
            "free_days",
            []
        ),
        points=data.get(
            "points",
            0
        )
    )


# ==========================================
# Create Academic Event Object
# ==========================================

def load_academic_event(
    data: dict
) -> AcademicEvent:

    return AcademicEvent(
        event_name=data["event_name"],
        week_number=data["week_number"],
        course_id=data["course_id"]
    )


# ==========================================
# Load Complete Data
# ==========================================

def load_all_data(
    file_path: str | Path
):

    data = load_json(file_path)

    student = load_student(
        data["student"]
    )

    courses = [
        load_course(course)
        for course in data.get(
            "courses",
            []
        )
    ]

    academic_events = [
        load_academic_event(event)
        for event in data.get(
            "academic_events",
            []
        )
    ]

    return (
        student,
        courses,
        academic_events
    )
