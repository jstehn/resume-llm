"""Job application and analysis API routes."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...agents import ResumeAgent
from ...database.connection import get_db
from ...database.models import JobApplication as DBJobApplication
from ...database.models import ResumeVersion as DBResumeVersion
from ...database.models import User as DBUser
from ...models.job import (
    JobAnalysisRequest,
    JobApplication,
    JobApplicationCreate,
    JobApplicationUpdate,
)

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
    analysis_request: JobAnalysisRequest, db: Session = Depends(get_db)  # noqa: ARG001
):
    """Analyze how well a resume matches a job description."""
    _ = db  # Acknowledge unused parameter for now
    try:
        agent = ResumeAgent()
        result = await agent.analyze_resume(
            resume_data=analysis_request.resume_data.model_dump()
        )

        return {
            "analysis_results": result,
            "suggestions": result,
            "change_summary": "Analysis complete",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        ) from e


@router.post("/applications/{application_id}/optimize")
async def optimize_resume_for_job(
    application_id: int,
    user_feedback: Optional[str] = None,  # noqa: ARG001
    db: Session = Depends(get_db),
):
    """Optimize a resume for a specific job application."""
    _ = user_feedback  # Acknowledge unused parameter for now
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
        if resume_version is not None:
            try:
                # Get the actual data from the SQLAlchemy model
                resume_data_raw = getattr(resume_version, "json_resume_data", None)
                job_desc_raw = getattr(application, "job_description", None)

                if not resume_data_raw:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Resume data is empty",
                    )

                if not job_desc_raw:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Job description is empty",
                    )

            except AttributeError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid resume data structure",
                ) from exc
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume version not found",
            )

        # Run optimization
        agent = ResumeAgent()
        result = await agent.optimize_resume(
            resume_data=resume_data_raw,
            job_description=job_desc_raw,
            company_name=getattr(application, "company_name", None),
        )

        # Store result in job application - for now just return the result
        return {
            "message": "Resume optimization complete",
            "optimization_result": result,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization failed: {str(e)}",
        ) from e


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
