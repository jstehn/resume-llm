"""Resume management API routes."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database.connection import get_db
from ...database.models import ResumeVersion as DBResumeVersion
from ...database.models import User as DBUser
from ...models.resume import JSONResume

router = APIRouter()


@router.post("/users/{user_id}/versions", status_code=status.HTTP_201_CREATED)
async def create_resume_version(
    user_id: int,
    version_name: str,
    resume_data: JSONResume,
    db: Session = Depends(get_db),
):
    """Create a new resume version for a user."""
    # Check if user exists
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Create resume version
    db_resume = DBResumeVersion(
        user_id=user_id,
        version_name=version_name,
        json_resume_data=resume_data.model_dump(mode="json"),
        is_active=False,
    )

    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)

    return {
        "id": db_resume.id,
        "version_name": db_resume.version_name,
        "created_at": db_resume.created_at,
        "is_active": db_resume.is_active,
    }


@router.get("/users/{user_id}/versions")
async def get_user_resume_versions(user_id: int, db: Session = Depends(get_db)):
    """Get all resume versions for a user."""
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    versions = (
        db.query(DBResumeVersion).filter(DBResumeVersion.user_id == user_id).all()
    )

    return [
        {
            "id": version.id,
            "version_name": version.version_name,
            "created_at": version.created_at,
            "updated_at": version.updated_at,
            "is_active": version.is_active,
        }
        for version in versions
    ]


@router.get("/versions/{version_id}", response_model=JSONResume)
async def get_resume_version(version_id: int, db: Session = Depends(get_db)):
    """Get a specific resume version."""
    version = db.query(DBResumeVersion).filter(DBResumeVersion.id == version_id).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found"
        )

    return JSONResume(**version.json_resume_data)


@router.put("/versions/{version_id}", response_model=JSONResume)
async def update_resume_version(
    version_id: int, resume_data: JSONResume, db: Session = Depends(get_db)
):
    """Update a resume version."""
    version = db.query(DBResumeVersion).filter(DBResumeVersion.id == version_id).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found"
        )

    version.json_resume_data = resume_data.model_dump()
    db.commit()
    db.refresh(version)

    return JSONResume(**version.json_resume_data)


@router.post("/versions/{version_id}/activate", status_code=status.HTTP_200_OK)
async def activate_resume_version(version_id: int, db: Session = Depends(get_db)):
    """Activate a resume version (deactivate others for the same user)."""
    version = db.query(DBResumeVersion).filter(DBResumeVersion.id == version_id).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found"
        )

    # Deactivate all other versions for this user
    db.query(DBResumeVersion).filter(
        DBResumeVersion.user_id == version.user_id, DBResumeVersion.id != version_id
    ).update({"is_active": False})

    # Activate this version
    version.is_active = True
    db.commit()

    return {"message": "Resume version activated successfully"}


@router.delete("/versions/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume_version(version_id: int, db: Session = Depends(get_db)):
    """Delete a resume version."""
    version = db.query(DBResumeVersion).filter(DBResumeVersion.id == version_id).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found"
        )

    db.delete(version)
    db.commit()
