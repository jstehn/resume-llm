"""Resume ingestion service for parsing different resume formats."""

import json
from io import StringIO
from pathlib import Path
from typing import Any, Dict, Optional

import pypdf

from ..models.resume import JSONResume


class ResumeIngestionService:
    """Service for ingesting resumes from various formats."""

    def __init__(self):
        pass

    def parse_json_resume(self, file_path: Path) -> JSONResume:
        """Parse a JSON Resume file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return JSONResume(**data)

    def parse_pdf_resume(self, file_path: Path) -> str:
        """Extract text from a PDF resume."""
        with open(file_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

        return text.strip()

    def text_to_json_resume(self, text: str, name: str = "Unknown") -> JSONResume:
        """Convert plain text resume to JSON Resume format.

        This is a basic implementation that would benefit from LLM enhancement.
        """
        # Basic parsing - in a real implementation, use LLM to extract structured data
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Try to extract name from first line
        if lines:
            potential_name = lines[0]
            if len(potential_name.split()) <= 4 and not any(
                char in potential_name for char in ["@", "http", "www"]
            ):
                name = potential_name

        # Create basic JSON Resume structure
        resume_data = {
            "basics": {
                "name": name,
                "email": None,
                "phone": None,
                "summary": " ".join(lines[:5]),  # Use first few lines as summary
            },
            "work": [],
            "education": [],
            "skills": [],
        }

        return JSONResume(**resume_data)

    async def ingest_resume(
        self, file_path: Path, format_type: Optional[str] = None
    ) -> JSONResume:
        """Ingest a resume from various formats."""
        if format_type is None:
            # Auto-detect format based on file extension
            extension = file_path.suffix.lower()
            if extension == ".json":
                format_type = "json"
            elif extension == ".pdf":
                format_type = "pdf"
            else:
                format_type = "text"

        if format_type == "json":
            return self.parse_json_resume(file_path)
        elif format_type == "pdf":
            text = self.parse_pdf_resume(file_path)
            return self.text_to_json_resume(text)
        else:
            # Assume text format
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            return self.text_to_json_resume(text)


# Global service instance
resume_ingestion_service = ResumeIngestionService()
