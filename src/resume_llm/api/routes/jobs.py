"""Job application and analysis API routes."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...agents.resume_agent import ResumeAgent
from ...database.connection import get_db
from ...database.models import JobApplication as DBJobApplication
from ...database.models import ResumeVersion as DBResumeVersion
from ...database.models import User as DBUser
from ...models.job import (
    JobAnalysisRequest,
    JobAnalysisResponse,
    JobApplication,
    JobApplicationCreate,
    JobApplicationUpdate,
)
from ...models.resume import JSONResume

router = APIRouter()


@router.post(
    "/applications", response_model=JobApplication, status_code=status.HTTP_201_CREATED
)
async def create_job_application(
    application: JobApplicationCreate, db: Session = Depends(get_db)
):
    """Create a new job application."""
    # Verify user and resume version exist
    user = (
        db.query(DBUser).filter(DBUser.id == application.user_id).first()
    )  # Fixed: Added user_id to model
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    resume_version = (
        db.query(DBResumeVersion)
        .filter(DBResumeVersion.id == application.resume_version_id)
        .first()
    )
    if not resume_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found"
        )

    # Create job application
    db_application = DBJobApplication(**application.model_dump())

    db.add(db_application)
    db.commit()
    db.refresh(db_application)

    return db_application


@router.get("/applications/user/{user_id}", response_model=List[JobApplication])
async def get_user_job_applications(user_id: int, db: Session = Depends(get_db)):
    """Get all job applications for a user."""
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    applications = (
        db.query(DBJobApplication).filter(DBJobApplication.user_id == user_id).all()
    )

    return applications


@router.get("/applications/{application_id}", response_model=JobApplication)
async def get_job_application(application_id: int, db: Session = Depends(get_db)):
    """Get a specific job application."""
    application = (
        db.query(DBJobApplication).filter(DBJobApplication.id == application_id).first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job application not found"
        )

    return application


@router.put("/applications/{application_id}", response_model=JobApplication)
async def update_job_application(
    application_id: int,
    application_update: JobApplicationUpdate,
    db: Session = Depends(get_db),
):
    """Update a job application."""
    application = (
        db.query(DBJobApplication).filter(DBJobApplication.id == application_id).first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job application not found"
        )

    # Update fields
    update_data = application_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "tailored_resume_data" and value:
            setattr(application, field, value.model_dump())
        else:
            setattr(application, field, value)

    db.commit()
    db.refresh(application)

    return application


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_job_resume_match(
    analysis_request: JobAnalysisRequest, db: Session = Depends(get_db)
):
    """Analyze how well a resume matches a job description."""
    try:
        agent = ResumeAgent()
        result = await agent.run(
            resume_data=analysis_request.resume_data,
            job_description=analysis_request.job_description,
        )

        return {
            "analysis_results": result.get("analysis_results", {}),
            "suggestions": result.get("analysis_results", {}).get("suggestions", {}),
            "change_summary": result.get("change_summary"),
            "optimized_resume": (
                result.get("optimized_resume").model_dump()
                if result.get("optimized_resume")
                else None
            ),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )


@router.post("/applications/{application_id}/optimize")
async def optimize_resume_for_job(
    application_id: int, user_feedback: str = None, db: Session = Depends(get_db)
):
    """Optimize a resume for a specific job application."""
    # Get job application
    application = (
        db.query(DBJobApplication).filter(DBJobApplication.id == application_id).first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job application not found"
        )

    # Get resume version
    resume_version = (
        db.query(DBResumeVersion)
        .filter(DBResumeVersion.id == application.resume_version_id)
        .first()
    )

    if not resume_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found"
        )

    try:
        # Create resume object from stored data
        resume_data = JSONResume(**resume_version.json_resume_data)

        # Run optimization
        agent = ResumeAgent()
        result = await agent.run(
            resume_data=resume_data,
            job_description=application.job_description,
            user_feedback=user_feedback,
        )

        # Store optimized resume in job application
        if result.get("optimized_resume"):
            application.tailored_resume_data = result["optimized_resume"].model_dump()
            db.commit()

        return {
            "analysis_results": result.get("analysis_results", {}),
            "optimized_resume": (
                result.get("optimized_resume").model_dump()
                if result.get("optimized_resume")
                else None
            ),
            "change_summary": result.get("change_summary"),
            "next_action": result.get("next_action"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization failed: {str(e)}",
        )


@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_application(application_id: int, db: Session = Depends(get_db)):
    """Delete a job application."""
    application = (
        db.query(DBJobApplication).filter(DBJobApplication.id == application_id).first()
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job application not found"
        )

    db.delete(application)
    db.commit()
