import json
from jsonschema import validate, ValidationError


def validate_jsonresume(resume_path: str, schema_path: str) -> bool:
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
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    validate(instance=resume, schema=schema)
    return True


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
