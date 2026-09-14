"""
Login / Registration GUI for the Intelligent Study Planner.

This is the Streamlit front-end for `auth_service.py`.
It collects user input, calls the authentication service,
and stores the authenticated student in Streamlit session state.
"""

import sys
from pathlib import Path

LOGIN_SYSTEM_DIR = Path(__file__).resolve().parent

if str(LOGIN_SYSTEM_DIR) not in sys.path:
    sys.path.insert(0, str(LOGIN_SYSTEM_DIR))

import streamlit as st

from db import init_db
from auth_service import (
    register,
    authenticate,
    AuthError,
    UsernameTakenError,
    WeakPasswordError,
    InvalidCredentialsError,
)


DAYS = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday",
]

STUDY_LOCATIONS = ["Home", "University", "Library", "Cafe"]


# =========================================================
# SESSION STATE
# =========================================================

def _init_session():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "auth_student" not in st.session_state:
        st.session_state.auth_student = None


def is_authenticated() -> bool:
    _init_session()
    return bool(
        st.session_state.authenticated
        and st.session_state.auth_student
    )


def logout():
    """Clears the session and returns the user to the login screen."""

    keys_to_clear = [
        "authenticated", "auth_student",
        "courses", "points", "study_time", "plan_generated",
        "unlocked_themes", "unlocked_banners", "unlocked_templates",
        "active_theme", "active_banner", "active_template",
        "selected_study_day", "max_daily_hours",
        "completed_sessions",
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)

    st.session_state.authenticated = False
    st.session_state.auth_student = None


# =========================================================
# SIDEBAR WIDGET
# =========================================================

def render_logout_button():
    """Small account card + logout button, meant for the sidebar."""

    _init_session()

    if not is_authenticated():
        return

    student = st.session_state.auth_student

    st.markdown(f"👤 **{student.get('name', 'Student')}**")
    st.caption(f"ID: {student.get('student_id', 'N/A')}")
    st.caption(f"📧 {student.get('email', 'N/A')}")

    if st.button(
        "🚪 Log out",
        key="logout_button",
        use_container_width=True,
    ):
        logout()
        st.rerun()


# =========================================================
# LOGIN FORM
# =========================================================

def _render_login_form():
    with st.form("login_form", clear_on_submit=False):

        username = st.text_input(
            "Username",
            key="login_username",
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password",
        )

        submitted = st.form_submit_button(
            "Log in",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    if not username or not password:
        st.error("Please enter both username and password.")
        return

    try:
        student = authenticate(username, password)

    except InvalidCredentialsError as error:
        st.error(str(error))

    except AuthError as error:
        st.error(f"Login failed: {error}")

    else:
        st.session_state.authenticated = True
        st.session_state.auth_student = student

        st.success(
            f"Welcome back, {student['name']}! 🎉"
        )

        st.rerun()


# =========================================================
# REGISTER FORM
# =========================================================

def _render_register_form():

    with st.form("register_form", clear_on_submit=False):

        st.markdown("**Account**")

        c1, c2 = st.columns(2)

        with c1:

            username = st.text_input(
                "Choose a username",
                key="reg_username",
            )

            password = st.text_input(
                "Choose a password",
                type="password",
                key="reg_password",
            )

        with c2:

            email = st.text_input(
                "Email",
                placeholder="example@gmail.com",
                key="reg_email",
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password",
                key="reg_confirm_password",
            )

            st.caption(
                "Password must be at least 6 characters."
            )

        st.divider()

        st.markdown("**Profile**")

        c3, c4 = st.columns(2)

        with c3:

            name = st.text_input(
                "Full name",
                key="reg_name",
            )

            university = st.text_input(
                "University",
                key="reg_university",
            )

            certificate = st.text_input(
                "Certificate (e.g. High School Diploma)",
                key="reg_certificate",
            )

        with c4:

            age = st.number_input(
                "Age",
                min_value=10,
                max_value=100,
                value=20,
                key="reg_age",
            )

            faculty = st.text_input(
                "Faculty",
                key="reg_faculty",
            )

            preferred_location = st.selectbox(
                "Preferred study location",
                STUDY_LOCATIONS,
                key="reg_location",
            )

        st.divider()

        st.markdown("**Weekly study availability**")

        st.caption(
            "How many hours can you study on each day? "
            "This powers the Study Plan and Study Timer tabs."
        )

        day_columns = st.columns(7)
        daily_hours = {}

        for column, day in zip(day_columns, DAYS):

            with column:

                daily_hours[day] = st.number_input(
                    day[:3],
                    min_value=0.0,
                    max_value=16.0,
                    value=2.0,
                    step=0.5,
                    key=f"reg_hours_{day}",
                )

        free_days = st.multiselect(
            "Free days (no classes)",
            DAYS,
            key="reg_free_days",
        )

        submitted = st.form_submit_button(
            "Create account",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    if not username or not password or not name or not email:
        st.error(
            "Username, password, name and email are required."
        )
        return

    if password != confirm_password:
        st.error("Passwords do not match.")
        return

    try:

        student_id = register(
            username=username,
            password=password,
            name=name,
            age=int(age),
            university=university,
            faculty=faculty,
            certificate=certificate,
            email=email,
            daily_study_hours=daily_hours,
            free_days=free_days,
            preferred_study_location=preferred_location,
        )

    except UsernameTakenError as error:
        st.error(str(error))

    except WeakPasswordError as error:
        st.error(str(error))

    except AuthError as error:
        st.error(f"Could not create account: {error}")

    else:

        student = authenticate(
            username,
            password,
        )

        st.session_state.authenticated = True
        st.session_state.auth_student = student

        st.success(
            f"Account created! Your student ID is {student_id}."
        )

        st.rerun()


# =========================================================
# PUBLIC ENTRY POINT
# =========================================================

def render_login_page():
    """
    Renders the full login/registration screen.
    """

    init_db()
    _init_session()

    st.markdown(
        "<h1 style='text-align:center; margin-bottom:0;'>"
        "📚 Intelligent Study Planner"
        "</h1>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p style='text-align:center; opacity:0.75; margin-top:4px;'>"
        "Log in or create an account to continue"
        "</p>",
        unsafe_allow_html=True,
    )

    st.write("")

    _, center, _ = st.columns([1, 2, 1])

    with center:

        login_tab, register_tab = st.tabs(
            ["🔐 Log in", "🆕 Create account"]
        )

        with login_tab:
            _render_login_form()

        with register_tab:
            _render_register_form()