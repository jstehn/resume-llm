# JSON Resume Validation Guide

This document describes the JSON Resume validation and data quality features implemented in the Resume LLM system.

## Overview

The Resume LLM system ensures strict compliance with the [JSON Resume standard](https://jsonresume.org/) through comprehensive validation and automatic data cleaning.

## Features

### 1. Schema Validation

- **Official Schema**: Uses the official JSON Resume schema for validation
- **Comprehensive Checks**: Validates data types, formats, and structure
- **Error Reporting**: Provides detailed error messages with field paths
- **Required Fields**: Ensures minimum required fields are present

### 2. Null Value Removal

- **Automatic Cleaning**: Recursively removes null values from resume data
- **Structure Preservation**: Maintains valid data while removing nulls
- **Schema Compliance**: Prevents validation errors caused by null values
- **Deep Cleaning**: Handles nested objects and arrays

### 3. JSON Extraction

- **Pattern Matching**: Extracts JSON Resume from LLM text responses
- **Code Block Detection**: Recognizes ```json code blocks
- **Standalone JSON**: Finds JSON objects in plain text
- **Resume Identification**: Validates extracted JSON contains resume structure

## Usage

### Command Line

```bash
# Validate a JSON Resume file
resume-llm validate my_resume.json

# Optimize with automatic validation
resume-llm optimize resume.json job_description.txt -o optimized.json
```

### Python API

```python
from resume_llm.utils.json_resume_validator import JSONResumeValidator
from resume_llm.utils.json_extractor import remove_null_values, save_json_resume_from_response

# Initialize validator
validator = JSONResumeValidator()

# Validate resume data
is_valid, errors = validator.validate(resume_data)
if not is_valid:
    for error in errors:
        print(f"Error: {error}")

# Remove null values
cleaned_data = remove_null_values(resume_data)

# Extract and save from LLM response
success = save_json_resume_from_response(llm_response, "output.json")
```

## Schema Details

### Required Fields
- `basics.name` (minimum requirement)

### Optional Sections
- `basics` - Personal information and contact details
- `work` - Professional experience
- `volunteer` - Volunteer experience
- `education` - Educational background
- `awards` - Awards and recognition
- `certificates` - Professional certifications
- `publications` - Published works
- `skills` - Technical and soft skills
- `languages` - Language proficiencies
- `interests` - Personal interests
- `references` - Professional references
- `projects` - Personal or professional projects
- `meta` - Schema metadata

### Date Format
- ISO 8601 format with flexibility: `YYYY-MM-DD`, `YYYY-MM`, or `YYYY`

## Data Processing Pipeline

1. **LLM Response** → Raw text with JSON Resume
2. **JSON Extraction** → Pure JSON Resume object
3. **Null Removal** → Clean data without null values
4. **Schema Validation** → Verify compliance
5. **File Output** → Save validated resume

## Error Types

### Validation Errors
- Missing required fields
- Invalid data types
- Malformed URLs or emails
- Incorrect date formats

### Extraction Errors
- No JSON found in response
- Invalid JSON syntax
- Missing resume structure (no `basics` section)

## Best Practices

1. **Always validate** resumes before using them
2. **Use the CLI** for quick validation checks
3. **Handle errors gracefully** in your applications
4. **Keep schema files updated** with latest JSON Resume standard
5. **Test with sample data** before production use

## Troubleshooting

### Common Issues

**Q: Validation fails with null value errors**
A: The system automatically removes null values, but if validation still fails, check for missing required fields.

**Q: JSON extraction fails**
A: Ensure the LLM response contains valid JSON. Try different prompt configurations.

**Q: Schema not found**
A: Verify the schema file exists at `src/resume_llm/config/jsonresume_schema.json`

### Debug Mode

```python
# Get detailed validation information
validator = JSONResumeValidator()
schema_dict = validator.get_schema_dict()
print(f"Schema loaded: {len(schema_dict)} properties")

# Check schema path
print(f"Schema path: {validator.get_schema_path()}")
```

## Integration Examples

### FastAPI Endpoint
```python
@app.post("/validate-resume")
async def validate_resume(resume: dict):
    validator = JSONResumeValidator()
    is_valid, errors = validator.validate(resume)
    return {"valid": is_valid, "errors": errors}
```

### CLI Integration
```python
from resume_llm.utils.json_resume_validator import json_resume_validator

# Use global validator instance
is_valid, errors = json_resume_validator.validate(resume_data)
```

## Contributing

When adding new validation features:

1. Update the schema file if needed
2. Add corresponding tests
3. Update documentation
4. Ensure backward compatibility
5. Test with sample resumes

## Related Files

- `src/resume_llm/utils/json_resume_validator.py` - Main validation logic
- `src/resume_llm/utils/json_extractor.py` - JSON extraction and cleaning
- `src/resume_llm/config/jsonresume_schema.json` - JSON Resume schema
- `tests/` - Validation tests
