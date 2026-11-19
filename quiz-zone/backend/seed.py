"""Loads 5 quizzes x 5 questions (25 total).
Usage:  python seed.py          (skips if data exists)
        python seed.py --reset  (wipes quizzes/questions/attempts first)
"""
import sys
from database import Base, SessionLocal, engine
import models

QUIZZES = [
    ("Python Programming Basics", "Python Programming", "Test your core Python knowledge: syntax, data types and built-ins.", "Easy", 5, [
        ("Which keyword is used to define a function in Python?", "def", "function", "define", "func", "A", "Functions are defined with the 'def' keyword, e.g. def greet():"),
        ("Which of these data types is immutable?", "list", "dict", "tuple", "set", "C", "Tuples cannot be changed after creation; lists, dicts and sets can."),
        ("What is the output of print(2 ** 3)?", "6", "8", "9", "5", "B", "The ** operator is exponentiation: 2 to the power 3 = 8."),
        ("Which symbol starts a single-line comment in Python?", "//", "#", "/*", "--", "B", "Python uses # for single-line comments."),
        ("Which list method adds an item to the end of a list?", "append()", "add()", "insert_end()", "push()", "A", "list.append(x) adds x to the end of the list."),
    ]),
    ("Artificial Intelligence Essentials", "Artificial Intelligence", "Key ideas behind AI and machine learning.", "Medium", 5, [
        ("Who coined the term 'Artificial Intelligence' in 1956?", "Alan Turing", "John McCarthy", "Geoffrey Hinton", "Marvin Gray", "B", "John McCarthy coined the term for the 1956 Dartmouth workshop."),
        ("Which of the following is a supervised learning algorithm?", "K-Means clustering", "Linear regression", "Apriori", "DBSCAN", "B", "Linear regression learns from labelled data, so it is supervised."),
        ("What does NLP stand for in AI?", "Neural Logic Programming", "Natural Language Processing", "Network Layer Protocol", "Numerical Learning Process", "B", "NLP = Natural Language Processing, how computers handle human language."),
        ("Artificial neural networks are inspired by which of the following?", "The human brain", "Electrical circuits", "Computer memory", "Search engines", "A", "ANNs loosely model neurons and synapses of the brain."),
        ("Which test checks whether a machine can show human-like intelligence?", "Bellman test", "Turing test", "Gödel test", "Hamming test", "B", "Proposed by Alan Turing in 1950."),
    ]),
    ("Database Management Systems", "Database Management", "SQL and relational database fundamentals.", "Medium", 5, [
        ("What does SQL stand for?", "Structured Query Language", "Simple Query Logic", "Sequential Query Language", "Standard Question List", "A", "SQL = Structured Query Language."),
        ("Which command quickly removes all rows from a table but keeps its structure?", "DROP", "TRUNCATE", "REMOVE", "CLEAR", "B", "TRUNCATE empties the table; DROP deletes the table itself."),
        ("What does a primary key do?", "Allows duplicate rows", "Uniquely identifies each row", "Links two databases", "Encrypts the table", "B", "A primary key is unique and not null for every row."),
        ("Which normal form removes partial dependency?", "1NF", "2NF", "3NF", "BCNF", "B", "2NF removes partial dependencies on part of a composite key."),
        ("Which SQL clause filters the results of GROUP BY?", "WHERE", "HAVING", "ORDER BY", "LIMIT", "B", "HAVING filters groups; WHERE filters rows before grouping."),
    ]),
    ("Computer Networks Fundamentals", "Computer Networks", "Protocols, layers, ports and devices.", "Medium", 5, [
        ("How many layers are there in the OSI model?", "4", "5", "7", "9", "C", "OSI has 7 layers: Physical to Application."),
        ("Which protocol is used for secure web browsing?", "HTTP", "FTP", "HTTPS", "SMTP", "C", "HTTPS = HTTP over TLS/SSL."),
        ("What is the default port number for HTTP?", "21", "80", "443", "25", "B", "HTTP uses port 80; HTTPS uses 443."),
        ("Which device forwards packets between different networks using IP addresses?", "Hub", "Switch", "Router", "Repeater", "C", "Routers operate at the network layer and connect networks."),
        ("How many bits are there in an IPv4 address?", "16", "32", "64", "128", "B", "IPv4 is 32 bits; IPv6 is 128 bits."),
    ]),
    ("General Knowledge Challenge", "General Knowledge", "A quick mix of everyday facts.", "Easy", 3, [
        ("What is the capital of India?", "Mumbai", "Kolkata", "New Delhi", "Chennai", "C", "New Delhi is the capital of India."),
        ("Which planet is known as the Red Planet?", "Venus", "Mars", "Jupiter", "Mercury", "B", "Iron oxide on its surface gives Mars a red colour."),
        ("Who wrote the Indian national anthem 'Jana Gana Mana'?", "Bankim Chandra Chatterjee", "Rabindranath Tagore", "Sarojini Naidu", "Subramania Bharati", "B", "Rabindranath Tagore wrote it."),
        ("What is the chemical symbol for gold?", "Go", "Gd", "Au", "Ag", "C", "Au comes from the Latin 'aurum'. Ag is silver."),
        ("Which is the largest ocean on Earth?", "Atlantic", "Indian", "Arctic", "Pacific", "D", "The Pacific covers about a third of the planet's surface."),
    ]),
]


def seed(reset: bool = False):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if reset:
            for m in (models.QuizAttempt, models.Question, models.Quiz):
                db.query(m).delete()
            db.commit()
        elif db.query(models.Quiz).count() > 0:
            print("Data already exists. Use 'python seed.py --reset' to reload.")
            return
        for title, cat, desc, diff, mins, qs in QUIZZES:
            quiz = models.Quiz(title=title, category=cat, description=desc, difficulty=diff,
                               total_questions=len(qs), duration_minutes=mins)
            db.add(quiz)
            db.flush()
            for t, a, b, c, d, ans, exp in qs:
                db.add(models.Question(quiz_id=quiz.id, question_text=t, option_a=a, option_b=b,
                                       option_c=c, option_d=d, correct_answer=ans, explanation=exp))
        db.commit()
        print(f"Seeded {len(QUIZZES)} quizzes and {sum(len(q[5]) for q in QUIZZES)} questions.")
    finally:
        db.close()


if __name__ == "__main__":
    seed("--reset" in sys.argv)
