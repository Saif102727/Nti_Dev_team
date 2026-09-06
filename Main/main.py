import sys
import os
import streamlit as st
import json
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Main.Timer.Timer import render_timer


# ==========================================
# Page Configuration
# ==========================================

st.set_page_config(
    page_title="Intelligent Study Planner",
    page_icon="📚",
    layout="wide"
)


# ==========================================
# Load Test JSON Data
# ==========================================

DATA_FILE = Path("data/dummy_data.json")


def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        st.error(
            f"Data file not found: {DATA_FILE}"
        )
        st.stop()

    except json.JSONDecodeError:
        st.error(
            "The JSON file contains invalid data."
        )
        st.stop()


data = load_data()

student_data = data["student"]
course_data = data["courses"]
academic_events = data["academic_events"]


# ==========================================
# Session State
# ==========================================

if "courses" not in st.session_state:

    st.session_state.courses = []

    # Convert JSON courses to the format
    # currently used by the UI

    for course in course_data:

        st.session_state.courses.append({

            "id": course["course_id"],

            "name": course["name"],

            "difficulty": course["difficulty_level"],

            "performance": 5,

            "exam_days": 7,

            "remaining_material": 50,

            "unavailable_time": "",

            "prerequisites": course["prerequisites"],

            "sessions": course["sessions"]

        })


if "points" not in st.session_state:

    st.session_state.points = student_data.get(
        "points",999
    )


if "study_time" not in st.session_state:

    st.session_state.study_time = 0.0


if "plan_generated" not in st.session_state:

    st.session_state.plan_generated = False


# ==========================================
# Header
# ==========================================

st.title("📚 Intelligent Study Planner")

st.write(
    "Plan your study time intelligently, "
    "track your progress, and earn points."
)


# ==========================================
# Sidebar
# ==========================================

st.sidebar.title("Student Dashboard")

st.sidebar.metric(
    "Student ID",
    student_data["student_id"]
)

st.sidebar.metric(
    "Points",
    st.session_state.points
)

st.sidebar.metric(
    "Study Time",
    f"{st.session_state.study_time:.1f} h"
)

st.sidebar.divider()


# ==========================================
# Daily Study Hours
# ==========================================

daily_hours = student_data.get(
    "daily_study_hours",
    {}
)

days = list(daily_hours.keys())

selected_day = st.sidebar.selectbox(
    "Study Day",
    days
)

available_hours = daily_hours[selected_day]

st.sidebar.metric(
    "Available Hours",
    f"{available_hours} h"
)


max_daily_hours = st.sidebar.number_input(
    "Maximum Study Hours / Day",
    min_value=1.0,
    max_value=24.0,
    value=float(
        max(1, available_hours)
    ),
    step=0.5
)


# ==========================================
# Main Tabs
# ==========================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📚 Courses",
        "🧠 Study Plan",
        "⏱️ Study Timer",
        "🛍️ Rewards"
    ]
)


# ==========================================
# Courses Tab
# ==========================================

with tab1:

    st.header("Your Courses")

    st.info(
        "Courses are currently loaded "
        "automatically from the test JSON file."
    )

    st.divider()

    # Display courses

    if st.session_state.courses:

        for course in st.session_state.courses:

            with st.expander(
                f"{course['name']} "
                f"({course['id']})"
            ):

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Difficulty",
                    f"{course['difficulty']}/5"
                )

                c2.metric(
                    "Prerequisites",
                    (
                        ", ".join(
                            course["prerequisites"]
                        )
                        if course["prerequisites"]
                        else "None"
                    )
                )

                c3.metric(
                    "Sessions",
                    len(course["sessions"])
                )

                st.subheader(
                    "Class Sessions"
                )

                for session in course["sessions"]:

                    time_slot = session["time_slot"]

                    st.write(
                        f"**{session['session_type']}** — "
                        f"{time_slot['day']} | "
                        f"{time_slot['start_time']} - "
                        f"{time_slot['end_time']}"
                    )

    else:

        st.info(
            "No courses available."
        )

    # Academic Events
    st.divider()

    st.subheader(
        "📅 Academic Events"
    )

    for event in academic_events:

        st.write(
            f"**Week {event['week_number']}** — "
            f"{event['event_name']} "
            f"({event['course_id']})"
        )


# ==========================================
# Study Plan Tab
# ==========================================

with tab2:

    st.header("🧠 Intelligent Study Plan")

    st.write(
        f"Selected day: **{selected_day}**"
    )

    st.write(
        f"Available study time: "
        f"**{available_hours} hours**"
    )

    st.write(
        f"Maximum allowed: "
        f"**{max_daily_hours} hours**"
    )

    st.divider()

    if not st.session_state.courses:

        st.info(
            "No courses available."
        )

    else:

        if st.button(
            "Generate Optimized Plan",
            type="primary"
        ):

            st.session_state.plan_generated = True

        if st.session_state.plan_generated:

            st.success(
                "Study plan generated!"
            )

            # Temporary algorithm
            # until optimizer.py is connected.

            total_hours = min(
                float(available_hours),
                float(max_daily_hours)
            )

            course_count = len(
                st.session_state.courses
            )

            recommended_time = (
                total_hours / course_count
            )

            for course in st.session_state.courses:

                st.write(
                    f"### 📖 {course['name']}"
                )

                st.write(
                    f"Difficulty: "
                    f"{course['difficulty']}/5"
                )

                st.write(
                    f"Recommended study time: "
                    f"{recommended_time:.1f} hours"
                )

                st.divider()


# ==========================================
# Study Timer Tab
# ==========================================

with tab3:

    render_timer(available_hours)


# ==========================================
# Rewards Tab
# ==========================================

with tab4:

    st.header("🛍️ Reward Shop")

    st.write(
        f"Your Points: "
        f"**{st.session_state.points}**"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.subheader("🎨 Theme")

        st.write("Cost: 100 Points")

        if st.button(
            "Buy Theme"
        ):

            if st.session_state.points >= 100:

                st.session_state.points -= 100

                st.success(
                    "Theme purchased!"
                )

            else:

                st.error(
                    "Not enough points."
                )

    with col2:

        st.subheader("🖼️ Banner")

        st.write("Cost: 150 Points")

        if st.button(
            "Buy Banner"
        ):

            if st.session_state.points >= 150:

                st.session_state.points -= 150

                st.success(
                    "Banner purchased!"
                )

            else:

                st.error(
                    "Not enough points."
                )

    with col3:

        st.subheader("📋 Study Template")

        st.write("Cost: 300 Points")

        if st.button(
            "Buy Template"
        ):

            if st.session_state.points >= 300:

                st.session_state.points -= 300

                st.success(
                    "Template purchased!"
                )

            else:

                st.error(
                    "Not enough points."
                )


# ==========================================
# Footer
# ==========================================

st.divider()

st.caption(
    "Intelligent Study Planner | "
    "Planning • Studying • Tracking • Rewarding"
)