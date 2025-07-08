"""User management API routes."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database.connection import get_db
from ...database.models import User as DBUser
from ...models.user import User, UserCreate, UserUpdate, UserWithStats

router = APIRouter()


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    # Check if user already exists
    existing_user = (
        db.query(DBUser)
        .filter((DBUser.username == user.username) | (DBUser.email == user.email))
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    # Create new user
    db_user = DBUser(
        username=user.username, email=user.email, api_keys={}, preferences={}
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.get("/", response_model=List[User])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users."""
    users = db.query(DBUser).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserWithStats)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user with statistics."""
    user = db.query(DBUser).filter(DBUser.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Calculate statistics
    resume_count = len(user.resume_versions)
    application_count = len(user.job_applications)
    active_conversations = len(
        [c for c in user.conversations if c.job_application_id is not None]
    )

    return UserWithStats(
        **user.__dict__,
        resume_count=resume_count,
        application_count=application_count,
        active_conversations=active_conversations,
    )


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)
):
    """Update a user."""
    user = db.query(DBUser).filter(DBUser.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update fields
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user."""
    user = db.query(DBUser).filter(DBUser.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(user)
    db.commit()
