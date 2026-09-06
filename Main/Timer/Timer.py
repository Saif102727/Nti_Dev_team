import streamlit as st
import time


def init_timer_state():
    if "timer_running" not in st.session_state:
        st.session_state.timer_running = False
    if "timer_paused" not in st.session_state:
        st.session_state.timer_paused = False
    if "timer_seconds" not in st.session_state:
        st.session_state.timer_seconds = 25 * 60
    if "timer_total_seconds" not in st.session_state:
        st.session_state.timer_total_seconds = 25 * 60
    if "completed_sessions" not in st.session_state:
        st.session_state.completed_sessions = []


def render_timer(available_hours=2.0):
    init_timer_state()

    st.header("⏱️ Study Timer & Focus Tracker")

    if not st.session_state.courses:
        st.info("No courses available to track. Please load your courses first.")
        return

    # Configuration section
    col1, col2, col3 = st.columns(3)

    with col1:
        course_names = [course.name for course in st.session_state.courses]
        selected_course = st.selectbox(
            "Choose Course",
            course_names,
            key="timer_course_select"
        )

    with col2:
        timer_mode = st.selectbox(
            "Session Type",
            ["Pomodoro (25 min)", "Short Break (5 min)", "Long Break (15 min)", "Custom Duration"],
            key="timer_mode_select"
        )

    with col3:
        if timer_mode == "Custom Duration":
            custom_mins = st.number_input(
                "Duration (minutes)",
                min_value=1,
                max_value=300,
                value=int(min(float(available_hours), 2.0) * 60),
                step=5,
                key="timer_custom_mins"
            )
            target_seconds = custom_mins * 60
        elif timer_mode == "Pomodoro (25 min)":
            target_seconds = 25 * 60
        elif timer_mode == "Short Break (5 min)":
            target_seconds = 5 * 60
        else:
            target_seconds = 15 * 60

    if not st.session_state.timer_running and not st.session_state.timer_paused:
        st.session_state.timer_seconds = target_seconds
        st.session_state.timer_total_seconds = target_seconds

    # Timer Display
    mins, secs = divmod(st.session_state.timer_seconds, 60)
    time_format = f"{mins:02d}:{secs:02d}"

    st.divider()

    c_left, c_center, c_right = st.columns([1, 2, 1])

    with c_center:
        st.markdown(
            f"""
            <div style="text-align: center; background-color: #1e1e2e; padding: 25px; border-radius: 15px; border: 2px solid #4CAF50;">
                <h1 style="font-size: 72px; margin: 0; color: #ffffff; font-family: monospace;">{time_format}</h1>
                <p style="font-size: 18px; color: #a6adc8; margin-top: 10px;">Subject: <b>{selected_course}</b></p>
            </div>
            """,
            unsafe_allow_html=True
        )

        progress = 0.0
        if st.session_state.timer_total_seconds > 0:
            elapsed = st.session_state.timer_total_seconds - st.session_state.timer_seconds
            progress = min(1.0, max(0.0, elapsed / st.session_state.timer_total_seconds))

        st.progress(progress)

    st.write("")

    # Control Buttons
    b1, b2, b3, b4 = st.columns(4)

    with b1:
        if not st.session_state.timer_running:
            if st.button("▶️ Start", use_container_width=True, type="primary"):
                st.session_state.timer_running = True
                st.session_state.timer_paused = False
                st.rerun()

    with b2:
        if st.session_state.timer_running:
            if st.button("⏸️ Pause", use_container_width=True):
                st.session_state.timer_running = False
                st.session_state.timer_paused = True
                st.rerun()

    with b3:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.timer_running = False
            st.session_state.timer_paused = False
            st.session_state.timer_seconds = target_seconds
            st.session_state.timer_total_seconds = target_seconds
            st.rerun()

    with b4:
        if st.button("✅ Finish Session", use_container_width=True):
            _complete_session(selected_course)

    # Countdown Loop Execution
    if st.session_state.timer_running:
        time.sleep(1)
        if st.session_state.timer_seconds > 0:
            st.session_state.timer_seconds -= 1
            st.rerun()
        else:
            st.session_state.timer_running = False
            st.balloons()
            st.success("🎉 Time's up! Great study session!")
            _complete_session(selected_course)

    st.divider()

    # Log History
    st.subheader("📜 Session History")
    if st.session_state.completed_sessions:
        for session in reversed(st.session_state.completed_sessions):
            st.write(
                f"• **{session['course']}** | "
                f"Duration: {session['duration_mins']} mins | "
                f"Earned: +{session['points']} Points"
            )
    else:
        st.info("No study sessions completed yet.")


def _complete_session(course_name):
    elapsed_seconds = st.session_state.timer_total_seconds - st.session_state.timer_seconds
    if elapsed_seconds <= 0:
        elapsed_seconds = st.session_state.timer_total_seconds

    duration_hours = elapsed_seconds / 3600.0
    duration_mins = max(1, int(elapsed_seconds / 60))

    earned_points = max(5, int(duration_mins * 0.75))

    st.session_state.study_time += duration_hours
    st.session_state.points += earned_points

    st.session_state.completed_sessions.append({
        "course": course_name,
        "duration_mins": duration_mins,
        "points": earned_points
    })

    st.session_state.timer_running = False
    st.session_state.timer_paused = False
    st.session_state.timer_seconds = st.session_state.timer_total_seconds

    st.success(f"Added {duration_mins} mins to study time and earned +{earned_points} points!")
    st.rerun()