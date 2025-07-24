import pytest
from jsonschema import ValidationError
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from resume_llm.utils.jsonresume_validator import validate_jsonresume


def test_valid_resume():
    resume_path = os.path.join("dummy_data", "resumes", "sample-jsonresume.json")
    schema_path = os.path.join("data", "schema", "jsonresume-schema.json")
    assert validate_jsonresume(resume_path, schema_path) is True


def test_invalid_resume(tmp_path):
    # Create an invalid resume (invalid date format in work.startDate)
    invalid_resume = tmp_path / "invalid.json"
    invalid_resume.write_text(
        """{
        "basics": {"name": "Test"},
        "work": [
            {
                "name": "Test Company",
                "startDate": "01-2013"
            }
        ]
    }""",
        encoding="utf-8",
    )
    schema_path = os.path.join("data", "schema", "jsonresume-schema.json")
    with pytest.raises(ValidationError):
        validate_jsonresume(str(invalid_resume), schema_path)
