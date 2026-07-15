"""Unit tests for the cookie_agent package version."""

import cookie_agent


def test_version() -> None:
    """Verify the package version is correctly exposed and formatted."""
    assert cookie_agent.__version__ == "1.0.0"
