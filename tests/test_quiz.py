import pytest
import time
import uuid

from harkata.quiz import QuizManager, ActiveQuiz
from harkata.models.entities import Quiz, Question, AnswerOption

class TestActiveQuiz:
    """Tests for the ActiveQuiz class."""

    @pytest.fixture
    def sample_quiz(self) -> Quiz:
        """Create a sample quiz for testing."""
        return Quiz(
            quiz_name="Test Quiz",
            questions=[
                Question(
                    question_id=1,
                    question_text="What is 2+2?",
                    options=[
                        AnswerOption(option_id=1, option_text="3", is_correct=False),
                        AnswerOption(option_id=2, option_text="4", is_correct=True),
                        AnswerOption(option_id=3, option_text="5", is_correct=False),
                    ]
                ),
                Question(
                    question_id=2,
                    question_text="What is the capital of France?",
                    options=[
                        AnswerOption(option_id=1, option_text="London", is_correct=False),
                        AnswerOption(option_id=2, option_text="Paris", is_correct=True),
                        AnswerOption(option_id=3, option_text="Berlin", is_correct=False),
                    ]
                )
            ]
        )
    
    @pytest.fixture
    def active_quiz(self, sample_quiz: Quiz) -> ActiveQuiz:
        """Create an ActiveQuiz instance for testing."""
        public_key = str(uuid.uuid4())
        private_key = str(uuid.uuid4())
        return ActiveQuiz(sample_quiz, public_key, private_key)

    def test_init(self, active_quiz: ActiveQuiz, sample_quiz: Quiz) -> None:
        """Test the initialization of ActiveQuiz."""
        assert active_quiz.quiz_contents == sample_quiz
        # No need to test that UUID strings are strings
        assert active_quiz.created_at <= time.time()

    def test_is_expired(self, active_quiz: ActiveQuiz) -> None:
        """Test the is_expired method."""
        # Quiz should not be expired initially
        assert not active_quiz.is_expired()
        
        # Mock the creation time to be 5 hours ago (18000 seconds)
        active_quiz.created_at = time.time() - 18000
        
        # Quiz should be expired with default max age (4 hours = 14400 seconds)
        assert active_quiz.is_expired()
        
        # Quiz should not be expired with custom max age of 6 hours (21600 seconds)
        assert not active_quiz.is_expired(max_age_seconds=21600)


class TestQuizManager:
    """Tests for the QuizManager class."""

    @pytest.fixture
    def manager(self) -> QuizManager:
        """Create a QuizManager instance for testing."""
        return QuizManager()
    
    @pytest.fixture
    def sample_quiz(self) -> Quiz:
        """Create a sample quiz for testing."""
        return Quiz(
            quiz_name="Test Quiz",
            questions=[
                Question(
                    question_id=1,
                    question_text="What is 2+2?",
                    options=[
                        AnswerOption(option_id=1, option_text="3", is_correct=False),
                        AnswerOption(option_id=2, option_text="4", is_correct=True),
                        AnswerOption(option_id=3, option_text="5", is_correct=False),
                    ]
                )
            ]
        )

    def test_init(self, manager: QuizManager) -> None:
        """Test initialization of QuizManager."""
        # Verify collections start empty
        assert len(manager.quizzes) == 0
        assert len(manager.teacher_keys) == 0
    
    def test_create_quiz(self, manager: QuizManager, sample_quiz: Quiz) -> None:
        """Test creating a new quiz."""
        response = manager.create_quiz(sample_quiz)
        
        # Get the keys from the response
        public_key = response.quiz_public_key
        private_key = response.quiz_private_key
        
        # Verify quiz is stored correctly
        assert len(manager.quizzes) == 1
        assert public_key in manager.quizzes
        assert manager.teacher_keys[private_key] == public_key
        
        # Verify quiz data integrity
        quiz_obj = manager.quizzes[public_key]
        assert quiz_obj.quiz_contents == sample_quiz
    
    def test_get_quiz_by_public_key(self, manager: QuizManager, sample_quiz: Quiz) -> None:
        """Test retrieving a quiz by its public key."""
        response = manager.create_quiz(sample_quiz)
        public_key = response.quiz_public_key
        
        # Verify retrieval with valid key
        quiz = manager.get_quiz_by_public_key(public_key)
        assert quiz is not None
        assert quiz.quiz_contents == sample_quiz
        
        # Verify behavior with invalid key
        assert manager.get_quiz_by_public_key(str(uuid.uuid4())) is None
    
    def test_get_quiz_by_private_key(self, manager: QuizManager, sample_quiz: Quiz) -> None:
        """Test retrieving a quiz by its private key."""
        response = manager.create_quiz(sample_quiz)
        private_key = response.quiz_private_key
        
        # Test retrieval with valid key
        quiz = manager.get_quiz_by_private_key(private_key)
        assert quiz is not None
        assert quiz.quiz_contents == sample_quiz
        
        # Test retrieval with invalid key
        assert manager.get_quiz_by_private_key(str(uuid.uuid4())) is None
    
    @pytest.mark.asyncio
    async def test_end_quiz(self, manager: QuizManager, sample_quiz: Quiz) -> None:
        """Test ending a quiz."""
        response = manager.create_quiz(sample_quiz)
        private_key = response.quiz_private_key
        
        # Test ending with valid key
        result = await manager.end_quiz(private_key)
        assert result is True
        assert len(manager.quizzes) == 0
        
        # Test ending with invalid key
        response = manager.create_quiz(sample_quiz)
        result = await manager.end_quiz(str(uuid.uuid4()))
        assert result is False
        assert len(manager.quizzes) == 1
    
    def test_get_all_quizzes(self, manager: QuizManager) -> None:
        """Test getting all active quizzes."""
        # Test with no quizzes
        response = manager.get_all_quizzes()
        assert len(response.active_quizzes) == 0
        
        # Create some quizzes
        quiz1 = Quiz(quiz_name="Quiz 1", questions=[])
        quiz2 = Quiz(quiz_name="Quiz 2", questions=[])
        
        manager.create_quiz(quiz1)
        manager.create_quiz(quiz2)
        
        # Test with quizzes
        response = manager.get_all_quizzes()
        assert len(response.active_quizzes) == 2
        
        # Just check basic properties without redundant type assertions
        for entry in response.active_quizzes:
            assert entry.quiz_name in ["Quiz 1", "Quiz 2"]
            assert entry.time_to_live <= 14400  # Max TTL is 4 hours (14400 seconds)
    
    @pytest.mark.asyncio
    async def test_async_cleanup_expired_quizzes(self, manager: QuizManager, sample_quiz: Quiz, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test the async cleanup of expired quizzes."""
        # Simplified test that focuses on key behavior
        response = manager.create_quiz(sample_quiz)
        quiz = manager.get_quiz_by_public_key(response.quiz_public_key)
        
        # Mock the expiration check to simulate an expired quiz
        quiz.is_expired = lambda: True
        
        await manager.async_cleanup_expired_quizzes()
        assert len(manager.quizzes) == 0


    @pytest.mark.asyncio
    async def test_async_cleanup_expired_quizzes_with_non_expiring_quiz(self, manager: QuizManager, sample_quiz: Quiz) -> None:
        """Test the async cleanup of expired quizzes with a non-expiring quiz."""
        # Create a non-expiring quiz
        response = manager.create_quiz(sample_quiz)
        quiz = manager.get_quiz_by_public_key(response.quiz_public_key)
        
        # Mock the expiration check to simulate a non-expired quiz
        quiz.is_expired = lambda: False
        
        await manager.async_cleanup_expired_quizzes()
        assert len(manager.quizzes) == 1