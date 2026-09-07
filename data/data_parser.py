import json

from Nti_Dev_team.models import Student, Course, Session, Time, AcademicEvent


def load_data(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Student
    student_data = data["student"]

    student = Student(
        student_id=student_data["student_id"],
        completed_courses=student_data["completed_courses"],
        preferred_study_location=student_data["preferred_study_location"],
        daily_study_hours=student_data["daily_study_hours"],
        free_days=student_data["free_days"],
        points=student_data["points"]
    )

    # Courses
    courses = []

    for course_data in data["courses"]:
        sessions = []

        for session_data in course_data["sessions"]:
            time_data = session_data["time_slot"]

            time = Time(
                day=time_data["day"],
                start_time=time_data["start_time"],
                end_time=time_data["end_time"]
            )

            session = Session(
                session_id=session_data["session_id"],
                course_id=session_data["course_id"],
                session_type=session_data["session_type"],
                time_slot=time
            )

            sessions.append(session)

        course = Course(
            course_id=course_data["course_id"],
            name=course_data["name"],
            difficulty_level=course_data["difficulty_level"],
            prerequisites=course_data["prerequisites"],
            sessions=sessions
        )

        courses.append(course)

    # Academic Events
    academic_events = []

    for event_data in data["academic_events"]:
        event = AcademicEvent(
            event_name=event_data["event_name"],
            week_number=event_data["week_number"],
            course_id=event_data["course_id"]
        )

        academic_events.append(event)

    return student, courses, academic_events