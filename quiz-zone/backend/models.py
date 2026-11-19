"""SQLAlchemy table definitions."""
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base


class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, default="")
    difficulty = Column(String(20), nullable=False, default="Easy")
    total_questions = Column(Integer, nullable=False, default=0)
    duration_minutes = Column(Integer, nullable=False, default=5)
    created_at = Column(DateTime, default=datetime.utcnow)
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    option_a = Column(String(300), nullable=False)
    option_b = Column(String(300), nullable=False)
    option_c = Column(String(300), nullable=False)
    option_d = Column(String(300), nullable=False)
    correct_answer = Column(String(1), nullable=False)  # 'A', 'B', 'C' or 'D'
    explanation = Column(Text, default="")
    quiz = relationship("Quiz", back_populates="questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    incorrect_answers = Column(Integer, nullable=False)
    time_taken = Column(Integer, nullable=False, default=0)  # seconds
    answers_json = Column(Text, default="[]")  # review snapshot so results can be re-opened
    created_at = Column(DateTime, default=datetime.utcnow)
