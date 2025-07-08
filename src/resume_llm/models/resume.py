"""JSON Resume schema models based on https://jsonresume.org/schema/"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class Location(BaseModel):
    """Location information."""
    address: Optional[str] = None
    postal_code: Optional[str] = Field(None, alias="postalCode")
    city: Optional[str] = None
    country_code: Optional[str] = Field(None, alias="countryCode")
    region: Optional[str] = None


class Profile(BaseModel):
    """Social media or professional profiles."""
    network: str  # e.g., "Twitter", "LinkedIn"
    username: Optional[str] = None
    url: HttpUrl


class Basics(BaseModel):
    """Basic information about the person."""
    name: str
    label: Optional[str] = None  # Job title
    image: Optional[str] = None  # Allow empty string for image
    email: Optional[str] = None
    phone: Optional[str] = None
    url: Optional[HttpUrl] = None
    summary: Optional[str] = None
    location: Optional[Location] = None
    profiles: Optional[List[Profile]] = Field(default_factory=list)


class Work(BaseModel):
    """Work experience."""
    name: str  # Company name
    position: str
    url: Optional[HttpUrl] = None
    start_date: Optional[str] = Field(None, alias="startDate")  # Allow empty string
    end_date: Optional[str] = Field(None, alias="endDate")  # Allow empty string
    summary: Optional[str] = None
    highlights: Optional[List[str]] = Field(default_factory=list)


class Volunteer(BaseModel):
    """Volunteer experience."""
    organization: str
    position: str
    url: Optional[HttpUrl] = None
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    summary: Optional[str] = None
    highlights: Optional[List[str]] = Field(default_factory=list)


class Education(BaseModel):
    """Education information."""
    institution: str
    url: Optional[HttpUrl] = None
    area: Optional[str] = None  # Field of study
    study_type: Optional[str] = Field(None, alias="studyType")  # Degree type
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    score: Optional[str] = None  # GPA, honors, etc.
    courses: Optional[List[str]] = Field(default_factory=list)


class Award(BaseModel):
    """Awards and honors."""
    title: str
    date_awarded: Optional[str] = Field(None, alias="date")
    awarder: Optional[str] = None  # Organization that gave the award
    summary: Optional[str] = None


class Certificate(BaseModel):
    """Certifications."""
    name: str
    issue_date: Optional[str] = Field(None, alias="date")
    url: Optional[HttpUrl] = None
    issuer: str


class Publication(BaseModel):
    """Publications."""
    name: str
    publisher: str
    release_date: Optional[str] = Field(None, alias="releaseDate")
    url: Optional[HttpUrl] = None
    summary: Optional[str] = None


class Skill(BaseModel):
    """Skills."""
    name: str
    level: Optional[str] = None  # e.g., "Master", "Intermediate"
    keywords: Optional[List[str]] = Field(default_factory=list)


class Language(BaseModel):
    """Languages."""
    language: str
    fluency: Optional[str] = None  # e.g., "Fluent", "Native"


class Interest(BaseModel):
    """Interests and hobbies."""
    name: str
    keywords: Optional[List[str]] = Field(default_factory=list)


class Reference(BaseModel):
    """References."""
    name: str
    reference: str  # The reference text


class Project(BaseModel):
    """Projects."""
    name: str
    description: Optional[str] = None
    highlights: Optional[List[str]] = Field(default_factory=list)
    keywords: Optional[List[str]] = Field(default_factory=list)
    start_date: Optional[str] = Field(None, alias="startDate")
    end_date: Optional[str] = Field(None, alias="endDate")
    url: Optional[HttpUrl] = None
    roles: Optional[List[str]] = Field(default_factory=list)
    entity: Optional[str] = None  # Organization or company
    type: Optional[str] = None  # e.g., "application", "library"


class Meta(BaseModel):
    """Metadata about the resume."""
    canonical: Optional[HttpUrl] = None
    version: Optional[str] = None
    last_modified: Optional[str] = Field(None, alias="lastModified")


class JSONResume(BaseModel):
    """Complete JSON Resume schema."""
    schema_url: Optional[str] = Field(default="https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json", alias="$schema")
    basics: Basics
    work: Optional[List[Work]] = Field(default_factory=list)
    volunteer: Optional[List[Volunteer]] = Field(default_factory=list)
    education: Optional[List[Education]] = Field(default_factory=list)
    awards: Optional[List[Award]] = Field(default_factory=list)
    certificates: Optional[List[Certificate]] = Field(default_factory=list)
    publications: Optional[List[Publication]] = Field(default_factory=list)
    skills: Optional[List[Skill]] = Field(default_factory=list)
    languages: Optional[List[Language]] = Field(default_factory=list)
    interests: Optional[List[Interest]] = Field(default_factory=list)
    references: Optional[List[Reference]] = Field(default_factory=list)
    projects: Optional[List[Project]] = Field(default_factory=list)
    meta: Optional[Meta] = None

    class Config:
        populate_by_name = True
