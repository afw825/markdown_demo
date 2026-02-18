"""Runtime configuration for the recurring-defect analysis project.

This module centralizes environment-variable access to avoid scattering config
lookups across the codebase.
"""

from __future__ import annotations

import os


# DATABASE_URL controls the SQLAlchemy connection string.
# Default points to a local Postgres instance for developer convenience.
DEFAULT_DATABASE_URL = "postgresql+psycopg://localhost:5432/steelworks"


def get_database_url() -> str:
    """Return the SQLAlchemy database URL.

    Time complexity: O(1) because environment variable lookup is constant time.
    Space complexity: O(1) because only one small string is returned.
    """
    # Pull from environment first so deployment can override local defaults.
    database_url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    # Trim whitespace to avoid subtle connection-string parsing failures.
    return database_url.strip()


def get_default_recurring_filter() -> bool:
    """Return whether the UI should show recurring defects only by default.

    Time complexity: O(1).
    Space complexity: O(1).
    """
    # Expected values are true-ish strings commonly used in environment files.
    raw_value = os.getenv("SHOW_RECURRING_ONLY", "true").strip().lower()
    # Convert to boolean while staying permissive for common variants.
    return raw_value in {"1", "true", "yes", "on"}
