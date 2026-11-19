"""Database operations + server-side grading."""
import json
import random
from sqlalchemy.orm import Session
import models
import schemas

PASS_PERCENT = 60


def list_quizzes(db: Session):
    return db.query(models.Quiz).order_by(models.Quiz.id).all()


def get_quiz(db: Session, quiz_id: int):
    return db.get(models.Quiz, quiz_id)


def get_questions(db: Session, quiz_id: int, shuffle: bool = False):
    qs = (db.query(models.Question).filter(models.Question.quiz_id == quiz_id)
          .order_by(models.Question.id).all())
    if shuffle:
        random.shuffle(qs)
    return qs


def grade_and_save(db: Session, quiz: models.Quiz, payload: schemas.SubmitIn) -> models.QuizAttempt:
    """Compare submitted answers with the stored correct answers. Frontend score is never used."""
    questions = {q.id: q for q in get_questions(db, quiz.id)}
    chosen = {}
    for a in payload.answers:
        if a.question_id not in questions:
            raise ValueError(f"Question {a.question_id} does not belong to this quiz")
        chosen[a.question_id] = a.selected

    review, correct = [], 0
    for q in questions.values():
        sel = chosen.get(q.id)
        ok = sel == q.correct_answer
        correct += int(ok)
        review.append({
            "question_id": q.id, "question_text": q.question_text,
            "option_a": q.option_a, "option_b": q.option_b,
            "option_c": q.option_c, "option_d": q.option_d,
            "selected": sel, "correct_answer": q.correct_answer,
            "is_correct": ok, "explanation": q.explanation or "",
        })

    total = len(questions)
    pct = round(correct / total * 100, 2) if total else 0.0
    attempt = models.QuizAttempt(
        quiz_id=quiz.id, score=correct, total_questions=total, percentage=pct,
        correct_answers=correct, incorrect_answers=total - correct,
        time_taken=min(payload.time_taken, quiz.duration_minutes * 60),
        answers_json=json.dumps(review),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def get_attempt(db: Session, attempt_id: int):
    return db.get(models.QuizAttempt, attempt_id)


def build_result(db: Session, attempt: models.QuizAttempt) -> dict:
    quiz = db.get(models.Quiz, attempt.quiz_id)
    return {
        "attempt_id": attempt.id, "quiz_id": attempt.quiz_id,
        "quiz_title": quiz.title if quiz else "Quiz",
        "total_questions": attempt.total_questions,
        "correct_answers": attempt.correct_answers,
        "incorrect_answers": attempt.incorrect_answers,
        "percentage": attempt.percentage,
        "passed": attempt.percentage >= PASS_PERCENT,
        "pass_percentage": PASS_PERCENT,
        "time_taken": attempt.time_taken,
        "created_at": attempt.created_at,
        "review": json.loads(attempt.answers_json or "[]"),
    }
