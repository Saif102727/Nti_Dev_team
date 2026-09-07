


import json


def calculate_difficulty(base_difficulty, prerequisites, w=0.6):

    if not prerequisites:
        return base_difficulty

    weighted_sum = 0
    influence_sum = 0

    for prerequisite in prerequisites.values():
        difficulty = prerequisite["personal_difficulty"]
        influence = prerequisite["influence"]

        weighted_sum += difficulty * influence
        influence_sum += influence

    prerequisite_difficulty = weighted_sum / influence_sum

    final_difficulty = (
        (1 - w) * base_difficulty
        + w * prerequisite_difficulty
    )

    return final_difficulty


# with open(r"data\dummy_data.json", "r") as file:
#     data = json.load(file)
# course_name = input("Enter the course: ")
# for course in data["courses"]:
#     if course["course_name"] == course_name:
#         selected_course = course
#         break

course = {
    "base_difficulty": 7.5,
    "prerequisites": {
        "Physics 2": {
            "personal_difficulty": 6.0,
            "influence": 0.75
        },
        "Math 2": {
            "personal_difficulty": 8.0,
            "influence": 1.0
        },
        "Math 1": {
            "personal_difficulty": 7.0,
            "influence": 0.5
        }
    }
}
difficulty = calculate_difficulty(course["base_difficulty"],course["prerequisites"])

print(f"Predicted difficulty: {difficulty:.2f}/10")