import json
import sqlite3

DB_NAME = "quiz.db"

def get_connection():
    """Returns a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)

def init_db():
    """Initializes the database and creates necessary tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # 2. Questions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_answer TEXT NOT NULL
        )
    ''')

    # 3. Quiz Results Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

# --- AUTHENTICATION HELPERS ---

def add_user(username, email, password):
    """Inserts a new user into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )
        conn.commit()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        return False, "Username or Email already exists."
    finally:
        conn.close()

def login_user(username, password):
    """Authenticates a user against credentials in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email FROM users WHERE (username = ? OR email = ?) AND password = ?",
        (username, username, password)
    )
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return True, {"id": user[0], "username": user[1], "email": user[2]}
    return False, "Invalid username/email or password."

# --- LEADERBOARD & DASHBOARD HELPERS ---

def save_score(user_id, category, score, total_questions, percentage):
    """Saves quiz results to database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO quiz_results (user_id, category, score, total_questions, percentage)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, category, score, total_questions, percentage))
    conn.commit()
    conn.close()

def get_leaderboard(limit=10):
    """Fetches top scores across all users."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.username, r.category, r.score, r.total_questions, r.percentage, r.timestamp
        FROM quiz_results r
        JOIN users u ON r.user_id = u.id
        ORDER BY r.percentage DESC, r.timestamp DESC
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_user_history(user_id):
    """Fetches quiz history for a specific user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT category, score, total_questions, percentage, timestamp
        FROM quiz_results
        WHERE user_id = ?
        ORDER BY timestamp DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_user_stats(user_id):
    """Fetches total quizzes played, average score, and highest percentage for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            COUNT(*) as total_quizzes,
            AVG(percentage) as avg_score,
            MAX(percentage) as max_score
        FROM quiz_results
        WHERE user_id = ?
    ''', (user_id,))
    stats = cursor.fetchone()
    conn.close()
    return {
        "total_quizzes": stats[0] if stats[0] else 0,
        "avg_score": round(stats[1], 1) if stats[1] else 0.0,
        "max_score": round(stats[2], 1) if stats[2] else 0.0
    }

# --- QUESTION SEEDING & FETCHING ---

