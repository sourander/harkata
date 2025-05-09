from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class AnswerOption(BaseModel):
    option_id: int
    option_text: str
    is_correct: bool

class Question(BaseModel):
    question_id: int
    question_text: str
    options: List[AnswerOption]

class Quiz(BaseModel):
    quiz_name: str
    questions: List[Question]
