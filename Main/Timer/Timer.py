import time
from typing import Optional

import streamlit as st


# =========================================================
# TIMER STATE
# =========================================================

def init_timer_state():
    defaults = {
        "timer_running": False,
        "timer_paused": False,
        "timer_seconds": 25 * 60,
        "timer_total_seconds": 25 * 60,
        "timer_last_tick": None,
        "timer_course": None,
        "timer_mode": "Pomodoro (25 min)",
        "completed_sessions": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =========================================================
# HTML HELPER
# =========================================================

def render_html(html: str):
    """
    Render HTML using Streamlit's native HTML renderer.
    Falls back to markdown for older Streamlit versions.
    """

    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(
            html,
            unsafe_allow_html=True,
        )


# =========================================================
# RESET TIMER
# =========================================================

def reset_timer(seconds: int):
    seconds = max(1, int(seconds))

    st.session_state.timer_running = False
    st.session_state.timer_paused = False
    st.session_state.timer_seconds = seconds
    st.session_state.timer_total_seconds = seconds
    st.session_state.timer_last_tick = None


# =========================================================
# START TIMER
# =========================================================

def start_timer(
    course_name: str,
    seconds: int,
):
    seconds = max(1, int(seconds))

    # Start a new session if needed
    if (
        st.session_state.timer_seconds <= 0
        or st.session_state.timer_course != course_name
        or (
            not st.session_state.timer_running
            and not st.session_state.timer_paused
            and st.session_state.timer_total_seconds != seconds
        )
    ):
        st.session_state.timer_seconds = seconds
        st.session_state.timer_total_seconds = seconds

    st.session_state.timer_course = course_name
    st.session_state.timer_running = True
    st.session_state.timer_paused = False
    st.session_state.timer_last_tick = time.monotonic()


# =========================================================
# PAUSE
# =========================================================

def pause_timer():
    st.session_state.timer_running = False
    st.session_state.timer_paused = True
    st.session_state.timer_last_tick = None


# =========================================================
# COMPLETE SESSION
# =========================================================

def _complete_session(
    course_name: str,
    completed_by_user: bool = False,
):
    total_seconds = int(
        st.session_state.timer_total_seconds
    )

    remaining_seconds = int(
        st.session_state.timer_seconds
    )

    elapsed_seconds = (
        total_seconds - remaining_seconds
    )

    # Manual Finish
    if completed_by_user:
        elapsed_seconds = max(
            60,
            elapsed_seconds,
        )

    # Automatic completion
    else:
        elapsed_seconds = total_seconds

    elapsed_seconds = min(
        elapsed_seconds,
        total_seconds,
    )

    duration_mins = max(
        1,
        int(elapsed_seconds / 60),
    )

    duration_hours = (
        elapsed_seconds / 3600.0
    )

    earned_points = max(
        5,
        int(duration_mins * 0.75),
    )

    # Update global progress
    st.session_state.study_time += duration_hours
    st.session_state.points += earned_points

    # Save session
    st.session_state.completed_sessions.append(
        {
            "course": course_name,
            "duration_mins": duration_mins,
            "points": earned_points,
            "timestamp": time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }
    )

    # Reset timer
    reset_timer(total_seconds)

    return duration_mins, earned_points


# =========================================================
# TIMER
# =========================================================

def render_timer(
    available_hours: float = 2.0,
    study_template: Optional[dict] = None,
):
    init_timer_state()

    st.header(
        "⏱️ Study Timer & Focus Tracker"
    )

    courses = st.session_state.get(
        "courses",
        [],
    )

    if not courses:
        st.info(
            "No courses available to track."
        )
        return

    # =====================================================
    # COURSE
    # =====================================================

    course_names = [
        course.name
        for course in courses
    ]

    selected_course = st.selectbox(
        "Choose Course",
        course_names,
        key="timer_course_select",
    )

    # =====================================================
    # TEMPLATE
    # =====================================================

    template = study_template or {
        "name": "⏱️ Pomodoro (25/5)",
        "study_minutes": 25,
        "break_minutes": 5,
    }

    study_minutes = max(
        1,
        int(
            template.get(
                "study_minutes",
                25,
            )
        ),
    )

    break_minutes = max(
        0,
        int(
            template.get(
                "break_minutes",
                5,
            )
        ),
    )

    st.info(
        f"Active template: **{template.get('name', 'Study Template')}**"
    )

    # =====================================================
    # TIMER MODE
    # =====================================================

    timer_mode = st.selectbox(
        "Session Type",
        [
            f"Study ({study_minutes} min)",
            f"Short Break ({break_minutes} min)",
            "Custom Duration",
        ],
        key="timer_mode_select",
    )

    # =====================================================
    # TARGET DURATION
    # =====================================================

    if timer_mode == "Custom Duration":

        max_minutes = max(
            1,
            min(
                300,
                int(
                    max(
                        1.0,
                        float(available_hours),
                    )
                    * 60
                ),
            ),
        )

        custom_mins = st.number_input(
            "Duration (minutes)",
            min_value=1,
            max_value=max_minutes,
            value=min(
                study_minutes,
                max_minutes,
            ),
            step=5,
            key="timer_custom_mins",
        )

        target_seconds = int(
            custom_mins * 60
        )

    elif timer_mode.startswith("Study"):

        target_seconds = (
            study_minutes * 60
        )

    else:

        target_seconds = (
            break_minutes * 60
        )

        if target_seconds <= 0:
            target_seconds = 60

    # =====================================================
    # INITIALIZE NEW TIMER
    # =====================================================

    if (
        not st.session_state.timer_running
        and not st.session_state.timer_paused
    ):

        if (
            st.session_state.timer_total_seconds
            != target_seconds
            or st.session_state.timer_course
            != selected_course
        ):

            reset_timer(
                target_seconds
            )

        st.session_state.timer_course = (
            selected_course
        )

    # =====================================================
    # TIMER DISPLAY
    # =====================================================

    remaining = max(
        0,
        int(
            st.session_state.timer_seconds
        ),
    )

    mins, secs = divmod(
        remaining,
        60,
    )

    time_format = (
        f"{mins:02d}:{secs:02d}"
    )

    timer_html = f"""
    <div class="timer-card">

        <div
            style="
                font-size: clamp(48px, 8vw, 88px);
                font-weight: 800;
                font-family: monospace;
                line-height: 1;
                color: #ffffff;
            "
        >
            {time_format}
        </div>

        <div
            style="
                margin-top: 12px;
                opacity: 0.8;
                font-size: 16px;
                color: #ffffff;
            "
        >
            📚 {selected_course}
        </div>

    </div>
    """

    render_html(timer_html)

    # =====================================================
    # PROGRESS
    # =====================================================

    total = max(
        1,
        int(
            st.session_state.timer_total_seconds
        ),
    )

    elapsed = total - remaining

    progress = min(
        1.0,
        max(
            0.0,
            elapsed / total,
        ),
    )

    st.progress(progress)

    # =====================================================
    # CONTROLS
    # =====================================================

    b1, b2, b3, b4 = st.columns(4)

    # -----------------------------------------------------
    # START
    # -----------------------------------------------------

    with b1:

        if not st.session_state.timer_running:

            if st.button(
                "▶️ Start",
                use_container_width=True,
                type="primary",
            ):

                start_timer(
                    selected_course,
                    target_seconds,
                )

                st.rerun()

    # -----------------------------------------------------
    # PAUSE / RESUME
    # -----------------------------------------------------

    with b2:

        if st.session_state.timer_running:

            if st.button(
                "⏸️ Pause",
                use_container_width=True,
            ):

                pause_timer()

                st.rerun()

        elif st.session_state.timer_paused:

            if st.button(
                "▶️ Resume",
                use_container_width=True,
            ):

                st.session_state.timer_running = True

                st.session_state.timer_paused = False

                st.session_state.timer_last_tick = (
                    time.monotonic()
                )

                st.rerun()

    # -----------------------------------------------------
    # RESET
    # -----------------------------------------------------

    with b3:

        if st.button(
            "🔄 Reset",
            use_container_width=True,
        ):

            reset_timer(
                target_seconds
            )

            st.rerun()

    # -----------------------------------------------------
    # FINISH
    # -----------------------------------------------------

    with b4:

        if st.button(
            "✅ Finish",
            use_container_width=True,
        ):

            # Update elapsed time before completing
            if st.session_state.timer_running:

                now = time.monotonic()

                last_tick = (
                    st.session_state.timer_last_tick
                    or now
                )

                elapsed_tick = int(
                    now - last_tick
                )

                st.session_state.timer_seconds = max(
                    0,
                    st.session_state.timer_seconds
                    - elapsed_tick,
                )

            duration, points = _complete_session(
                selected_course,
                completed_by_user=True,
            )

            st.success(
                f"Session completed: "
                f"{duration} min • "
                f"+{points} points"
            )

            st.rerun()

    # =====================================================
    # COUNTDOWN
    # =====================================================

    if st.session_state.timer_running:

        now = time.monotonic()

        last_tick = (
            st.session_state.timer_last_tick
            or now
        )

        elapsed_tick = int(
            now - last_tick
        )

        if elapsed_tick >= 1:

            st.session_state.timer_seconds = max(
                0,
                st.session_state.timer_seconds
                - elapsed_tick,
            )

            st.session_state.timer_last_tick = now

        # -------------------------------------------------
        # TIME'S UP
        # -------------------------------------------------

        if st.session_state.timer_seconds <= 0:

            duration, points = _complete_session(
                selected_course,
                completed_by_user=False,
            )

            st.balloons()

            st.success(
                f"🎉 Time's up! "
                f"{duration} minutes completed. "
                f"+{points} points!"
            )

            st.rerun()

        # -------------------------------------------------
        # REFRESH
        # -------------------------------------------------

        time.sleep(1)

        st.rerun()

    # =====================================================
    # HISTORY
    # =====================================================

    st.divider()

    st.subheader(
        "📜 Session History"
    )

    sessions = st.session_state.get(
        "completed_sessions",
        [],
    )

    if not sessions:

        st.info(
            "No study sessions completed yet."
        )

    else:

        for session in reversed(
            sessions[-20:]
        ):

            st.write(
                f"• **{session['course']}** — "
                f"{session['duration_mins']} min — "
                f"+{session['points']} points"
            )