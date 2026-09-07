from dataclasses import dataclass, field
from typing import List, Dict


# ==========================================
# Time
# ==========================================

@dataclass
class Time:
    day: str
    start_time: str
    end_time: str


# ==========================================
# Session
# ==========================================

@dataclass
class Session:
    session_id: str
    course_id: str
    session_type: str
    time_slot: Time


# ==========================================
# Course
# ==========================================

@dataclass
class Course:
    course_id: str
    name: str
    difficulty_level: int
    prerequisites: List[str] = field(default_factory=list)
    sessions: List[Session] = field(default_factory=list)


# ==========================================
# Student
# ==========================================

@dataclass
class Student:
    student_id: str
    completed_courses: List[str]
    preferred_study_location: str
    daily_study_hours: Dict[str, int]
    free_days: List[str] = field(default_factory=list)
    points: int = 0


# ==========================================
# Academic Event
# ==========================================

@dataclass
class AcademicEvent:
    event_name: str
    week_number: int
    course_id: str
