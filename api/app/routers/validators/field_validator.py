from fastapi import HTTPException, status

from app.utility import unicode_tool


def strip_and_validate_field_length(
    field_value: str,
    max_length: int,
    error_message: str,
) -> str:
    """
    Validate field length and return stripped value.

    Args:
        field_value: The field value to validate
        max_length: Maximum allowed length in half-width characters
        error_message: Error message to use if validation fails

    Returns:
        Stripped field value

    Raises:
        HTTPException: If field length exceeds maximum
    """
    stripped_value = field_value.strip()
    if unicode_tool.count_full_width_and_half_width_characters(stripped_value) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )
    return stripped_value
