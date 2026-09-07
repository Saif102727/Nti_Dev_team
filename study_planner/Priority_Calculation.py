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
