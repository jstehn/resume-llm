"""Main FastAPI application."""

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..database.connection import get_db, init_db
from .routes import jobs, resumes, users

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Resume LLM API",
    description="AI-powered resume refinement tool API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(resumes.router, prefix="/api/v1/resumes", tags=["resumes"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Resume LLM API", "version": "0.1.0", "docs": "/docs"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}",
        )


if __name__ == "__main__":
    uvicorn.run(
        "resume_llm.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
