from datetime import datetime
from typing import List

from models import Student, Course, Session


class Schedule:
    def __init__(self, sessions: List[Session] = None):
        self.sessions = sessions if sessions is not None else []

    # Convert time from HH:MM to minutes
    @staticmethod
    def time_to_minutes(time: str) -> int:
        time_obj = datetime.strptime(time, "%H:%M")
        return time_obj.hour * 60 + time_obj.minute

    # Check if two sessions have a time conflict
    @staticmethod
    def sessions_conflict(first: Session, second: Session) -> bool:

        if first.time_slot.the_day != second.time_slot.the_day:
            return False

        first_start = Schedule.time_to_minutes(
            first.time_slot.start_time
        )
        first_end = Schedule.time_to_minutes(
            first.time_slot.end_time
        )

        second_start = Schedule.time_to_minutes(
            second.time_slot.start_time
        )
        second_end = Schedule.time_to_minutes(
            second.time_slot.end_time
        )

        return first_start < second_end and second_start < first_end

    # Check if a new session conflicts with the current schedule
    def has_conflict(self, new_session: Session) -> bool:

        return any(
            self.sessions_conflict(new_session, session)
            for session in self.sessions
        )

    # Add session if there is no conflict
    def add_session(self, session: Session) -> bool:

        if self.has_conflict(session):
            return False

        self.sessions.append(session)
        return True

    # Check course prerequisites
    @staticmethod
    def check_prerequisites(
        course: Course,
        student: Student
    ) -> bool:

        completed_courses = set(student.course_completed)

        return all(
            prerequisite in completed_courses
            for prerequisite in course.perequisites
        )

    # Filter courses according to prerequisites
    @staticmethod
    def filter_available_courses(
        courses: List[Course],
        student: Student
    ) -> List[Course]:

        return [
            course
            for course in courses
            if Schedule.check_prerequisites(course, student)
        ]

    # Calculate free gaps between sessions
    def calculate_gaps(self) -> dict:

        gaps = {}

        days = set(
            session.time_slot.the_day
            for session in self.sessions
        )

        for day in days:

            day_sessions = [
                session
                for session in self.sessions
                if session.time_slot.the_day == day
            ]

            day_sessions.sort(
                key=lambda session:
                self.time_to_minutes(
                    session.time_slot.start_time
                )
            )

            day_gaps = []

            for i in range(len(day_sessions) - 1):

                current_end = self.time_to_minutes(
                    day_sessions[i].time_slot.end_time
                )

                next_start = self.time_to_minutes(
                    day_sessions[i + 1].time_slot.start_time
                )

                gap = next_start - current_end

                if gap > 0:
                    day_gaps.append(gap)

            gaps[day] = day_gaps

        return gaps

    # Get the longest free gap for each day
    def longest_gap(self) -> dict:

        gaps = self.calculate_gaps()

        return {
            day: max(day_gaps, default=0)
            for day, day_gaps in gaps.items()
        }

    # Return the complete schedule
    def get_schedule(self) -> List[Session]:
        return self.sessions