## Flow of the application

The application is a quiz engine with the following requirements:


* Teachers upload a JSON file containing questions in a predefined schema.
* Successful upload returns two keys: `x-quiz-public-key` and `x-teacher-key`.
* Teachers retain the teacher key (e.g., in a cookie) to manage the quiz.
* Students join a quiz by supplying `x-quiz-public-key` and a display name; the backend returns an `x-student-session-key`.
`x-student-session-key` is retained (e.g., in a cookie) for the duration of the quiz.
* Teachers can view the list of students who have joined the quiz.
* Teachers advance the quiz by sending a POST request to set the active question using `x-teacher-key`.
Front‑end clients poll a GET endpoint (`/quizzes/{x-quiz-public-key}/current_question`) to retrieve the active question.
* Students submit answers via POST; the system stores only the latest answer per combination of `x-quiz-public-key`, `x-student-session-key`, and question number.
* Automatic cleanup removes quizzes older than four hours or upon teacher termination.
* All endpoints use simple token‑based auth via headers (`x-teacher-key`, `x-student-session-key`), no WebSockets required.
* The API is fully documented via FastAPI's OpenAPI/Swagger interface, enabling use with curl or Postman, or even the Swagger UI's interactive interface.
* Nothing is persisted in a database; all data is stored in memory.
* Application is stateless, with no session management.


## Endpoints

### Teacher Endpoints

* `GET /quizzes`  
    Returns a list of all active quizzes.

* `POST /quizzes`  
    Teacher uploads a quiz JSON file to create a new quiz. Returns `x-quiz-public-key` and `x-teacher-key`.

* `POST /quizzes/{x-quiz-public-key}/set_active_question`  
    Teacher sets the active question number. Requires `x-teacher-key`.

* `POST /quizzes/{x-quiz-public-key}/end`  
    Teacher ends the quiz and removes it from the active pool. Requires `x-teacher-key`.

* `GET /quizzes/{x-quiz-public-key}/results`  
    (Optional) Teacher fetches results or answer stats for the quiz.

### Student Endpoints

* `POST /quizzes/{x-quiz-public-key}/join`  
    Student joins a quiz with a name. Returns `x-student-session-key`.

* `POST /quizzes/{x-quiz-public-key}/questions/{question_number}/answer` [^key-req]
    Student submits or updates their answer for a specific question. The question must be active in order to accept the answer.

* `GET /quizzes/{x-quiz-public-key}/current_question` [^key-req]
    Returns the current active question for the quiz.

* `GET /quizzes/{x-quiz-public-key}/questions/{question_number}` [^key-req]
    Returns the full details of a specific question.

[^key-req]: The `x-student-session-key` is required for this endpoint, but it is not explicitly mentioned in the endpoint description. It should be included in the request headers to authenticate the student session.


## Data Dictionary

| Header Name             | Variable Name            | Description                                                        |
| ----------------------- | ------------------------ | ------------------------------------------------------------------ |
| `x-quiz-public-key`     | `ActiveQuiz.public_key`  | Unique identifier for the quiz, generated upon creation.           |
| `x-teacher-key`         | `ActiveQuiz.private_key` | Unique identifier for the teacher, generated upon creation.        |
| `x-student-session-key` | `Not Implemented Yet`    | Unique identifier for the student session, generated upon joining. |
