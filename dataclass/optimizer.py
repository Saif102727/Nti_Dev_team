#This code for Test It isn't use it in main code
class StudyOptimizer:

    @staticmethod
    def allocate_study_time(available_hours: float, courses: list) -> dict:

        if not courses or available_hours <= 0:
            return {}

        total_difficulty = sum(course.difficulty_level for course in courses)
        study_plan = {}

        for course in courses:
            weight = course.difficulty_level / total_difficulty
            allocated_hours = round(weight * available_hours, 2)

            study_plan[course.name] = {
                "course_id": getattr(course, 'course_id', 'Unknown'),
                "difficulty": course.difficulty_level,
                "allocated_hours": allocated_hours
            }

        return study_plan

"""
I use This Code in Main Code
"""
# total_hours = min(
#     float(available_hours),
#     float(max_daily_hours),
# )

#          # ==================================
#          # Optimize Self-Study Plan
#          # ==================================
#  from dataclass.optimizer import StudyOptimizer

#   study_plan = StudyOptimizer.allocate_study_time(
#        available_hours=total_hours,
#        courses=course_list  
#        )

#    if study_plan:
#         for course_name, details in study_plan.items():

#             difficulty = details["difficulty"]
#             recommended_time = details["allocated_hours"]

#             with st.container(border=True):
#                 st.subheader(course_name)

#                 col1, col2 = st.columns(
#                     2,
#                     gap="medium",
#                 )

#                 with col1:
#                     st.metric(
#                         "Difficulty",
#                         f"{difficulty}/5",
#                     )

#                 with col2:
#                     st.metric(
#                         "Recommended Time",
#                         f"{recommended_time:.2f} h",
#                     )

#     else:
#         st.info(
#             "No study recommendations "
#             "could be generated."
#         )
