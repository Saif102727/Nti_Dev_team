import sys
from pathlib import Path

import streamlit as st


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =========================================================
# IMPORTS
# =========================================================

from loader import load_courses_and_events

from Main.Timer.Timer import render_timer

from Main.styles import (
    THEMES,
    BANNERS,
    STUDY_TEMPLATES,
    apply_styles,
    render_app_header,
    render_banner,
    get_active_template,
)

# Login system: make Login_system's plain (non-package) modules
# importable, then pull in the GUI + persistence helpers.
LOGIN_SYSTEM_DIR = PROJECT_ROOT / "Login_system"

if str(LOGIN_SYSTEM_DIR) not in sys.path:
    sys.path.insert(0, str(LOGIN_SYSTEM_DIR))

from login_page import render_login_page, render_logout_button, is_authenticated
from auth_service import update_points


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Intelligent Study Planner",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# AUTHENTICATION GATE
# =========================================================
#
# Nothing below this point should run until the user is logged in:
# the dashboard is built around *their* student record, not a static
# demo file.

if not is_authenticated():
    render_login_page()
    st.stop()

student = st.session_state.auth_student


# =========================================================
# CONSTANTS
# =========================================================

CATALOG_FILE = PROJECT_ROOT / "data" / "mock_university_data.json"


# =========================================================
# DATA LOADING
# =========================================================
#
# Courses and academic events are a shared catalog (every student
# studies the same courses), loaded once and cached. The student
# themself is NOT loaded from this file — they come from the login
# system above, so points, study hours, etc. are the real,
# per-account values from the database.

@st.cache_data(show_spinner=False)
def load_project_data():
    return load_courses_and_events(CATALOG_FILE)


try:
    courses, academic_events = load_project_data()

except Exception as error:
    st.error("Unable to load project data.")
    st.exception(error)
    st.stop()


# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================

