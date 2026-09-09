# Nti_Dev_team — Intelligent Study Planner

A Streamlit app that helps a student plan study time around their courses,
class sessions, and academic events, then track focused study sessions
with a Pomodoro-style timer and earn reward points.

## Project Structure

```
Nti_Dev_team/
├── model.py                    # Core dataclasses: Student, Course, Session, Time, AcademicEvent
├── loader.py                   # Loads data/dummy_data.json into the model.py dataclasses
├── requirements.txt
│
├── data/
│   └── dummy_data.json         # Sample student/course/event data
│   └── data_parser.py          # Commit
│ 
│── Login_systemV2\
│   └── auth_service.py         # Commit
│   └── bulk_register.py        # Commit
│   └── cli_test.py             # Commit
│   └── db.py                   # Commit
│   └── login_page.py           # Commit
│   └── security.py             # Commit
│ 
├── dataclass/
│   ├── schedule.py             # Schedule: conflict checks, prerequisite checks, free-time gaps
│   └── optimizer.py            # TODO: study-plan optimizer (see docstring)
│ 
├── study_planner/
│   ├── Difficulty_Estimation.py   # Implemented: personalized course difficulty
│   ├── Priority_Calculation.py    # TODO
│   ├── Schedule_Generation.py     # TODO
│   ├── Schedule_Optimization.py   # TODO
│   ├── Study-hour_Allocation.py   # TODO
│   └── Notifications.py           # TODO
│ 
└── Main/
    ├── main.py                 # Streamlit entry point / UI
    └── Timer/
        └── Timer.py            # Pomodoro-style study timer + points
```

Files marked **TODO** contain only a docstring describing their intended
purpose and a suggested function signature — they are placeholders for
features that haven't been implemented yet.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python -m streamlit run Main/main.py
```

The app loads sample data automatically from `data/dummy_data.json` — no
extra configuration needed.

## Notes for contributors

- Don't commit `__pycache__/` or `.vscode/` — they're now excluded via
  `.gitignore`.
- `Main/main.py` currently uses a temporary "split hours equally across
  courses" algorithm on the Study Plan tab. The real optimization logic
  belongs in `dataclass/optimizer.py`, drawing on `dataclass/schedule.py`
  and the `study_planner/` modules once they're implemented.
- All dataclasses live in `model.py` — keep field names there in sync with
  `loader.py` and `data/dummy_data.json`.
