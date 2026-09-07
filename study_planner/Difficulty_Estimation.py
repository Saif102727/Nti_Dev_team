"""
Difficulty Estimation
======================
Estimates the *effective* difficulty of a course for a specific student by
blending the course's base difficulty with how hard the student found its
prerequisites (weighted by how strongly each prerequisite influences the
new course).
"""

import json


def calculate_difficulty(base_difficulty, prerequisites, w=0.6):
    """
    Calculate a personalized difficulty score for a course.

    Args:
        base_difficulty (float): The course's official difficulty (0-10).
        prerequisites (dict): Mapping of prerequisite name -> {
            "personal_difficulty": float,  # how hard the student found it
            "influence": float              # how relevant it is to this course
        }
        w (float): Weight given to prerequisite history vs. base difficulty
            (0 = ignore prerequisites, 1 = ignore base difficulty).

    Returns:
        float: Estimated personal difficulty for the course.
    """

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


# ==========================================
# Manual test / demo cases
# ==========================================
#
# Run this file directly (`python Difficulty_Estimation.py`) to see sample
# output. This block does NOT run when the module is imported elsewhere.

if __name__ == "__main__":

    sample_cases = [
        {
            "label": "No prerequisites",
            "base_difficulty": 6.5,
            "prerequisites": {}
        },
        {
            "label": "Single easy prerequisite",
            "base_difficulty": 7.0,
            "prerequisites": {
                "Programming 1": {"personal_difficulty": 8.0, "influence": 1.0}
            }
        },
        {
            "label": "Multiple prerequisites, mixed influence",
            "base_difficulty": 7.5,
            "prerequisites": {
                "Physics 2": {"personal_difficulty": 6.0, "influence": 0.75},
                "Math 2": {"personal_difficulty": 8.0, "influence": 1.0},
                "Math 1": {"personal_difficulty": 7.0, "influence": 0.5}
            }
        },
        {
            "label": "Student struggled with a highly-influential prerequisite",
            "base_difficulty": 8.0,
            "prerequisites": {
                "Math 2": {"personal_difficulty": 3.0, "influence": 1.0},
                "Physics 2": {"personal_difficulty": 4.0, "influence": 0.75}
            }
        }
    ]

    for case in sample_cases:
        difficulty = calculate_difficulty(
            case["base_difficulty"],
            case["prerequisites"]
        )
        print(f"{case['label']}: {difficulty:.2f}/10")

    # Example of loading a course from the real project data file:
    #
    # from pathlib import Path
    # data_path = Path(__file__).resolve().parent.parent / "data" / "dummy_data.json"
    # with open(data_path, "r", encoding="utf-8") as file:
    #     data = json.load(file)
