import streamlit as st
from auth import authenticate_user, register_user
from dashboard import render_dashboard
from database import init_db, seed_questions
from leaderboard import record_quiz_result, render_leaderboard
from pdf_generator import generate_quiz_pdf
from quiz_data import (
    evaluate_quiz,
    get_available_categories,
    get_available_difficulties,
    load_quiz_questions,
)
from utils import (
    format_time_display,
    get_remaining_seconds,
    init_session_state,
    reset_quiz_session,
    start_quiz_timer,
)

st.set_page_config(
    page_title="Online Quiz Platform", page_icon="🎯", layout="wide"
)

# Initialize database, seed questions, set up session states
init_db()
seed_questions()
init_session_state()

if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

# --- SIDEBAR (LOGOUT ONLY) ---
st.sidebar.title("🎯 Quiz Platform")
if st.session_state.authenticated:
    st.sidebar.success(f"Logged in: **{st.session_state.user_data['username']}**")
    if st.sidebar.button("Logout 🚪", key="logout_btn"):
        st.session_state.authenticated = False
        st.session_state.current_page = "Dashboard"
        reset_quiz_session()
        st.rerun()

# --- 1. AUTHENTICATION ---
if not st.session_state.authenticated:
    st.title("Welcome to Online Quiz Platform 🧠")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        u = st.text_input("User/Email", key="login_user")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Sign In", type="primary", key="login_btn"):
            ok, res = authenticate_user(u, p)
            if ok:
                st.session_state.authenticated = True
                st.session_state.user_data = res
                st.session_state.current_page = "Dashboard"
                st.rerun()
            else:
                st.error(res)
                
    with tab2:
        u = st.text_input("Username", key="reg_user")
        e = st.text_input("Email", key="reg_email")
        p1 = st.text_input("Password", type="password", key="reg_pass1")
        p2 = st.text_input("Confirm Password", type="password", key="reg_pass2")
        if st.button("Register", key="reg_btn"):
            ok, msg = register_user(u, e, p1, p2)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

# --- 2. DASHBOARD SCREEN ---
elif st.session_state.current_page == "Dashboard":
    render_dashboard(
        st.session_state.user_data["id"],
        st.session_state.user_data["username"],
    )
    st.markdown("---")
    if st.button("Proceed to Take Quiz ➡️", type="primary", use_container_width=True, key="goto_quiz_btn"):
        st.session_state.current_page = "Take Quiz"
        st.rerun()

