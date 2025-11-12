from fastapi import HTTPException

from app.utility import unicode_tool


def validate_field_length(
    field_value: str,
    max_length: int,
    error_exception: HTTPException,
) -> str:
    """
    Validate field length and return stripped value.

    Args:
        field_value: The field value to validate
        max_length: Maximum allowed length in half-width characters
        error_exception: HTTPException to raise if validation fails

    Returns:
        Stripped field value

    Raises:
        HTTPException: If field length exceeds maximum
    """
    stripped_value = field_value.strip()
    if unicode_tool.count_full_width_and_half_width_characters(stripped_value) > max_length:
        raise error_exception
    return stripped_value
