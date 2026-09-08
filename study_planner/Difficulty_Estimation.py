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


    # Example of loading a course from the real project data file:
    #
    # from pathlib import Path
    # data_path = Path(__file__).resolve().parent.parent / "data" / "dummy_data.json"
    # with open(data_path, "r", encoding="utf-8") as file:
    #     data = json.load(file)