def get_questions(category="All", difficulty="All", limit=5):
    """Loads questions dynamically with safe JSON option parsing."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT question, options, correct_answer FROM questions WHERE 1=1"
    params = []
    
    if category != "All":
        query += " AND category = ?"
        params.append(category)
        
    if difficulty != "All":
        query += " AND difficulty = ?"
        params.append(difficulty)
        
    query += " ORDER BY RANDOM() LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    
    questions = []
    for r in rows:
        raw_options = r[1]
        if isinstance(raw_options, str):
            try:
                parsed_options = json.loads(raw_options)
            except:
                parsed_options = eval(raw_options)
        else:
            parsed_options = raw_options

        questions.append({
            "question": r[0],
            "options": parsed_options,
            "correct": r[2]
        })
    return questions

def fetch_questions(category="All", difficulty="All", limit=5):
    """Alias for get_questions to ensure compatibility across modules."""
    return get_questions(category, difficulty, limit)

def seed_questions():
    """Seeds the database with default questions if empty."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM questions")
    count = cursor.fetchone()[0]

    if count == 0:
        question_bank = [
            # --- PYTHON ---
            {"category": "Python", "difficulty": "Easy", "question": "What is the output of print(2 ** 3)?", "options": ["5", "6", "8", "9"], "correct": "8"},
            {"category": "Python", "difficulty": "Easy", "question": "Which keyword is used to define a function in Python?", "options": ["func", "def", "function", "define"], "correct": "def"},
            {"category": "Python", "difficulty": "Easy", "question": "What is the correct file extension for Python files?", "options": [".pt", ".pyt", ".py", ".pyth"], "correct": ".py"},
            {"category": "Python", "difficulty": "Medium", "question": "Which of the following is a mutable data type in Python?", "options": ["Tuple", "String", "List", "Integer"], "correct": "List"},
            {"category": "Python", "difficulty": "Medium", "question": "How do you insert a single-line comment in Python?", "options": ["// comment", "/* comment */", "<!-- comment -->", "# comment"], "correct": "# comment"},
            {"category": "Python", "difficulty": "Medium", "question": "Which method is used to add an element to the end of a list?", "options": ["insert()", "add()", "append()", "extend()"], "correct": "append()"},
            {"category": "Python", "difficulty": "Hard", "question": "Who created the Python programming language?", "options": ["Guido van Rossum", "Dennis Ritchie", "James Gosling", "Bjarne Stroustrup"], "correct": "Guido van Rossum"},
            {"category": "Python", "difficulty": "Hard", "question": "What does the 'len()' function do?", "options": ["Finds the largest number", "Returns the length of an object", "Converts to lowercase", "Loops through an array"], "correct": "Returns the length of an object"},
            {"category": "Python", "difficulty": "Medium", "question": "Which statement is used to stop a loop?", "options": ["stop", "exit", "break", "return"], "correct": "break"},
            {"category": "Python", "difficulty": "Easy", "question": "What is the result of 10 % 3?", "options": ["1", "3", "3.33", "0"], "correct": "1"},

            # --- SCIENCE ---
            {"category": "Science", "difficulty": "Easy", "question": "What is the chemical symbol for water?", "options": ["Wa", "H2O", "O2", "HO"], "correct": "H2O"},
            {"category": "Science", "difficulty": "Easy", "question": "Which planet is known as the Red Planet?", "options": ["Venus", "Jupiter", "Mars", "Saturn"], "correct": "Mars"},
            {"category": "Science", "difficulty": "Medium", "question": "What is the powerhouse of the cell?", "options": ["Nucleus", "Ribosome", "Mitochondria", "Cytoplasm"], "correct": "Mitochondria"},
            {"category": "Science", "difficulty": "Medium", "question": "What gas do plants primarily absorb from the atmosphere?", "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"], "correct": "Carbon Dioxide"},
            {"category": "Science", "difficulty": "Hard", "question": "How many bones are in the adult human body?", "options": ["206", "208", "210", "195"], "correct": "206"},
            {"category": "Science", "difficulty": "Medium", "question": "What is the hardest natural substance on Earth?", "options": ["Gold", "Iron", "Diamond", "Quartz"], "correct": "Diamond"},
            {"category": "Science", "difficulty": "Hard", "question": "Approximately what is the speed of light in a vacuum?", "options": ["300,000 km/s", "150,000 km/s", "1,000,000 km/s", "30,000 km/s"], "correct": "300,000 km/s"},
            {"category": "Science", "difficulty": "Easy", "question": "At what temperature does water boil at sea level in Celsius?", "options": ["50", "90", "100", "120"], "correct": "100"},
            {"category": "Science", "difficulty": "Medium", "question": "Who developed the theory of general relativity?", "options": ["Isaac Newton", "Albert Einstein", "Nikola Tesla", "Galileo Galilei"], "correct": "Albert Einstein"},
            {"category": "Science", "difficulty": "Hard", "question": "Which element has the chemical symbol 'Au'?", "options": ["Silver", "Argon", "Aluminum", "Gold"], "correct": "Gold"},

            # --- HISTORY ---
            {"category": "History", "difficulty": "Easy", "question": "Who was the first President of the United States?", "options": ["Abraham Lincoln", "Thomas Jefferson", "George Washington", "John Adams"], "correct": "George Washington"},
            {"category": "History", "difficulty": "Medium", "question": "In what year did World War II end?", "options": ["1941", "1945", "1950", "1939"], "correct": "1945"},
            {"category": "History", "difficulty": "Easy", "question": "Who built the pyramids?", "options": ["Romans", "Greeks", "Mayans", "Egyptians"], "correct": "Egyptians"},
            {"category": "History", "difficulty": "Medium", "question": "Which ancient empire was ruled by Julius Caesar?", "options": ["Ottoman Empire", "Roman Empire", "Persian Empire", "Mongol Empire"], "correct": "Roman Empire"},
            {"category": "History", "difficulty": "Easy", "question": "Who is credited with discovering America in 1492?", "options": ["Leif Erikson", "Christopher Columbus", "Marco Polo", "Ferdinand Magellan"], "correct": "Christopher Columbus"},
            {"category": "History", "difficulty": "Hard", "question": "The Cold War was primarily a geopolitical tension between the USA and which other nation?", "options": ["China", "Germany", "Soviet Union", "Japan"], "correct": "Soviet Union"},
            {"category": "History", "difficulty": "Medium", "question": "Who was the British Prime Minister during most of World War II?", "options": ["Neville Chamberlain", "Winston Churchill", "Clement Attlee", "Margaret Thatcher"], "correct": "Winston Churchill"},
            {"category": "History", "difficulty": "Hard", "question": "What was the ancient writing system of Egypt called?", "options": ["Cuneiform", "Hieroglyphics", "Sanskrit", "Runes"], "correct": "Hieroglyphics"},
            {"category": "History", "difficulty": "Medium", "question": "In which year did the Titanic sink?", "options": ["1912", "1905", "1920", "1898"], "correct": "1912"},
            {"category": "History", "difficulty": "Hard", "question": "Who was the first human to journey into outer space?", "options": ["Neil Armstrong", "Buzz Aldrin", "Yuri Gagarin", "John Glenn"], "correct": "Yuri Gagarin"}
        ]

        for q in question_bank:
            options_json = json.dumps(q["options"])
            cursor.execute('''
                INSERT INTO questions (category, difficulty, question, options, correct_answer)
                VALUES (?, ?, ?, ?, ?)
            ''', (q["category"], q["difficulty"], q["question"], options_json, q["correct"]))
            
        conn.commit()

    conn.close()