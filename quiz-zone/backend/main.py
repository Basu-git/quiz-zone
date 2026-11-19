"""Quiz Zone - FastAPI application.
Run (from the backend folder):  uvicorn main:app --reload
"""
import os
from pathlib import Path
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import crud
import models  # noqa: F401  (registers tables)
import schemas
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)  # creates tables if they don't exist

app = FastAPI(title="Quiz Zone API", version="1.0.0")

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["*"])


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/quizzes", response_model=List[schemas.QuizOut])
def list_quizzes(db: Session = Depends(get_db)):
    return crud.list_quizzes(db)


@app.get("/api/quizzes/{quiz_id}", response_model=schemas.QuizOut)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = crud.get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@app.get("/api/quizzes/{quiz_id}/questions", response_model=List[schemas.QuestionOut])
def get_questions(quiz_id: int, db: Session = Depends(get_db)):
    if not crud.get_quiz(db, quiz_id):
        raise HTTPException(status_code=404, detail="Quiz not found")
    return crud.get_questions(db, quiz_id, shuffle=True)


@app.post("/api/quizzes/{quiz_id}/submit", response_model=schemas.ResultOut, status_code=201)
def submit_quiz(quiz_id: int, payload: schemas.SubmitIn, db: Session = Depends(get_db)):
    quiz = crud.get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    try:
        attempt = crud.grade_and_save(db, quiz, payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return crud.build_result(db, attempt)


@app.get("/api/results/{attempt_id}", response_model=schemas.ResultOut)
def get_result(attempt_id: int, db: Session = Depends(get_db)):
    attempt = crud.get_attempt(db, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Result not found")
    return crud.build_result(db, attempt)


# Serve the two webpages from the same server (must be LAST so /api routes win)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
