from pydantic import BaseModel

class QuizCreateResponse(BaseModel):
    quiz_public_key: str
    quiz_private_key: str

class QuizKeyName(BaseModel):
    quiz_public_key: str
    quiz_name: str
    time_to_live: int

class QuizListResponse(BaseModel):
    active_quizzes: list[QuizKeyName]
