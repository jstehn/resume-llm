"""Database models for Resume LLM."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base


class User(Base):
    """User model for storing user information and configurations."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    api_keys = Column(JSON, default={})  # Encrypted API keys
    preferences = Column(JSON, default={})  # User preferences
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    resume_versions = relationship("ResumeVersion", back_populates="user", cascade="all, delete-orphan")
    job_applications = relationship("JobApplication", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class ResumeVersion(Base):
    """Resume version model for storing different versions of a user's resume."""
    
    __tablename__ = "resume_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    version_name = Column(String(100), nullable=False)
    json_resume_data = Column(JSON, nullable=False)  # JSON Resume format
    is_active = Column(Boolean, default=False)  # Only one active version per user
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="resume_versions")
    job_applications = relationship("JobApplication", back_populates="resume_version")


class JobApplication(Base):
    """Job application model for tracking applications and tailored resumes."""
    
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_version_id = Column(Integer, ForeignKey("resume_versions.id"), nullable=False)
    job_title = Column(String(200), nullable=False)
    company = Column(String(100), nullable=False)
    job_description = Column(Text, nullable=False)
    tailored_resume_data = Column(JSON)  # Modified resume for this job
    status = Column(String(50), default="draft")  # draft, applied, interview, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="job_applications")
    resume_version = relationship("ResumeVersion", back_populates="job_applications")
    conversations = relationship("Conversation", back_populates="job_application", cascade="all, delete-orphan")


class Conversation(Base):
    """Conversation model for storing AI agent chat history."""
    
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=True)
    message_type = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    extra_data = Column(JSON, default={})  # Store additional context, thinking, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    job_application = relationship("JobApplication", back_populates="conversations")
