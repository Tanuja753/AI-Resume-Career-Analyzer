from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.routers.auth import router as auth_router
from app.routers.resume import router as resume_router
from app.routers.job_description import router as job_description_router

from app.database.database import get_db
from app.routers.skill_gap import router as skill_gap_router
from app.routers.job_compatibility import router as job_compatibility_router
from app.routers.interview_question import (
    router as interview_question_router,
)
from app.routers.preparation_plan import (
    router as preparation_plan_router,
)

from app.routers.preparation_progress import (
    router as preparation_progress_router,
)
from app.routers.resume_builder import (
    router as resume_builder_router,
)
from app.routers.resume_pdf import (
    router as resume_pdf_router,
)

app = FastAPI(
    title="AI Resume & Career Analyzer",
    description="Backend API for AI-powered resume and career analysis.",
    version="1.0.0",
)
app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(job_description_router)
app.include_router(
    skill_gap_router
)
app.include_router(job_compatibility_router)
app.include_router(
    interview_question_router
)
app.include_router(
    preparation_plan_router
)
app.include_router(preparation_progress_router)
app.include_router(
    resume_builder_router,
)
app.include_router(
    resume_pdf_router,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "AI Resume & Career Analyzer API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.get("/db-session-test")
def db_session_test(db: Session = Depends(get_db)):
    return {
        "message": "Database session dependency is working"
    }

@app.get("/db-test")
def database_test(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))

    return {
        "message": "PostgreSQL connection successful",
        "result": result.scalar()
    }