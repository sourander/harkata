import uuid
import time
from typing import Dict, List, Optional, Tuple
from harkata.models.entities import Quiz
from harkata.models.responses import QuizCreateResponse, QuizListResponse, QuizKeyName

class ActiveQuiz:
    """Class representing an active quiz instance in memory."""
    
    def __init__(self, quiz_contents: Quiz, public_key: str, private_key: str):
        self.quiz_contents = quiz_contents
        self.public_key = public_key
        self.private_key = private_key
        self.created_at = time.time()
    
    def add_student(self, name: str) -> str:
        """Add a student to the quiz and return their session key."""
        raise NotImplementedError()
    
    def submit_answer(self, student_key: str, question_number: int, answers: List[str]) -> bool:
        """Submit an answer for a student."""
        raise NotImplementedError()
    
    def get_student_names(self) -> List[str]:
        """Get all student names who have joined this quiz."""
        raise NotImplementedError()
        
    def is_expired(self, max_age_seconds: int = 14400) -> bool:
        """Check if the quiz is older than the maximum age (default 4 hours)."""
        return (time.time() - self.created_at) > max_age_seconds


class QuizManager:
    """Manages all active quizzes in the application."""
    
    def __init__(self):
        self.quizzes: Dict[str, ActiveQuiz] = {}  # public_key -> Quiz object
        self.teacher_keys: Dict[str, str] = {}  # private_key -> public_key
    
    def create_quiz(self, quiz_contents: Quiz) -> QuizCreateResponse:
        """Create a new quiz and return public and private keys."""
        public_key = str(uuid.uuid4())
        private_key = str(uuid.uuid4())
        
        quiz = ActiveQuiz(quiz_contents, public_key, private_key)
        self.quizzes[public_key] = quiz
        self.teacher_keys[private_key] = public_key

        return QuizCreateResponse(quiz_public_key=public_key, quiz_private_key=private_key)
    
    def get_quiz_by_public_key(self, public_key: str) -> Optional[ActiveQuiz]:
        """Get a quiz by its public key."""
        return self.quizzes.get(public_key)
    
    def get_quiz_by_private_key(self, private_key: str) -> Optional[ActiveQuiz]:
        """Get a quiz by teacher's private key."""
        public_key = self.teacher_keys.get(private_key)
        if public_key:
            return self.quizzes.get(public_key)
        return None
    
    async def end_quiz(self, private_key: str) -> bool:
        """End a quiz and remove it from active quizzes."""
        public_key = self.teacher_keys.get(private_key)
        if public_key and public_key in self.quizzes:
            del self.quizzes[public_key]
            del self.teacher_keys[private_key]
            return True
        return False
    
    def get_all_quizzes(self) -> QuizListResponse:
        """Get all active quizzes."""

        active_quizzes = [
            QuizKeyName(
                quiz_public_key=quiz.public_key, 
                quiz_name=quiz.quiz_contents.quiz_name,
                time_to_live=int(quiz.created_at + 14400 - time.time()),
            )
            for quiz in self.quizzes.values()
        ]
        return QuizListResponse(active_quizzes=active_quizzes)    

    async def async_cleanup_expired_quizzes(self) -> int:
        """Async version of cleanup_expired_quizzes."""
        for quiz in self.quizzes.copy().values():
            if quiz.is_expired():
                del self.quizzes[quiz.public_key]
                del self.teacher_keys[quiz.private_key]
                print(f"Removed expired quiz: {quiz.public_key}")
    
    