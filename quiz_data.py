from database import fetch_questions

def get_available_categories():
    """Returns list of supported quiz categories including 'All'."""
    return ["All", "Python", "Science", "History"]

def get_available_difficulties():
    """Returns supported difficulty levels including 'All'."""
    return ["All", "Easy", "Medium", "Hard"]

def load_quiz_questions(category="All", difficulty="All", limit=5):
    """Retrieves quiz questions filtered by selected criteria from the database."""
    return fetch_questions(category=category, difficulty=difficulty, limit=limit)

def evaluate_quiz(questions, user_answers):
    """
    Evaluates user submissions against correct answers.
    Returns (score, total, percentage, details_list).
    """
    score = 0
    total = len(questions)
    details = []

    for i, q in enumerate(questions):
        selected = user_answers.get(i, "Not Answered")
        correct = q["correct"]
        is_correct = (selected == correct)

        if is_correct:
            score += 1

        details.append({
            "question": q["question"],
            "options": q.get("options", []),
            "selected_answer": selected,
            "correct_answer": correct,
            "is_correct": is_correct
        })

    percentage = (score / total) * 100 if total > 0 else 0.0
    return score, total, percentage, details