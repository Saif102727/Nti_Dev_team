<<<<<<< HEAD
# ----------------------------------
# Final Scheduling Algorithm
# ----------------------------------
from dataclass.schedule import Schedule
my_schedule = Schedule()

valid_courses = Schedule.filter_available_courses(
    st.session_state.courses,
    student
)

my_schedule.build_schedule(valid_courses)

my_schedule.export_to_json("final_schedule.json")

st.subheader("🗓️ Your Approved Weekly Schedule")

import pandas as pd

table_data = []
for session in my_schedule.get_schedule():
    table_data.append({
        "Day": session.time_slot.day,
        "Start Time": session.time_slot.start_time,
        "End Time": session.time_slot.end_time,
        "Course": getattr(session, 'course_id', 'Unknown'),
        "Type": session.session_type
    })

if table_data:
    df = pd.DataFrame(table_data)

    days_order = [
        "Sunday", "Monday", "Tuesday",
        "Wednesday", "Thursday", "Friday", "Saturday"
    ]
    df['Day'] = pd.Categorical(
    df['Day'], categories=days_order, ordered=True)

    df = df.sort_values(['Day', 'Start Time']).reset_index(drop=True)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No classes scheduled. Please check prerequisites.")

    # ==================================
    # Optimize Self-Study Plan
    # ==================================

st.divider()
st.subheader("📊 Suggested Study Plan")

from dataclass.optimizer import StudyOptimizer

total_hours = min(
    float(available_hours),
    float(max_daily_hours)
) if available_hours else 0.0

if valid_courses and total_hours > 0:
    study_plan = StudyOptimizer.allocate_study_time(
        available_hours=total_hours,
            courses=valid_courses
        )

for course_name, details in study_plan.items():
    st.write(f"### 📖 {course_name} ({details['course_id']})")

    col1, col2 = st.columns(2)
    col1.metric("Difficulty", f"{details['difficulty']}/5")
    col2.metric("Allocated Time",
                        f"{details['allocated_hours']} hours")

    st.divider()
else:
    st.warning("No available study hours or courses to optimize for this day.")
# ==========================================
# Standalone Test
# ==========================================
if __name__ == "__main__":
    class MockCourse:
        def __init__(self, course_id, name, difficulty_level):
            self.course_id = course_id
            self.name = name
            self.difficulty_level = difficulty_level

    test_courses = [
        MockCourse("CS201", "Data Structures", 4),
        MockCourse("MATH101", "Calculus I", 3),
        MockCourse("ENG101", "Academic Writing", 1)
    ]

    test_hours = 4.0

    print(f"\n--- Testing Optimizer with {test_hours} Hours ---")
    result = StudyOptimizer.allocate_study_time(test_hours, test_courses)

    import json
    print(json.dumps(result, indent=4, ensure_ascii=False))
=======
"""
Optimizer
======================
STATUS: Not implemented yet.

Intended purpose:
    This is the module Main/main.py refers to in its "Study Plan" tab
    comment ("optimizer.py is not implemented yet"). It should replace the
    temporary equal-split algorithm currently in Main/main.py by combining:
      - dataclass/schedule.py -> Schedule (conflict checks, free-time gaps)
      - study_planner/Priority_Calculation.py
      - study_planner/Study-hour_Allocation.py

Suggested signature:

    def build_optimized_plan(student, courses, schedule) -> dict:
        ...
"""
>>>>>>> 643d86d12bc5513599b57fd6914cdbbc67536a30
