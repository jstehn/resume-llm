"""Utility to extract JSON Resume from agent responses."""

import json
import re
from typing import Any, Dict, Optional


def remove_null_values(data: Any) -> Any:
    """
    Recursively remove null values from a dictionary or list.

    Args:
        data: The data structure to clean (dict, list, or any value)

    Returns:
        The cleaned data structure with null values removed
    """
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            cleaned_value = remove_null_values(value)
            # Only include non-null values
            if cleaned_value is not None:
                cleaned[key] = cleaned_value
        return cleaned
    elif isinstance(data, list):
        cleaned = []
        for item in data:
            cleaned_item = remove_null_values(item)
            # Only include non-null items
            if cleaned_item is not None:
                cleaned.append(cleaned_item)
        return cleaned
    else:
        # Return the value as-is if it's not null, otherwise return None
        return data if data is not None else None


def extract_json_from_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON Resume from agent response text.

    Args:
        response_text: The full response text from the agent

    Returns:
        Dictionary containing the JSON Resume, or None if not found
    """
    # Look for JSON code blocks
    json_pattern = r"```json\s*(\{.*?\})\s*```"
    matches = re.findall(json_pattern, response_text, re.DOTALL)

    if matches:
        try:
            # Try to parse the first JSON match
            json_data = json.loads(matches[0])
            return json_data
        except json.JSONDecodeError:
            pass

    # Try to find standalone JSON (without code blocks)
    # Look for patterns that start with { and end with }
    standalone_pattern = r"(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})"
    matches = re.findall(standalone_pattern, response_text, re.DOTALL)

    for match in matches:
        try:
            json_data = json.loads(match)
            # Check if it looks like a resume (has basics section)
            if isinstance(json_data, dict) and "basics" in json_data:
                return json_data
        except json.JSONDecodeError:
            continue

    return None


def save_json_resume_from_response(response_text: str, output_path: str) -> bool:
    """
    Extract and save JSON Resume from agent response.

    Args:
        response_text: The full response text from the agent
        output_path: Path to save the JSON Resume

    Returns:
        True if successful, False otherwise
    """
    json_data = extract_json_from_response(response_text)

    if json_data:
        try:
            # Remove null values before saving
            cleaned_data = remove_null_values(json_data)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
            return True
        except (OSError, IOError) as e:
            print(f"Error saving JSON Resume: {e}")
            return False

    return False
