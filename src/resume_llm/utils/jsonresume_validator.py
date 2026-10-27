import json
from functools import cache
from pathlib import Path
from typing import Any

from jsonschema import ValidationError, validate

# Repo root is three levels above src/resume_llm/utils/
SCHEMA_PATH = (
    Path(__file__).resolve().parents[3] / "data" / "schema" / "jsonresume-schema.json"
)


@cache
def load_schema(schema_path: str = str(SCHEMA_PATH)) -> dict[str, Any]:
    """
    Loads and caches a JSON schema file.
    Args:
        schema_path (str): Path to the JSON schema file.
    Returns:
        dict: The parsed schema.
    """
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_resume(
    resume: dict[str, Any], schema_path: str = str(SCHEMA_PATH)
) -> bool:
    """
    Validates a JSON resume dict against the JSON Resume schema.
    Args:
        resume (dict): The parsed JSON resume.
        schema_path (str): Path to the JSON schema file.
    Returns:
        bool: True if valid, raises ValidationError if invalid.
    """
    validate(instance=resume, schema=load_schema(schema_path))
    return True


def validate_jsonresume(resume_path: str, schema_path: str = str(SCHEMA_PATH)) -> bool:
    """
    Validates a JSON resume file against the JSON Resume schema.
    Args:
        resume_path (str): Path to the JSON resume file.
        schema_path (str): Path to the JSON schema file.
    Returns:
        bool: True if valid, raises ValidationError if invalid.
    """
    with open(resume_path, "r", encoding="utf-8") as f:
        resume = json.load(f)
    return validate_resume(resume, schema_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python jsonresume_validator.py <resume.json> <schema.json>")
        sys.exit(1)
    try:
        validate_jsonresume(sys.argv[1], sys.argv[2])
        print("Validation successful: Resume is valid.")
    except ValidationError as e:
        print(f"Validation failed: {e.message}")
        sys.exit(2)
