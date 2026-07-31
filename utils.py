import time
import streamlit as st

def init_session_state():
    """Initializes default session states if they don't exist."""
    defaults = {
        "authenticated": False,
        "user_data": None,
        "current_page": "Dashboard",
        "current_quiz": None,
        "current_question_index": 0,
        "user_answers": {},
        "quiz_completed": False,
        "quiz_results": {},
        "quiz_start_time": None,
        "time_limit_seconds": 0
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def start_quiz_timer(minutes):
    """Starts the timer by storing the start time and duration in seconds."""
    st.session_state["quiz_start_time"] = time.time()
    st.session_state["time_limit_seconds"] = minutes * 60

def get_remaining_seconds():
    """Calculates remaining seconds based on system clock elapsed time."""
    if not st.session_state.get("quiz_start_time"):
        return 0
    elapsed = time.time() - st.session_state["quiz_start_time"]
    remaining = int(st.session_state["time_limit_seconds"] - elapsed)
    return max(0, remaining)

def format_time_display(seconds):
    """Formats total seconds into MM:SS format string."""
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"

def reset_quiz_session():
    """Resets all active quiz session states when navigating away or finishing."""
    st.session_state["current_quiz"] = None
    st.session_state["current_question_index"] = 0
    st.session_state["user_answers"] = {}
    st.session_state["quiz_completed"] = False
    st.session_state["quiz_results"] = {}
    st.session_state["quiz_start_time"] = None
    st.session_state["time_limit_seconds"] = 0