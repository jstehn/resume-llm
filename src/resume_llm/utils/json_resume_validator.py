"""JSON Resume schema validation utilities."""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from jsonschema import Draft7Validator, ValidationError


class JSONResumeValidator:
    """Validator for JSON Resume schema compliance."""

    def __init__(self):
        """Initialize validator with JSON Resume schema."""
        self.schema_path = (
            Path(__file__).parent.parent / "config" / "jsonresume_schema.json"
        )
        self.schema = None
        self.validator = None

        self._load_schema()

    def _load_schema(self):
        """Load the JSON Resume schema."""
        try:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                self.schema = json.load(f)
            self.validator = Draft7Validator(self.schema)
        except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
            print(f"Warning: Could not load JSON Resume schema: {e}")

    def validate(self, resume_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate resume data against JSON Resume schema.

        Args:
            resume_data: Resume data to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """

        if not self.validator:
            return False, ["Schema not loaded"]

        errors = []

        try:
            # Validate against schema
            for error in self.validator.iter_errors(resume_data):
                path = ".".join(str(p) for p in error.path) if error.path else "root"
                errors.append(f"Validation error at {path}: {error.message}")
        except (TypeError, ValueError, ValidationError) as e:
            errors.append(f"Schema validation failed: {str(e)}")

        return len(errors) == 0, errors

    def validate_resume_string(self, resume_json: str) -> Tuple[bool, List[str]]:
        """
        Validate JSON Resume string.

        Args:
            resume_json: JSON Resume as string

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        try:
            resume_data = json.loads(resume_json)
            return self.validate(resume_data)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {str(e)}"]

    def get_schema_path(self) -> Path:
        """Get the path to the JSON Resume schema file."""
        return self.schema_path

    def get_schema_dict(self) -> Dict[str, Any]:
        """Get the JSON Resume schema as a dictionary."""
        if not self.schema:
            self._load_schema()
        return self.schema or {}

    def get_schema_summary(self) -> str:
        """Get a human-readable summary of the JSON Resume schema."""
        return """
JSON Resume Schema Summary:
• basics: Personal information, contact details, and profiles
• work: Professional experience with highlights
• volunteer: Volunteer experience
• education: Educational background
• awards: Awards and recognition
• certificates: Professional certifications
• publications: Published works
• skills: Technical and soft skills with keywords
• languages: Language proficiencies
• interests: Personal interests
• references: Professional references
• projects: Personal or professional projects (entity and type fields allowed)
• meta: Schema metadata

All sections are optional except 'basics' which should contain at least 'name'.
Date format: ISO 8601 with flexibility (YYYY-MM-DD, YYYY-MM, or YYYY)
        """.strip()

    def get_schema_structure(self) -> str:
        """Get a detailed structure of the JSON Resume schema."""
        return """
JSON Resume Schema Structure:

{
  "$schema": "string (URI)",
  "basics": {
    "name": "string (required)",
    "label": "string (e.g. Web Developer)",
    "image": "string (URL to image)",
    "email": "string (email format)",
    "phone": "string (any format)",
    "url": "string (URI)",
    "summary": "string (2-3 sentences)",
    "location": {
      "address": "string",
      "postalCode": "string",
      "city": "string",
      "countryCode": "string (ISO-3166-1 ALPHA-2)",
      "region": "string"
    },
    "profiles": [{
      "network": "string (e.g. Twitter)",
      "username": "string",
      "url": "string (URI)"
    }]
  },
  "work": [{
    "name": "string (company name)",
    "location": "string (e.g. Menlo Park, CA)",
    "description": "string (company description)",
    "position": "string (job title)",
    "url": "string (URI)",
    "startDate": "string (ISO 8601: YYYY-MM-DD, YYYY-MM, or YYYY)",
    "endDate": "string (ISO 8601: YYYY-MM-DD, YYYY-MM, or YYYY)",
    "summary": "string (overview of responsibilities)",
    "highlights": ["string (accomplishments)"]
  }],
  "volunteer": [{
    "organization": "string",
    "position": "string",
    "url": "string (URI)",
    "startDate": "string (ISO 8601)",
    "endDate": "string (ISO 8601)",
    "summary": "string",
    "highlights": ["string"]
  }],
  "education": [{
    "institution": "string",
    "url": "string (URI)",
    "area": "string (field of study)",
    "studyType": "string (e.g. Bachelor)",
    "startDate": "string (ISO 8601)",
    "endDate": "string (ISO 8601)",
    "score": "string (e.g. 3.67/4.0)",
    "courses": ["string (course names)"]
  }],
  "awards": [{
    "title": "string",
    "date": "string (ISO 8601)",
    "awarder": "string",
    "summary": "string"
  }],
  "certificates": [{
    "name": "string",
    "date": "string (ISO 8601)",
    "url": "string (URI)",
    "issuer": "string"
  }],
  "publications": [{
    "name": "string",
    "publisher": "string",
    "releaseDate": "string (ISO 8601)",
    "url": "string (URI)",
    "summary": "string"
  }],
  "skills": [{
    "name": "string (skill category)",
    "level": "string (e.g. Master)",
    "keywords": ["string (skill keywords)"]
  }],
  "languages": [{
    "language": "string (e.g. English)",
    "fluency": "string (e.g. Fluent)"
  }],
  "interests": [{
    "name": "string",
    "keywords": ["string"]
  }],
  "references": [{
    "name": "string",
    "reference": "string (reference text)"
  }],
  "projects": [{
    "name": "string",
    "description": "string",
    "highlights": ["string"],
    "keywords": ["string"],
    "startDate": "string (ISO 8601)",
    "endDate": "string (ISO 8601)",
    "url": "string (URI)",
    "roles": ["string (e.g. Team Lead)"],
    "entity": "string (company/organization)",
    "type": "string (e.g. application, volunteering)"
  }],
  "meta": {
    "canonical": "string (URI)",
    "version": "string (semver)",
    "lastModified": "string (ISO 8601)"
  }
}
        """.strip()


# Global validator instance
json_resume_validator = JSONResumeValidator()