def initialize_session_state():

    defaults = {
        # -------------------------------------------------
        # Core data
        # -------------------------------------------------

        "courses": list(courses),

        "points": int(
            (
                student.get("points", 0)
                if isinstance(student, dict)
                else getattr(student, "points", 0)
            )
            or 0
        ),

        "study_time": 0.0,

        "plan_generated": False,

        # -------------------------------------------------
        # Reward inventory
        # -------------------------------------------------

        "unlocked_themes": [
            "default"
        ],

        "unlocked_banners": [
            "default_banner"
        ],

        "unlocked_templates": [
            "pomodoro"
        ],

        # -------------------------------------------------
        # Active customization
        # -------------------------------------------------

        "active_theme": "default",

        "active_banner": "default_banner",

        "active_template": "pomodoro",

        # -------------------------------------------------
        # UI synchronization flags
        # -------------------------------------------------

        "theme_ui_sync": False,

        "banner_ui_sync": False,

        "template_ui_sync": False,

        # -------------------------------------------------
        # Sidebar state
        # -------------------------------------------------

        "selected_study_day": None,

        # IMPORTANT:
        # Never initialize this as None because it is later
        # used by number_input and formatted as a float.
        "max_daily_hours": 0.0,
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


initialize_session_state()


# =========================================================
# SESSION STATE SANITIZATION
# =========================================================

def sanitize_numeric_state():

    # -----------------------------------------------------
    # Points
    # -----------------------------------------------------

    try:
        st.session_state.points = int(
            st.session_state.get("points", 0) or 0
        )
    except (TypeError, ValueError):
        st.session_state.points = 0

    # -----------------------------------------------------
    # Study time
    # -----------------------------------------------------

    try:
        st.session_state.study_time = float(
            st.session_state.get("study_time", 0.0) or 0.0
        )
    except (TypeError, ValueError):
        st.session_state.study_time = 0.0

    # -----------------------------------------------------
    # Maximum daily hours
    #
    # This is the important fix for the NoneType error.
    # -----------------------------------------------------

    raw_max_hours = st.session_state.get(
        "max_daily_hours",
        0.0,
    )

    try:
        if raw_max_hours is None:
            raw_max_hours = 0.0

        raw_max_hours = float(raw_max_hours)

    except (TypeError, ValueError):
        raw_max_hours = 0.0

    if raw_max_hours < 0:
        raw_max_hours = 0.0

    st.session_state.max_daily_hours = raw_max_hours


sanitize_numeric_state()


# =========================================================
# INVENTORY VALIDATION
# =========================================================

def validate_inventory():

    # =====================================================
    # THEMES
    # =====================================================

    unlocked_themes = st.session_state.get(
        "unlocked_themes",
        [],
    )

    if not isinstance(unlocked_themes, list):
        unlocked_themes = []

    unlocked_themes = [
        key
        for key in unlocked_themes
        if key in THEMES
    ]

    unlocked_themes = list(
        dict.fromkeys(unlocked_themes)
    )

    if "default" not in unlocked_themes:
        unlocked_themes.insert(
            0,
            "default",
        )

    st.session_state.unlocked_themes = unlocked_themes

    if (
        st.session_state.active_theme
        not in unlocked_themes
    ):
        st.session_state.active_theme = "default"


    # =====================================================
    # BANNERS
    # =====================================================

    unlocked_banners = st.session_state.get(
        "unlocked_banners",
        [],
    )

    if not isinstance(unlocked_banners, list):
        unlocked_banners = []

    unlocked_banners = [
        key
        for key in unlocked_banners
        if key in BANNERS
    ]

    unlocked_banners = list(
        dict.fromkeys(unlocked_banners)
    )

    if "default_banner" not in unlocked_banners:
        unlocked_banners.insert(
            0,
            "default_banner",
        )

    st.session_state.unlocked_banners = unlocked_banners

    if (
        st.session_state.active_banner
        not in unlocked_banners
    ):
        st.session_state.active_banner = "default_banner"


    # =====================================================
    # TEMPLATES
    # =====================================================

    unlocked_templates = st.session_state.get(
        "unlocked_templates",
        [],
    )

    if not isinstance(unlocked_templates, list):
        unlocked_templates = []

    unlocked_templates = [
        key
        for key in unlocked_templates
        if key in STUDY_TEMPLATES
    ]

    unlocked_templates = list(
        dict.fromkeys(unlocked_templates)
    )

    if "pomodoro" not in unlocked_templates:
        unlocked_templates.insert(
            0,
            "pomodoro",
        )

    st.session_state.unlocked_templates = unlocked_templates

    if (
        st.session_state.active_template
        not in unlocked_templates
    ):
        st.session_state.active_template = "pomodoro"


validate_inventory()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_value(
    obj,
    *keys,
    default=None,
):
    """
    Supports both dataclass/object data and dictionaries.
    """

    for key in keys:

        if isinstance(obj, dict):

            if key in obj:
                return obj[key]

        else:

            value = getattr(
                obj,
                key,
                None,
            )

            if value is not None:
                return value

    return default


def safe_float(
    value,
    default=0.0,
):
    try:

        if value is None:
            return float(default)

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return float(default)


def safe_int(
    value,
    default=0,
):
    try:

        if value is None:
            return int(default)

        return int(value)

    except (
        TypeError,
        ValueError,
    ):

        return int(default)


# =========================================================
# THEME CALLBACK
# =========================================================

def change_theme_from_sidebar():

    selected = st.session_state.get(
        "sidebar_theme_selector",
        "default",
    )

    if selected not in THEMES:
        selected = "default"

    if selected not in st.session_state.unlocked_themes:
        selected = "default"

    st.session_state.active_theme = selected


# =========================================================
# BANNER CALLBACK
# =========================================================

def change_banner_from_sidebar():

    selected = st.session_state.get(
        "sidebar_banner_selector",
        "default_banner",
    )

    if selected not in BANNERS:
        selected = "default_banner"

    if selected not in st.session_state.unlocked_banners:
        selected = "default_banner"

    st.session_state.active_banner = selected


# =========================================================
# TEMPLATE CALLBACK
# =========================================================

def change_template_from_sidebar():

    selected = st.session_state.get(
        "sidebar_template_selector",
        "pomodoro",
    )

    if selected not in STUDY_TEMPLATES:
        selected = "pomodoro"

    if selected not in st.session_state.unlocked_templates:
        selected = "pomodoro"

    st.session_state.active_template = selected


# =========================================================
# SHOP ACTIVATION
# =========================================================

def activate_theme(key: str):

    if key not in THEMES:
        return False

    if key not in st.session_state.unlocked_themes:
        return False

    st.session_state.active_theme = key

    # Synchronize widget on NEXT rerun.
    st.session_state.theme_ui_sync = True

    return True


def activate_banner(key: str):

    if key not in BANNERS:
        return False

    if key not in st.session_state.unlocked_banners:
        return False

    st.session_state.active_banner = key

    st.session_state.banner_ui_sync = True

    return True


def activate_template(key: str):

    if key not in STUDY_TEMPLATES:
        return False

    if key not in st.session_state.unlocked_templates:
        return False

    st.session_state.active_template = key

    st.session_state.template_ui_sync = True

    return True


# =========================================================
# SHOP PURCHASE
# =========================================================

def buy_item(
    item_type: str,
    key: str,
    price: int,
) -> bool:

    price = max(
        0,
        safe_int(price),
    )

    # -----------------------------------------------------
    # Validate item
    # -----------------------------------------------------

    if item_type == "theme":

        if key not in THEMES:
            return False

        inventory = st.session_state.unlocked_themes

    elif item_type == "banner":

        if key not in BANNERS:
            return False

        inventory = st.session_state.unlocked_banners

    elif item_type == "template":

        if key not in STUDY_TEMPLATES:
            return False

        inventory = st.session_state.unlocked_templates

    else:

        return False


    # -----------------------------------------------------
    # Already unlocked
    # -----------------------------------------------------

    if key in inventory:

        if item_type == "theme":
            activate_theme(key)

        elif item_type == "banner":
            activate_banner(key)

        elif item_type == "template":
            activate_template(key)

        return True


    # -----------------------------------------------------
    # Check points
    # -----------------------------------------------------

    current_points = safe_int(
        st.session_state.get(
            "points",
            0,
        )
    )

    if current_points < price:
        return False


    # -----------------------------------------------------
    # Deduct points
    # -----------------------------------------------------

    st.session_state.points = (
        current_points - price
    )


    # -----------------------------------------------------
    # Unlock item
    # -----------------------------------------------------

    inventory.append(key)


    # -----------------------------------------------------
    # Activate
    # -----------------------------------------------------

    if item_type == "theme":

        activate_theme(key)

    elif item_type == "banner":

        activate_banner(key)

    elif item_type == "template":

        activate_template(key)


    return True


# =========================================================
# STUDY PLAN GENERATOR
# =========================================================

def generate_study_recommendations(
    course_list,
    available_hours,
):

    if not course_list:
        return []

    available_hours = safe_float(
        available_hours,
        0.0,
    )

    available_hours = max(
        0.0,
        available_hours,
    )

    if available_hours <= 0:
        return []

    weights = []

    for course in course_list:

        difficulty = get_value(
            course,
            "difficulty_level",
            "difficulty",
            default=1,
        )

        difficulty = safe_float(
            difficulty,
            1.0,
        )

        difficulty = max(
            1.0,
            min(
                5.0,
                difficulty,
            ),
        )

        weight = 1.0 + (
            difficulty * 0.5
        )

        weights.append(weight)


    total_weight = sum(weights)

    if total_weight <= 0:
        return []


    recommendations = []

    for course, weight in zip(
        course_list,
        weights,
    ):

        recommended_time = (
            available_hours
            * weight
            / total_weight
        )

        recommendations.append(
            (
                course,
                recommended_time,
            )
        )


    return recommendations


# =========================================================
# APPLY GUI
# =========================================================

apply_styles()

render_app_header()

render_banner()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title(
        "Student Dashboard"
    )

    render_logout_button()

    st.divider()


    # =====================================================
    # STUDENT INFORMATION
    # =====================================================

    student_id = get_value(
        student,
        "student_id",
        default="N/A",
    )

    st.metric(
        "Student ID",
        str(student_id),
    )

    st.metric(
        "Points",
        safe_int(
            st.session_state.get(
                "points",
                0,
            )
        ),
    )

    current_study_time = safe_float(
        st.session_state.get(
            "study_time",
            0.0,
        ),
        0.0,
    )

    st.metric(
        "Study Time",
        f"{current_study_time:.1f} h",
    )


    st.divider()


    # =====================================================
    # CUSTOMIZATION
    # =====================================================

    st.subheader(
        "Customization"
    )


    # =====================================================
    # THEME
    # =====================================================

    theme_options = {
        key: THEMES[key]["name"]
        for key in st.session_state.unlocked_themes
        if key in THEMES
    }

    if not theme_options:

        theme_options = {
            "default": THEMES["default"]["name"]
        }

        st.session_state.unlocked_themes = [
            "default"
        ]

    current_theme = st.session_state.active_theme

    if current_theme not in theme_options:

        current_theme = "default"

        st.session_state.active_theme = "default"

    theme_keys = list(
        theme_options.keys()
    )


    # -----------------------------------------------------
    # IMPORTANT:
    # Widget state is synchronized BEFORE creating widget.
    # Never modify this key after selectbox is created.
    # -----------------------------------------------------

    if st.session_state.get(
        "theme_ui_sync",
        False,
    ):

        st.session_state[
            "sidebar_theme_selector"
        ] = current_theme

        st.session_state.theme_ui_sync = False


    if (
        "sidebar_theme_selector"
        not in st.session_state
    ):

        st.session_state[
            "sidebar_theme_selector"
        ] = current_theme


    selected_theme = st.selectbox(
        "Active Theme",
        options=theme_keys,
        format_func=lambda key: theme_options[key],
        key="sidebar_theme_selector",
        on_change=change_theme_from_sidebar,
    )


    # =====================================================
    # BANNER
    # =====================================================

    banner_options = {
        key: BANNERS[key]["name"]
        for key in st.session_state.unlocked_banners
        if key in BANNERS
    }

    if not banner_options:

        banner_options = {
            "default_banner": BANNERS[
                "default_banner"
            ]["name"]
        }

        st.session_state.unlocked_banners = [
            "default_banner"
        ]

    current_banner = st.session_state.active_banner

    if current_banner not in banner_options:

        current_banner = "default_banner"

        st.session_state.active_banner = (
            "default_banner"
        )

    banner_keys = list(
        banner_options.keys()
    )


    if st.session_state.get(
        "banner_ui_sync",
        False,
    ):

        st.session_state[
            "sidebar_banner_selector"
        ] = current_banner

        st.session_state.banner_ui_sync = False


    if (
        "sidebar_banner_selector"
        not in st.session_state
    ):

        st.session_state[
            "sidebar_banner_selector"
        ] = current_banner


    selected_banner = st.selectbox(
        "Active Banner",
        options=banner_keys,
        format_func=lambda key: banner_options[key],
        key="sidebar_banner_selector",
        on_change=change_banner_from_sidebar,
    )


    # =====================================================
    # TEMPLATE
    # =====================================================

    template_options = {
        key: STUDY_TEMPLATES[key]["name"]
        for key in st.session_state.unlocked_templates
        if key in STUDY_TEMPLATES
    }

    if not template_options:

        template_options = {
            "pomodoro": STUDY_TEMPLATES[
                "pomodoro"
            ]["name"]
        }

        st.session_state.unlocked_templates = [
            "pomodoro"
        ]

    current_template = st.session_state.active_template

    if current_template not in template_options:

        current_template = "pomodoro"

        st.session_state.active_template = (
            "pomodoro"
        )

    template_keys = list(
        template_options.keys()
    )


    if st.session_state.get(
        "template_ui_sync",
        False,
    ):

        st.session_state[
            "sidebar_template_selector"
        ] = current_template

        st.session_state.template_ui_sync = False


    if (
        "sidebar_template_selector"
        not in st.session_state
    ):

        st.session_state[
            "sidebar_template_selector"
        ] = current_template


    selected_template = st.selectbox(
        "Active Study Template",
        options=template_keys,
        format_func=lambda key: template_options[key],
        key="sidebar_template_selector",
        on_change=change_template_from_sidebar,
    )


    st.divider()


    # =====================================================
    # STUDY AVAILABILITY
    # =====================================================

    st.subheader(
        "Study Availability"
    )

    daily_hours = get_value(
        student,
        "daily_study_hours",
        default={},
    )

    if not isinstance(
        daily_hours,
        dict,
    ):
        daily_hours = {}


    if daily_hours:

        days = list(
            daily_hours.keys()
        )

        previous_day = st.session_state.get(
            "selected_study_day"
        )

        if previous_day not in days:
            previous_day = days[0]


        # Initialize widget state before creating it.
        if (
            "selected_study_day"
            not in st.session_state
            or st.session_state.selected_study_day
            not in days
        ):

            st.session_state.selected_study_day = (
                previous_day
            )


        selected_day = st.selectbox(
            "Study Day",
            options=days,
            key="selected_study_day",
        )


        available_hours = safe_float(
            daily_hours.get(
                selected_day,
                0,
            ),
            0.0,
        )

    else:

        selected_day = None

        available_hours = 0.0

        st.warning(
            "No daily study hours available."
        )


    st.metric(
        "Available Hours",
        f"{available_hours:.1f} h",
    )


    # =====================================================
    # MAX DAILY HOURS
    # =====================================================

    if available_hours > 0:

        max_allowed = min(
            24.0,
            max(
                0.5,
                available_hours,
            ),
        )

        # ---------------------------------------------
        # Read and sanitize previous value
        # ---------------------------------------------

        old_max = st.session_state.get(
            "max_daily_hours",
            0.0,
        )

        old_max = safe_float(
            old_max,
            max_allowed,
        )

        if old_max <= 0:
            old_max = max_allowed

        if old_max > max_allowed:
            old_max = max_allowed


        # ---------------------------------------------
        # IMPORTANT:
        # If number_input already exists in session
        # state, do not assign its widget key here.
        # ---------------------------------------------

        if (
            "max_daily_hours"
            not in st.session_state
        ):

            st.session_state.max_daily_hours = (
                old_max
            )


        max_daily_hours = st.number_input(
            "Maximum Study Hours / Day",
            min_value=0.5,
            max_value=float(max_allowed),
            value=float(old_max),
            step=0.5,
            key="max_daily_hours",
        )


        # ---------------------------------------------
        # Final safety conversion
        # ---------------------------------------------

        max_daily_hours = safe_float(
            max_daily_hours,
            max_allowed,
        )

        max_daily_hours = max(
            0.5,
            min(
                max_allowed,
                max_daily_hours,
            ),
        )

    else:

        max_daily_hours = 0.0

        st.caption(
            "No study hours available for this day."
        )


# =========================================================
# FINAL SAFETY
# =========================================================

available_hours = safe_float(
    available_hours,
    0.0,
)

max_daily_hours = safe_float(
    max_daily_hours,
    0.0,
)


# =========================================================
# MAIN TABS
# =========================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Courses",
        "Study Plan",
        "Study Timer",
        "Reward Shop",
    ]
)


