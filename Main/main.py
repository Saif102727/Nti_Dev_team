import sys
from pathlib import Path

import streamlit as st


# ==========================================
# Project Path
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ==========================================
# Imports
# ==========================================

from loader import load_all_data
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
# Data File
# ==========================================

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "dummy_data.json"
)


# ==========================================
# Load Data
# ==========================================

@st.cache_data
def load_project_data():

    try:

        return load_all_data(
            DATA_FILE
        )

    except FileNotFoundError:

        st.error(
            f"Data file not found:\n\n{DATA_FILE}"
        )

        st.stop()

    except KeyError as error:

        st.error(
            f"Missing field in JSON data: {error}"
        )

        st.stop()

    except Exception as error:

        st.error(
            f"Error while loading project data:\n\n{error}"
        )

        st.stop()


student, courses, academic_events = (
    load_project_data()
)


# ==========================================
# Session State
# ==========================================

if "courses" not in st.session_state:

    st.session_state.courses = courses


if "points" not in st.session_state:

    st.session_state.points = student.points


if "study_time" not in st.session_state:

    st.session_state.study_time = 0.0


if "plan_generated" not in st.session_state:

    st.session_state.plan_generated = False


# ==========================================
# Header
# ==========================================

st.title(
    "📚 Intelligent Study Planner"
)

st.write(
    "Plan your study time intelligently, "
    "track your progress, and earn points."
)


# ==========================================
# Sidebar
# ==========================================

st.sidebar.title(
    "Student Dashboard"
)


# ------------------------------------------
# Student ID
# ------------------------------------------

st.sidebar.metric(
    "Student ID",
    student.student_id
)


# ------------------------------------------
# Points
# ------------------------------------------

st.sidebar.metric(
    "Points",
    st.session_state.points
)


# ------------------------------------------
# Study Time
# ------------------------------------------

st.sidebar.metric(
    "Study Time",
    f"{st.session_state.study_time:.1f} h"
)


st.sidebar.divider()


# ==========================================
# Daily Study Hours
# ==========================================

daily_hours = student.daily_study_hours


if daily_hours:

    days = list(
        daily_hours.keys()
    )

    selected_day = st.sidebar.selectbox(
        "Study Day",
        days
    )

    available_hours = daily_hours[
        selected_day
    ]

else:

    selected_day = None

    available_hours = 0

    st.sidebar.warning(
        "No daily study hours available."
    )


# ==========================================
# Available Hours
# ==========================================

st.sidebar.metric(
    "Available Hours",
    f"{float(available_hours):.1f} h"
)


# ==========================================
# Maximum Study Hours
# ==========================================

default_max_hours = max(
    1.0,
    float(available_hours)
)

default_max_hours = min(
    default_max_hours,
    24.0
)


