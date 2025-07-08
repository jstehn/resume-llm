"""Job application related Pydantic models."""

from datetime import datetime
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

from .resume import JSONResume


class JobApplicationBase(BaseModel):
    """Base job application model."""

    job_title: str = Field(..., max_length=200)
    company: str = Field(..., max_length=100)
    job_description: str
    status: Literal[
        "draft", "applied", "interview", "offer", "rejected", "withdrawn"
    ] = "draft"


class JobApplicationCreate(JobApplicationBase):
    """Job application creation model."""

    user_id: int
    resume_version_id: int


class JobApplicationUpdate(BaseModel):
    """Job application update model."""

    job_title: Optional[str] = Field(None, max_length=200)
    company: Optional[str] = Field(None, max_length=100)
    job_description: Optional[str] = None
    status: Optional[
        Literal["draft", "applied", "interview", "offer", "rejected", "withdrawn"]
    ] = None
    tailored_resume_data: Optional[JSONResume] = None


class JobApplication(JobApplicationBase):
    """Job application response model."""

    id: int
    user_id: int
    resume_version_id: int
    tailored_resume_data: Optional[JSONResume] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobAnalysisRequest(BaseModel):
    """Request model for job analysis."""

    job_description: str
    resume_data: JSONResume


class JobAnalysisResponse(BaseModel):
    """Response model for job analysis."""

    missing_skills: list[str]
    recommended_changes: list[str]
    match_score: float = Field(..., ge=0, le=1)
    suggestions: Dict[str, Any]
