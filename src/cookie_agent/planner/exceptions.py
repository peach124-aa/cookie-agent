"""Exceptions for the Action Planner module."""


class PlannerError(Exception):
    """Base exception for planner errors."""


class MappingError(PlannerError):
    """Raised when an intent cannot be mapped to a known device sequence."""