# =========================================================
# TAB 1 — COURSES
# =========================================================

with tab1:

    st.header(
        "Your Courses"
    )

    st.info(
        "Courses are loaded automatically "
        "from the project JSON data."
    )

    st.divider()

    course_list = st.session_state.courses


    if course_list:

        for course in course_list:

            course_name = get_value(
                course,
                "name",
                default="Unnamed Course",
            )

            course_id = get_value(
                course,
                "course_id",
                default="N/A",
            )

            difficulty = get_value(
                course,
                "difficulty_level",
                "difficulty",
                default=0,
            )

            prerequisites = get_value(
                course,
                "prerequisites",
                default=[],
            )

            sessions = get_value(
                course,
                "sessions",
                default=[],
            )


            if not isinstance(
                prerequisites,
                list,
            ):
                prerequisites = []


            if not isinstance(
                sessions,
                list,
            ):
                sessions = []


            difficulty = safe_int(
                difficulty,
                0,
            )


            with st.expander(
                f"{course_name} ({course_id})"
            ):

                c1, c2, c3 = st.columns(
                    3,
                    gap="medium",
                )


                with c1:

                    st.metric(
                        "Difficulty",
                        f"{difficulty}/5",
                    )


                with c2:

                    prerequisites_text = (
                        ", ".join(
                            map(
                                str,
                                prerequisites,
                            )
                        )
                        if prerequisites
                        else "None"
                    )

                    st.metric(
                        "Prerequisites",
                        prerequisites_text,
                    )


                with c3:

                    st.metric(
                        "Sessions",
                        len(sessions),
                    )


                st.divider()

                st.subheader(
                    "Class Sessions"
                )


                if sessions:

                    for session in sessions:

                        session_type = get_value(
                            session,
                            "session_type",
                            default="Session",
                        )

                        time_slot = get_value(
                            session,
                            "time_slot",
                            default=None,
                        )


                        if time_slot:

                            day = get_value(
                                time_slot,
                                "day",
                                default="N/A",
                            )

                            start_time = get_value(
                                time_slot,
                                "start_time",
                                default="N/A",
                            )

                            end_time = get_value(
                                time_slot,
                                "end_time",
                                default="N/A",
                            )


                            st.write(
                                f"**{session_type}** — "
                                f"{day} | "
                                f"{start_time} - "
                                f"{end_time}"
                            )

                        else:

                            st.write(
                                f"**{session_type}**"
                            )

                else:

                    st.info(
                        "No sessions available."
                    )

    else:

        st.info(
            "No courses available."
        )


    # =====================================================
    # ACADEMIC EVENTS
    # =====================================================

    st.divider()

    st.subheader(
        "Academic Events"
    )


    if academic_events:

        for event in academic_events:

            week = get_value(
                event,
                "week_number",
                default="N/A",
            )

            event_name = get_value(
                event,
                "event_name",
                default="Event",
            )

            event_course_id = get_value(
                event,
                "course_id",
                default="N/A",
            )


            st.write(
                f"**Week {week}** — "
                f"{event_name} "
                f"({event_course_id})"
            )

    else:

        st.info(
            "No academic events available."
        )



