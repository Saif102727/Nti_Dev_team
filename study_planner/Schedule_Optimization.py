"""
Schedule Optimization
======================
STATUS: Not implemented yet.

Intended purpose:
    Take a raw generated schedule (see Schedule_Generation.py) and optimize
    the allocation of study hours across courses, respecting the student's
    max daily hours and each course's priority/difficulty, instead of the
    temporary "equal split" logic currently used in Main/main.py.

Suggested signature:

    def optimize_schedule(schedule, max_daily_hours: float) -> dict:
        ...
"""
