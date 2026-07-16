"""Validation utilities for configuration constraints."""

from typing import Any

from cookie_agent.config.exceptions import ValidationError


def validate_positive(name: str, value: int | float) -> None:
    """Validate a numeric value is strictly positive."""
    if value <= 0:
        raise ValidationError(f"{name} must be > 0, got {value}")


def validate_non_negative(name: str, value: int | float) -> None:
    """Validate a numeric value is non-negative."""
    if value < 0:
        raise ValidationError(f"{name} must be >= 0, got {value}")


def validate_range(
    name: str, value: int | float, min_val: int | float, max_val: int | float
) -> None:
    """Validate a numeric value falls within an inclusive range."""
    if not (min_val <= value <= max_val):
        raise ValidationError(
            f"{name} must be between {min_val} and {max_val}, got {value}"
        )


def validate_non_empty(name: str, value: str) -> None:
    """Validate a string is not empty or whitespace."""
    if not value or not value.strip():
        raise ValidationError(f"{name} cannot be empty or whitespace")


def validate_enum(name: str, value: str, valid_options: list[str]) -> None:
    """Validate a string falls within a discrete set of options."""
    if value not in valid_options:
        raise ValidationError(f"{name} must be one of {valid_options}, got {value}")


def validate_type(name: str, value: Any, expected_type: type) -> None:
    """Validate a value strictly matches an expected Python type."""
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"{name} must be of type {expected_type.__name__}, "
            f"got {type(value).__name__}"
        )
