import streamlit as st
import pandas as pd
from database import get_user_stats, get_user_history

def render_dashboard(user_id, username):
    """Renders user dashboard with statistics and quiz history."""
    st.title(f"Welcome, {username}! 👋")
    st.subheader("Your Performance Overview")

    stats = get_user_stats(user_id)

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Quizzes Played", stats["total_quizzes"])
    m2.metric("Average Score", f"{stats['avg_score']}%")
    m3.metric("Highest Score", f"{stats['max_score']}%")

    st.markdown("---")
    st.subheader("📜 Recent Quiz History")

    history = get_user_history(user_id)

    if history:
        df = pd.DataFrame(history, columns=["Category", "Score", "Total Questions", "Percentage (%)", "Date & Time"])
        df["Percentage (%)"] = df["Percentage (%)"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("You haven't taken any quizzes yet. Click the button below to get started!")