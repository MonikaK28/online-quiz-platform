# 🎯 Online Quiz Platform

A full-stack Python web application for conducting online quizzes, featuring real-time timers, user authentication, interactive dashboards, global leaderboards, and PDF result exports.

---

## 🚀 Features

* **🔐 Authentication:** User registration and login with secure session tracking.
* **📝 Dynamic Quiz Engine:** Questions filtered by category (Python, Science, History) and difficulty (Easy, Medium, Hard).
* **⏱️ Real-time Timer:** Live countdown timer with automatic quiz submission when time expires.
* **📊 Analytics Dashboard:** Personal performance metrics, score averages, personal bests, and full attempt history.
* **🏆 Global Leaderboard:** Top player rankings across all categories with rank badges.
* **📄 PDF Export:** Downloadable PDF performance reports with question-by-question breakdowns.

---

## 🛠️ Tech Stack

* **Language:** Python 3.8+
* **Frontend / UI:** Streamlit
* **Database:** SQLite3 (`sqlite3`)
* **Data Handling:** Pandas
* **PDF Generation:** FPDF2 (`fpdf2`)

---

## 📁 Project Structure

* `app.py` - Main application file and user interface navigation.
* `auth.py` - Handles user registration and login verification.
* `database.py` - Manages SQLite database connection, tables, and question seed data.
* `quiz_data.py` - Fetches quiz questions and evaluates user answers.
* `dashboard.py` - Displays user analytics and previous quiz results.
* `leaderboard.py` - Displays global player rankings.
* `pdf_generator.py` - Creates downloadable PDF result reports.
* `utils.py` - Handles session states, timers, and helper functions.
* `assets/` - Contains UI screenshots for documentation.

---
## 📸 Screenshots

Here is a visual walkthrough of the platform showcasing the user journey:

### 1. User Dashboard
*Displays personal analytics, metrics, and past quiz attempts history.*
![Dashboard](assets/dashboard.png)

### 2. Active Timed Quiz Interface
*Features clean options layouts, progress tracking, and a live ticking countdown timer.*
![Active Quiz](assets/quiz.png)

### 3. Detailed Results & Inline Evaluation
*Provides instant grading, performance badges, and itemized answer reviews with checkmarks and crosses.*
![Results](assets/results.png)

### 4. Global Leaderboard
*Ranks top-performing users across categories with timestamps.*
![Leaderboard](assets/leaderboard.png)

## 🏃 Setup & Local Execution

1. **Clone or download the project files into a single folder.**

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
