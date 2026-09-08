from datetime import datetime
from typing import List

from models import Student, Course, Session


class Schedule:

    def __init__(self, sessions: List[Session]):
        self.sessions = sessions if sessions is not None else []


    # ==========================================
    # Convert HH:MM to minutes
    # ==========================================

    @staticmethod
    def time_to_minutes(time: str) -> int:

        time_obj = datetime.strptime(
            time,
            "%H:%M"
        )

        return (
            time_obj.hour * 60
            + time_obj.minute
        )


    # ==========================================
    # Check if two sessions conflict
    # ==========================================

    @staticmethod
    def sessions_conflict(
        first: Session,
        second: Session
    ) -> bool:

        # Different days = no conflict

        if (
            first.time_slot.day
            != second.time_slot.day
        ):
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


        # Check time overlap

        return (
            first_start < second_end
            and second_start < first_end
        )


    # ==========================================
    # Check new session against schedule
    # ==========================================

    def has_conflict(
        self,
        new_session: Session
    ) -> bool:

        return any(
            self.sessions_conflict(
                new_session,
                session
            )
            for session in self.sessions
        )


    # ==========================================
    # Add session if no conflict
    # ==========================================

    def add_session(
        self,
        session: Session
    ) -> bool:

        if self.has_conflict(session):
            return False

        self.sessions.append(session)

        return True


    # ==========================================
    # Check course prerequisites
    # ==========================================

    @staticmethod
    def check_prerequisites(
        course: Course,
        student: Student
    ) -> bool:

        completed_courses = set(
            student.completed_courses
        )

        return all(
            prerequisite in completed_courses
            for prerequisite
            in course.prerequisites
        )


    # ==========================================
    # Filter available courses
    # ==========================================

    @staticmethod
    def filter_available_courses(
        courses: List[Course],
        student: Student
    ) -> List[Course]:

        return [
            course
            for course in courses
            if Schedule.check_prerequisites(
                course,
                student
            )
        ]


    # ==========================================
    # Calculate free gaps
    # ==========================================

    def calculate_gaps(self) -> dict:

        gaps = {}


        # Get all days in the schedule

        days = set(
            session.time_slot.day
            for session in self.sessions
        )


        for day in days:

            day_sessions = [
                session
                for session in self.sessions
                if session.time_slot.day == day
            ]


            # Sort sessions by start time

            day_sessions.sort(
                key=lambda session:
                self.time_to_minutes(
                    session.time_slot.start_time
                )
            )


            day_gaps = []


            for i in range(
                len(day_sessions) - 1
            ):

                current_end = (
                    self.time_to_minutes(
                        day_sessions[i]
                        .time_slot.end_time
                    )
                )


                next_start = (
                    self.time_to_minutes(
                        day_sessions[i + 1]
                        .time_slot.start_time
                    )
                )


                gap = next_start - current_end


                if gap > 0:
                    day_gaps.append(gap)


            gaps[day] = day_gaps


        return gaps


    # ==========================================
    # Get longest free gap per day
    # ==========================================

    def longest_gap(self) -> dict:

        gaps = self.calculate_gaps()


        return {
            day: max(
                day_gaps,
                default=0
            )
            for day, day_gaps
            in gaps.items()
        }


    # ==========================================
    # Return complete schedule
    # ==========================================

    def get_schedule(
        self
    ) -> List[Session]:

        return self.sessions