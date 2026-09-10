# Nti_Dev_team — Intelligent Study Planner

A Streamlit app that helps a student plan study time around their courses,
class sessions, and academic events, then track focused study sessions
with a Pomodoro-style timer and earn reward points.

## Project Structure

```text
Nti_Dev_team/
├── models.py                   # Core dataclasses: Student, Course, Session, Time, AcademicEvent
├── loader.py                   # Loads shared data/dummy_data.json into the models.py dataclasses
├── requirements.txt
│
├── data/
│   ├── dummy_data.json         # Shared catalog of courses and academic events
│   └── schedule.json           # Actual lecture schedules (4 predefined schedules)
│
├── Login_systemV2/
│   ├── auth_service.py         # Core auth logic (register, authenticate, update_points)
│   ├── db.py                   # SQLite database setup (app_data.db)
│   ├── login_page.py           # Streamlit login/registration UI
│   ├── security.py             # Password encryption (salt + hash)
│   └── bulk_register.py, cli_test.py, diagnose_login.py # Utilities & testing tools
│
├── dataclass/
│   ├── schedule.py             # Schedule logic: conflict checks, prerequisite checks, free-time gaps
│   └── optimizer.py            # Simple study-plan allocator (distributes hours by difficulty)
│
├── study_planner/              # The "Smart Pipeline" Engine (Fully Implemented)
│   ├── Difficulty_Estimation.py# Calculates personalized course difficulty
│   ├── Priority_Calculation.py # Calculates study priority (AHP: deadline, weakness, etc.)
│   ├── Studyhour_Allocation.py # Allocates available hours based on course priority
│   ├── Schedule_Generation.py  # Backtracking algorithm to slot sessions without conflicts
│   └── Schedule_Optimization.py# Evaluates generated schedules and returns the best one (Score/100)
│
└── Main/
    └── main.py                 # Streamlit entry point / UI (4 Tabs)
```
## Setup

```bash
python -m venv .venv
source .venv/bin/activate       
pip install -r requirements.txt
```
## Run

```bash
python -m streamlit run Main/main.py
```
The app requires the user to log in first. Real student data (study hours, enrolled courses, points) is loaded dynamically from the `SQLite` database, while shared courses/events are loaded from `data/dummy_data.json`.

## Notes for contributors


- Don't commit `__pycache__/` or `.vscode/` — they're now excluded via `.gitignore`.
- `Main/main.py` uses two planning methods in the Study Plan tab: a simple algorithm (`dataclass/optimizer.py`) and a fully optimized "Smart Weekly Schedule" that utilizes the complete `study_planner/` pipeline.
- **Data Integration:** The `study_planner` pipeline originally relied on dummy data. It now uses parallel adapter functions (e.g., `_real_data` / `_for_real_student`) to seamlessly convert real user data from the SQLite login system into the formats required by the algorithms.
- All dataclasses live in `models.py` — keep field names there in sync with `loader.py` and `data/dummy_data.json`.
