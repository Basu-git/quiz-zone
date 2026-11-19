-- Optional: run in Supabase SQL Editor. (The app also creates these tables automatically on startup.)
CREATE TABLE IF NOT EXISTS quizzes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',
    difficulty VARCHAR(20) NOT NULL DEFAULT 'Easy',
    total_questions INTEGER NOT NULL DEFAULT 0,
    duration_minutes INTEGER NOT NULL DEFAULT 5,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    option_a VARCHAR(300) NOT NULL,
    option_b VARCHAR(300) NOT NULL,
    option_c VARCHAR(300) NOT NULL,
    option_d VARCHAR(300) NOT NULL,
    correct_answer CHAR(1) NOT NULL CHECK (correct_answer IN ('A','B','C','D')),
    explanation TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_questions_quiz ON questions(quiz_id);

CREATE TABLE IF NOT EXISTS quiz_attempts (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    percentage DOUBLE PRECISION NOT NULL,
    correct_answers INTEGER NOT NULL,
    incorrect_answers INTEGER NOT NULL,
    time_taken INTEGER NOT NULL DEFAULT 0,
    answers_json TEXT DEFAULT '[]',   -- extra column: stores the answer review
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_attempts_quiz ON quiz_attempts(quiz_id);