# =========================================================
# TAB 2 — STUDY PLAN
# =========================================================

with tab2:

    st.header(
        "Intelligent Study Plan"
    )

    if selected_day:

        c1, c2, c3 = st.columns(
            3,
            gap="medium",
        )

        with c1:

            st.metric(
                "Selected Day",
                selected_day,
            )

        with c2:

            st.metric(
                "Available Time",
                f"{available_hours:.1f} h",
            )

        with c3:

            st.metric(
                "Maximum Allowed",
                f"{max_daily_hours:.1f} h",
            )

    else:

        st.warning(
            "No study day is available."
        )

    st.divider()

    if not course_list:

        st.info(
            "No courses available."
        )

    elif available_hours <= 0:

        st.warning(
            "There are no available study hours "
            "for this day."
        )

    elif max_daily_hours <= 0:

        st.warning(
            "Maximum study hours must be greater "
            "than zero."
        )

    else:

        if st.button(
            "Generate Optimized Plan",
            type="primary",
            width="stretch",
            key="generate_plan_button",
        ):

            st.session_state.plan_generated = True

            st.rerun()

        # =====================================================
        # GENERATE PLAN
        # =====================================================

        if st.session_state.plan_generated:

            st.success(
                "Study plan generated successfully!"
            )

            # ---------------------------------------------
            # Calculate total available study time
            # ---------------------------------------------

            total_hours = min(
                float(available_hours),
                float(max_daily_hours),
            )

