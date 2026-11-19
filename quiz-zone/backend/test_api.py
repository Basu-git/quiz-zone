"""Quick automated test: python test_api.py  (uses a temporary SQLite DB)"""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test_tmp.db"
from fastapi.testclient import TestClient
import seed
from main import app
from database import SessionLocal
import models

seed.seed(reset=True)
c = TestClient(app)

qs = c.get("/api/quizzes").json(); assert len(qs) == 5, qs
assert all(q["total_questions"] == 5 for q in qs)
assert c.get("/api/quizzes/1").status_code == 200
assert c.get("/api/quizzes/999").status_code == 404
questions = c.get("/api/quizzes/1/questions").json()
assert len(questions) == 5 and all("correct_answer" not in q and "explanation" not in q for q in questions)
assert "index.html" or c.get("/").status_code == 200 and c.get("/quiz.html").status_code == 200

db = SessionLocal()
truth = {q.id: q.correct_answer for q in db.query(models.Question).filter_by(quiz_id=1)}
ids = [q["id"] for q in questions]
# 3 correct, 1 wrong, 1 unanswered
ans = [{"question_id": ids[0], "selected": truth[ids[0]]}, {"question_id": ids[1], "selected": truth[ids[1]]},
       {"question_id": ids[2], "selected": truth[ids[2]]},
       {"question_id": ids[3], "selected": "A" if truth[ids[3]] != "A" else "B"}, {"question_id": ids[4], "selected": None}]
r = c.post("/api/quizzes/1/submit", json={"answers": ans, "time_taken": 42}); assert r.status_code == 201, r.text
j = r.json(); assert (j["correct_answers"], j["incorrect_answers"], j["percentage"], j["passed"]) == (3, 2, 60.0, True), j
r2 = c.get(f"/api/results/{j['attempt_id']}").json(); assert r2["correct_answers"] == 3 and len(r2["review"]) == 5
assert c.get("/api/results/9999").status_code == 404
assert c.post("/api/quizzes/1/submit", json={"answers": [{"question_id": 1, "selected": "Z"}], "time_taken": 1}).status_code == 422
assert c.post("/api/quizzes/1/submit", json={"answers": [{"question_id": 9999, "selected": "A"}], "time_taken": 1}).status_code == 422
assert c.post("/api/quizzes/999/submit", json={"answers": [], "time_taken": 1}).status_code == 404
j0 = c.post("/api/quizzes/1/submit", json={"answers": [], "time_taken": 5}).json(); assert j0["percentage"] == 0 and not j0["passed"]
assert db.query(models.QuizAttempt).count() == 2
assert db.query(models.Question).count() == 25
print("ALL TESTS PASSED")
db.close(); os.remove("test_tmp.db")
