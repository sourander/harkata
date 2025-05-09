# Harkata

## Overview

Harkata is a lightweight, stateless backend for real-time quizzes inspired by platforms like Socrative and Kahoot, but with a focus on simplicity and privacy. The key differentiators:

- No user accounts or authentication required
- No persistent data storage (everything is in-memory)
- Simple HTTP polling instead of WebSockets
- Automatic cleanup of inactive quizzes

## How It Works

### For Teachers

1. Upload a JSON file containing quiz questions following our schema
2. Receive two keys: `x-quiz-public-key` and `x-teacher-key`
3. Share the public key with students
4. Use the teacher key to:
    - View the list of connected students
    - Control quiz progression
    - End the quiz when finished

There is currently no UI for teachers that would allow them to upload a quiz, manage the quiz, view the results or create a quiz JSON. These will be implemented later.

### For Students (Using a separate client)

1. Join using the quiz's public key and a display name
2. Receive a `x-student-session-key` for the duration of the quiz
3. Answer questions as they are presented
4. See results based on teacher settings

Note that multiple different clients can be used to join any quiz, since there is not login process. Maybe a simple SPA WebApp? Or C++ app running on a Raspberry Pi? Or even a simple command line client? The possibilities are endless.

## Technical Features

- RESTful API with simple header-based authentication
- Fully documented with OpenAPI/Swagger UI
- In-memory data storage with automatic cleanup
- Stateless architecture for easy scaling
- No WebSockets required - simple polling mechanism

## Current Status

This project is currently in development.
