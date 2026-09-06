from dataclasses import dataclass ,field
from typing import List, Dict
@dataclass

class Time:
    the_day: str
    start_time : str
    end_time : str


@dataclass


class Session:
    session_id: str   # Unique ID to differentiate between multiple sections of the same course
    session_type: str  # "Lecture" or "Section"
    course_id: str
    time_slot : Time  #Links the session to a specific day and time

@dataclass

class Course:
    name_course: str
    course_id: str
    dificulty_level: int # Integer (1-5) representing how hard the course is[cite: 1]
    perequisites:List[str] = field(default_factory=list)
    session: list[str] = field(default_factory=list)


@dataclass

class Student:
    student_id: str
    pereferd_study_location: str
    daily_student_hours: Dict[str,list]
    course_completed: list[str]
    free_days: list[str] = field(default_factory=list)
    points: int = 0

@dataclass

class Acadmic_Event:
    event_name: str
    weak_number: str
    course_id: str