# ---------------------------------------------
# Optimize Self-Study Plan
# ---------------------------------------------

            from dataclass.optimizer import StudyOptimizer

            study_plan = StudyOptimizer.allocate_study_time(
                available_hours=total_hours,
                courses=course_list,
            )

            # ---------------------------------------------
            # Display Study Plan
            # ---------------------------------------------

            if study_plan:

                for course_name, details in study_plan.items():

                    difficulty = safe_int(
                        details.get(
                            "difficulty",
                            0,
                        ),
                        0,
                    )

                    recommended_time = safe_float(
                        details.get(
                            "allocated_hours",
                            0.0,
                        ),
                        0.0,
                    )

                    with st.container(border=True):

                        st.subheader(
                            course_name
                        )

                        col1, col2 = st.columns(
                            2,
                            gap="medium",
                        )

                        with col1:

                            st.metric(
                                "Difficulty",
                                f"{difficulty}/5",
                            )

                        with col2:

                            st.metric(
                                "Recommended Time",
                                f"{recommended_time:.2f} h",
                            )

            else:

                st.info(
                    "No study recommendations "
                    "could be generated."
                )

# =========================================================
# TAB 3 — TIMER
# =========================================================

with tab3:

    st.header(
        "Study Timer"
    )

    st.write(
        "Stay focused and track your study session."
    )

    st.divider()


    active_template = get_active_template()


    # -----------------------------------------------------
    # Safety fallback
    # -----------------------------------------------------

    if not isinstance(
        active_template,
        dict,
    ):

        active_template = STUDY_TEMPLATES.get(
            "pomodoro",
            {
                "name": "Pomodoro",
                "study_minutes": 25,
                "break_minutes": 5,
            },
        )


    active_template_name = active_template.get(
        "name",
        "Pomodoro",
    )

    active_study_minutes = safe_int(
        active_template.get(
            "study_minutes",
            25,
        ),
        25,
    )

    active_break_minutes = safe_int(
        active_template.get(
            "break_minutes",
            5,
        ),
        5,
    )


    col1, col2, col3 = st.columns(
        3,
        gap="medium",
    )


    with col1:

        st.metric(
            "Active Template",
            active_template_name,
        )


    with col2:

        st.metric(
            "Study Session",
            f"{active_study_minutes} min",
        )


    with col3:

        st.metric(
            "Break",
            f"{active_break_minutes} min",
        )


    st.divider()


    render_timer(
        available_hours=float(
            available_hours
        ),
        study_template=active_template,
    )


