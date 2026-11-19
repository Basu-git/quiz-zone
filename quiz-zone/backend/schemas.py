"""Pydantic models: request validation and response shapes."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class QuizOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    category: str
    description: Optional[str] = ""
    difficulty: str
    total_questions: int
    duration_minutes: int


class QuestionOut(BaseModel):
    """Note: NO correct_answer / explanation here, so answers are never leaked."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str


class AnswerIn(BaseModel):
    question_id: int
    selected: Optional[str] = Field(default=None, pattern="^[A-D]$")


class SubmitIn(BaseModel):
    answers: List[AnswerIn] = Field(max_length=100)
    time_taken: int = Field(default=0, ge=0, le=86400)


class ReviewItem(BaseModel):
    question_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    selected: Optional[str] = None
    correct_answer: str
    is_correct: bool
    explanation: Optional[str] = ""


class ResultOut(BaseModel):
    attempt_id: int
    quiz_id: int
    quiz_title: str
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    percentage: float
    passed: bool
    pass_percentage: int
    time_taken: int
    created_at: datetime
    review: List[ReviewItem]