# --- 3. QUIZ ENGINE SCREEN ---
elif st.session_state.current_page == "Take Quiz":
    st.header("📝 Take a Quiz")
    
    # Configuration Step
    if not st.session_state.current_quiz and not st.session_state.quiz_completed:
        c1, c2 = st.columns(2)
        cat = c1.selectbox("Category", get_available_categories(), key="cat_sel")
        diff = c2.selectbox("Difficulty", get_available_difficulties(), key="diff_sel")
        c3, c4 = st.columns(2)
        num_q = c3.slider("Questions", 1, 10, 5, key="num_q")
        dur = c4.number_input("Time (Mins)", 1, 30, 5, key="dur")

        if st.button("🚀 Start Quiz", type="primary", key="start_quiz_btn"):
            qs = load_quiz_questions(cat, diff, num_q)
            if qs:
                st.session_state.current_quiz = {"category": cat, "questions": qs}
                st.session_state.current_question_index = 0
                st.session_state.user_answers = {}
                start_quiz_timer(dur)
                st.rerun()
            else:
                st.error("No questions found for the selected configuration.")

    # Active Test Interface (Wrapped in a fragment running every 1 second for live ticking)
    elif st.session_state.current_quiz and not st.session_state.quiz_completed:
        
        @st.fragment(run_every=1.0)
        def render_active_quiz():
            qs = st.session_state.current_quiz["questions"]
            idx = st.session_state.current_question_index
            rem_sec = get_remaining_seconds()

            if rem_sec <= 0:
                st.warning("⏱️ Time's up! Submitting your quiz automatically.")
                st.session_state.quiz_completed = True
                st.rerun()

            c1, c2 = st.columns([3, 1])
            c1.progress((idx + 1) / len(qs))
            c1.caption(f"Question {idx + 1} of {len(qs)}")
            c2.markdown(f"⏱️ **Time:** `{format_time_display(rem_sec)}`")

            st.markdown(f"### Q{idx + 1}. {qs[idx]['question']}")
            
            current_options = qs[idx]["options"]
            prev_answer = st.session_state.user_answers.get(idx, None)
            default_ix = current_options.index(prev_answer) if prev_answer in current_options else None

            ans = st.radio("Choose option:", current_options, key=f"q_radio_{idx}", index=default_ix)
            if ans:
                st.session_state.user_answers[idx] = ans

            b1, b2, b3 = st.columns(3)
            if idx > 0 and b1.button("⬅️ Prev", key="prev_q_btn"):
                st.session_state.current_question_index -= 1
                st.rerun()
            if idx < len(qs) - 1 and b2.button("Next ➡️", key="next_q_btn"):
                st.session_state.current_question_index += 1
                st.rerun()
            if b3.button("✅ Submit Quiz", type="primary", key="submit_quiz_btn"):
                st.session_state.quiz_completed = True
                st.rerun()

        render_active_quiz()

    # Results Breakdown
    elif st.session_state.quiz_completed:
        st.balloons()
        st.success("🎉 Quiz Completed!")
        quiz = st.session_state.current_quiz
        qs = quiz["questions"] if quiz else st.session_state.quiz_results.get("questions", [])
        cat = quiz["category"] if quiz else "General"

        if not st.session_state.quiz_results:
            score, total, pct, details = evaluate_quiz(qs, st.session_state.user_answers)
            st.session_state.quiz_results = {
                "score": score, "total": total, "percentage": pct, "details": details, "category": cat
            }
            record_quiz_result(st.session_state.user_data["id"], cat, score, total, pct)

        res = st.session_state.quiz_results
        r1, r2, r3 = st.columns(3)
        r1.metric("Score", f"{res['score']} / {res['total']}")
        r2.metric("Percentage", f"{res['percentage']:.1f}%")
        r3.metric("Status", "PASSED 🏆" if res["percentage"] >= 50 else "RETRY 💡")

        st.markdown("---")
        st.subheader("📋 Detailed Results Breakdown")

        for i, d in enumerate(res["details"], 1):
            with st.container():
                st.markdown(f"### Q{i}: {d['question']}")
                
                options_list = d.get("options", [])
                for opt in options_list:
                    if opt == d["correct_answer"] and opt == d["selected_answer"]:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;✅ **{opt}** &nbsp; *— Your answer (Correct)*")
                    elif opt == d["correct_answer"]:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;✅ **{opt}** &nbsp; *— Correct Answer*")
                    elif opt == d["selected_answer"]:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;❌ ~~{opt}~~ &nbsp; *— Your answer (Incorrect)*")
                    else:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;⚪ {opt}")

                if d["selected_answer"] == "Not Answered":
                    st.warning("⚠️ You did not answer this question.")
                
                st.markdown("---")

        col_pdf, col_next = st.columns(2)
        
        pdf = generate_quiz_pdf(
            st.session_state.user_data["username"], res["category"], res["score"],
            res["total"], res["percentage"], res["details"]
        )
        
        with col_pdf:
            st.download_button(
                "📄 Download Result PDF",
                pdf,
                f"{st.session_state.user_data['username']}_result.pdf",
                "application/pdf",
                key="dl_pdf_btn"
            )
            
        with col_next:
            if st.button("Proceed to Leaderboard 🏆", type="primary", use_container_width=True, key="goto_leaderboard_btn"):
                reset_quiz_session()
                st.session_state.current_page = "Leaderboard"
                st.rerun()

# --- 4. LEADERBOARD SCREEN ---
elif st.session_state.current_page == "Leaderboard":
    render_leaderboard()
    st.markdown("---")
    if st.button("⬅️ Back to Dashboard", use_container_width=True, key="back_to_dash_btn"):
        st.session_state.current_page = "Dashboard"
        st.rerun()