max_daily_hours = st.sidebar.number_input(
    "Maximum Study Hours / Day",
    min_value=1.0,
    max_value=24.0,
    value=default_max_hours,
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
# COURSES TAB
# ==========================================

with tab1:

    st.header(
        "Your Courses"
    )

    st.info(
        "Courses are loaded automatically "
        "from the project JSON data."
    )

    st.divider()


    # ======================================
    # Courses
    # ======================================

    if st.session_state.courses:

        for course in st.session_state.courses:

            with st.expander(
                f"{course.name} ({course.course_id})"
            ):

                c1, c2, c3 = st.columns(3)


                # ----------------------------------
                # Difficulty
                # ----------------------------------

                c1.metric(
                    "Difficulty",
                    f"{course.difficulty_level}/5"
                )


                # ----------------------------------
                # Prerequisites
                # ----------------------------------

                prerequisites = (
                    course.prerequisites
                )

                if prerequisites:

                    prerequisites_text = (
                        ", ".join(
                            prerequisites
                        )
                    )

                else:

                    prerequisites_text = "None"


                c2.metric(
                    "Prerequisites",
                    prerequisites_text
                )


                # ----------------------------------
                # Sessions
                # ----------------------------------

                c3.metric(
                    "Sessions",
                    len(course.sessions)
                )


                # ----------------------------------
                # Class Sessions
                # ----------------------------------

                st.subheader(
                    "Class Sessions"
                )


                if course.sessions:

                    for session in course.sessions:

                        time_slot = (
                            session.time_slot
                        )

                        st.write(
                            f"**{session.session_type}** — "
                            f"{time_slot.day} | "
                            f"{time_slot.start_time} - "
                            f"{time_slot.end_time}"
                        )

                else:

                    st.info(
                        "No sessions available."
                    )


    else:

        st.info(
            "No courses available."
        )


    # ======================================
    # Academic Events
    # ======================================

    st.divider()

    st.subheader(
        "📅 Academic Events"
    )


    if academic_events:

        for event in academic_events:

            st.write(
                f"**Week {event.week_number}** — "
                f"{event.event_name} "
                f"({event.course_id})"
            )

    else:

        st.info(
            "No academic events available."
        )


# ==========================================
# STUDY PLAN TAB
# ==========================================

with tab2:

    st.header(
        "🧠 Intelligent Study Plan"
    )


    # --------------------------------------
    # Selected Day
    # --------------------------------------

    if selected_day:

        st.write(
            f"Selected day: "
            f"**{selected_day}**"
        )

        st.write(
            f"Available study time: "
            f"**{float(available_hours):.1f} hours**"
        )

        st.write(
            f"Maximum allowed: "
            f"**{max_daily_hours:.1f} hours**"
        )

    else:

        st.warning(
            "No study day is available."
        )


    st.divider()


    # ======================================
    # Courses Check
    # ======================================

    if not st.session_state.courses:

        st.info(
            "No courses available."
        )

    elif available_hours <= 0:

        st.warning(
            "There are no available study hours "
            "for this day."
        )

    else:

        # ==================================
        # Generate Plan
        # ==================================

        if st.button(
            "Generate Optimized Plan",
            type="primary"
        ):

            st.session_state.plan_generated = True


        # ==================================
        # Display Plan
        # ==================================

        if st.session_state.plan_generated:

            st.success(
                "Study plan generated!"
            )


            # ----------------------------------
            # Temporary Algorithm
            # ----------------------------------
            #
            # optimizer.py is not implemented yet.
            #
            # For now, the available time is
            # distributed equally between courses.
            #
            # This section will later be replaced
            # with the real optimizer.
            # ----------------------------------

            total_hours = min(
                float(available_hours),
                float(max_daily_hours)
            )


            course_count = len(
                st.session_state.courses
            )


            if course_count > 0:

                recommended_time = (
                    total_hours
                    / course_count
                )


                for course in (
                    st.session_state.courses
                ):

                    st.write(
                        f"### 📖 {course.name}"
                    )


                    st.write(
                        f"Difficulty: "
                        f"{course.difficulty_level}/5"
                    )


                    st.write(
                        f"Recommended study time: "
                        f"{recommended_time:.1f} hours"
                    )


                    st.divider()


# ==========================================
# STUDY TIMER TAB
# ==========================================

with tab3:

    render_timer(
        float(available_hours)
    )


# ==========================================
# REWARDS TAB
# ==========================================

with tab4:

    st.header(
        "🛍️ Reward Shop"
    )


    st.write(
        f"Your Points: "
        f"**{st.session_state.points}**"
    )


    col1, col2, col3 = st.columns(3)


    # ======================================
    # Theme
    # ======================================

    with col1:

        st.subheader(
            "🎨 Theme"
        )

        st.write(
            "Cost: 100 Points"
        )


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


    # ======================================
    # Banner
    # ======================================

    with col2:

        st.subheader(
            "🖼️ Banner"
        )

        st.write(
            "Cost: 150 Points"
        )


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


    # ======================================
    # Study Template
    # ======================================

    with col3:

        st.subheader(
            "📋 Study Template"
        )

        st.write(
            "Cost: 300 Points"
        )


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