import streamlit as st
import pandas as pd
from database import save_score, get_leaderboard

def record_quiz_result(user_id, category, score, total_questions, percentage):
    """Saves user's quiz completion details to the database."""
    save_score(user_id, category, score, total_questions, percentage)

def render_leaderboard():
    """Displays global rankings and top performer scores."""
    st.title("🏆 Global Leaderboard")
    st.caption("Top quiz scores across all categories and users")

    leaderboard_data = get_leaderboard(limit=10)

    if leaderboard_data:
        df = pd.DataFrame(
            leaderboard_data,
            columns=["Username", "Category", "Score", "Total", "Percentage (%)", "Completed At"]
        )

        ranks = []
        for i in range(len(df)):
            if i == 0:
                ranks.append("🥇 1st")
            elif i == 1:
                ranks.append("🥈 2nd")
            elif i == 2:
                ranks.append("🥉 3rd")
            else:
                ranks.append(f"{i + 1}th")
                
        df.insert(0, "Rank", ranks)
        df["Percentage (%)"] = df["Percentage (%)"].apply(lambda x: f"{x:.1f}%")

        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No scores recorded on the leaderboard yet. Be the first to play!")