# =========================================================
# TAB 4 — REWARD SHOP
# =========================================================

with tab4:

    st.header(
        "Reward Shop"
    )

    st.metric(
        "Your Available Points",
        safe_int(
            st.session_state.get(
                "points",
                0,
            )
        ),
    )

    st.divider()


    # =====================================================
    # THEMES
    # =====================================================

    st.subheader(
        "Themes"
    )


    if THEMES:

        theme_count = max(
            1,
            min(
                len(THEMES),
                4,
            ),
        )


        theme_columns = st.columns(
            theme_count,
            gap="medium",
        )


        for index, (
            key,
            item,
        ) in enumerate(
            THEMES.items()
        ):

            with theme_columns[
                index % theme_count
            ]:

                st.markdown(
                    f"### {item['name']}"
                )

                st.write(
                    f"Cost: **{item['price']} Points**"
                )


                # -------------------------------------------------
                # UNLOCKED
                # -------------------------------------------------

                if key in st.session_state.unlocked_themes:

                    if (
                        st.session_state.active_theme
                        == key
                    ):

                        st.success(
                            "Active"
                        )

                    else:

                        if st.button(
                            "Use Theme",
                            key=f"use_theme_{key}",
                            width="stretch",
                        ):

                            if activate_theme(key):

                                st.rerun()


                # -------------------------------------------------
                # LOCKED
                # -------------------------------------------------

                else:

                    if st.button(
                        "Buy Theme",
                        key=f"buy_theme_{key}",
                        width="stretch",
                    ):

                        price = safe_int(
                            item.get(
                                "price",
                                0,
                            ),
                            0,
                        )


                        if buy_item(
                            "theme",
                            key,
                            price,
                        ):

                            st.success(
                                "Theme unlocked!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Not enough points."
                            )


    # =====================================================
    # BANNERS
    # =====================================================

    st.divider()

    st.subheader(
        "Banners"
    )


    if BANNERS:

        banner_count = max(
            1,
            min(
                len(BANNERS),
                3,
            ),
        )


        banner_columns = st.columns(
            banner_count,
            gap="medium",
        )


        for index, (
            key,
            item,
        ) in enumerate(
            BANNERS.items()
        ):

            with banner_columns[
                index % banner_count
            ]:

                try:

                    st.image(
                        item["url"],
                        width="stretch",
                    )

                except Exception:

                    st.warning(
                        "Unable to load banner preview."
                    )


                st.markdown(
                    f"### {item['name']}"
                )


                st.write(
                    f"Cost: **{item['price']} Points**"
                )


                # -------------------------------------------------
                # UNLOCKED
                # -------------------------------------------------

                if key in st.session_state.unlocked_banners:

                    if (
                        st.session_state.active_banner
                        == key
                    ):

                        st.success(
                            "Active"
                        )

                    else:

                        if st.button(
                            "Use Banner",
                            key=f"use_banner_{key}",
                            width="stretch",
                        ):

                            if activate_banner(key):

                                st.rerun()


                # -------------------------------------------------
                # LOCKED
                # -------------------------------------------------

                else:

                    if st.button(
                        "Buy Banner",
                        key=f"buy_banner_{key}",
                        width="stretch",
                    ):

                        price = safe_int(
                            item.get(
                                "price",
                                0,
                            ),
                            0,
                        )


                        if buy_item(
                            "banner",
                            key,
                            price,
                        ):

                            st.success(
                                "Banner unlocked!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Not enough points."
                            )


    # =====================================================
    # STUDY TEMPLATES
    # =====================================================

    st.divider()

    st.subheader(
        "Study Templates"
    )


    if STUDY_TEMPLATES:

        template_count = max(
            1,
            min(
                len(STUDY_TEMPLATES),
                3,
            ),
        )


        template_columns = st.columns(
            template_count,
            gap="medium",
        )


        for index, (
            key,
            item,
        ) in enumerate(
            STUDY_TEMPLATES.items()
        ):

            with template_columns[
                index % template_count
            ]:

                st.markdown(
                    f"### {item['name']}"
                )


                st.caption(
                    item.get(
                        "desc",
                        "",
                    )
                )


                st.write(
                    f"Cost: **{item['price']} Points**"
                )


                # -------------------------------------------------
                # UNLOCKED
                # -------------------------------------------------

                if key in st.session_state.unlocked_templates:

                    if (
                        st.session_state.active_template
                        == key
                    ):

                        st.success(
                            "Active"
                        )

                    else:

                        if st.button(
                            "Use Template",
                            key=f"use_template_{key}",
                            width="stretch",
                        ):

                            if activate_template(key):

                                st.rerun()


                # -------------------------------------------------
                # LOCKED
                # -------------------------------------------------

                else:

                    if st.button(
                        "Buy Template",
                        key=f"buy_template_{key}",
                        width="stretch",
                    ):

                        price = safe_int(
                            item.get(
                                "price",
                                0,
                            ),
                            0,
                        )


                        if buy_item(
                            "template",
                            key,
                            price,
                        ):

                            st.success(
                                "Template unlocked!"
                            )

                            st.rerun()

                        else:

                            st.error(
                                "Not enough points."
                            )


# =========================================================
# PERSIST PROGRESS
# =========================================================
#
# Points can change during this run (finishing a study session,
# buying a shop item). Whenever that happens, write the new total
# back to the student's account so it survives logging out and
# logging back in.

_current_points = safe_int(
    st.session_state.get("points", 0),
    0,
)

if _current_points != safe_int(student.get("points", 0), 0):

    try:
        update_points(student["student_id"], _current_points)
        st.session_state.auth_student["points"] = _current_points

    except Exception:
        # Don't let a DB hiccup break the dashboard — points still
        # live correctly in this session either way.
        pass


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Intelligent Study Planner | "
    "Planning • Studying • Tracking"
)