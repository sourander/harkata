import asyncio

from contextlib import asynccontextmanager
from fastapi import FastAPI
from harkata.quiz import QuizManager

# We want to use this as a singleton
# If you need it, import it from here
QM = QuizManager()

async def periodic_cleanup():
    while True:
        await asyncio.sleep(5)
        await QM.async_cleanup_expired_quizzes()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background task
    task = asyncio.create_task(periodic_cleanup())
    yield
    # Cancel the task on shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Harkata API",
    description="A simple API for Harkata, a tool for managing and analyzing data.",
    version="0.1.0",
    lifespan=lifespan,
)