from harkata import QM, app
from harkata.models.entities import Quiz
from harkata.models.responses import QuizCreateResponse, QuizListResponse
from pathlib import Path

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/quizzes")
async def create_quiz(quiz: Quiz = None) -> QuizCreateResponse:
    if quiz is None:
        # Load default quiz from example_quiz.json
        default_path = Path(__file__).parent / "data" / "example_quiz.json"
        default_path = default_path.resolve()
        default_path.read_bytes()
        quiz = Quiz.model_validate_json(default_path.read_text(encoding="utf-8"))

    # Add the Quiz to the QuizManager by calling the add_quiz method
    response = QM.create_quiz(quiz)
            
    return response

@app.get("/quizzes")
async def get_quizzes() -> QuizListResponse:
    return QM.get_all_quizzes()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

