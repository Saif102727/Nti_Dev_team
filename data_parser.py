import json
from operator import add

from model import Student, Course, Session, Time, AcadmicEvent

def load_data(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # -------------------------
    # Create Student object
    # -------------------------
    student_data = data["student"]

    student = Student(
        student_id=student_data["student_id"],
        pereferd_study_location=student_data["preferred_study_location"],
        daily_student_hours=student_data["daily_study_hours"],
        course_completed=student_data["completed_courses"],
        free_days=student_data["free_days"],
        points=student_data["points"]
    )

    # -------------------------
    # Create Course objects
    # -------------------------
    courses = []

    for course_data in data["courses"]:

        sessions = []

        for session_data in course_data["sessions"]:

            time_data = session_data["time_slot"]

            time_slot = Time(
                the_day=time_data["day"],
                start_time=time_data["start_time"],
                end_time=time_data["end_time"]
            )

            session = Session(
                session_id=session_data["session_id"],
                session_type=session_data["session_type"],
                course_id=session_data["course_id"],
                time_slot=time_slot
            )

            sessions.append(session)

        course = Course(
            name_course=course_data["name"],
            course_id=course_data["course_id"],
            dificulty_level=course_data["difficulty_level"],
            perequisites=course_data["prerequisites"],
            session=sessions
        )

        courses.append(course)

    # -------------------------
    # Create Academic Event objects
    # -------------------------
    academic_events = []

    for event_data in data["academicevents"]:

        event = AcadmicEvent(
            event_name=event_data["event_name"],
            weak_number=str(event_data["week_number"]),
            course_id=event_data["course_id"]
        )

        academic_events.append(event)

    return student, courses, academic_events