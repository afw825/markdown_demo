"""Database bootstrap utility.

This module initializes the database by executing schema and seed SQL files.
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import text

from steelworks_defect.config import get_database_url
from steelworks_defect.db import create_db_engine


def _read_sql_file(path: Path) -> str:
    """Read a SQL file as UTF-8 text.

    Time complexity: O(m), where m is file size in bytes.
    Space complexity: O(m).
    """
    return path.read_text(encoding="utf-8")


def initialize_database(project_root: Path) -> None:
    """Execute schema and seed SQL files in one transaction boundary each.

    Resources are properly closed because SQLAlchemy engine connections are
    wrapped in context managers (`engine.begin()`).

    Time complexity: O(s + d), where s and d are SQL script sizes.
    Space complexity: O(s + d) for in-memory SQL text.
    """
    schema_path = project_root / "db" / "schema.sql"
    seed_path = project_root / "db" / "seed.sql"

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    if not seed_path.exists():
        raise FileNotFoundError(f"Seed file not found: {seed_path}")

    engine = create_db_engine(get_database_url())

    schema_sql = _read_sql_file(schema_path)
    seed_sql = _read_sql_file(seed_path)

    # engine.begin() guarantees commit/rollback semantics and closes the
    # underlying connection even when exceptions are raised.
    with engine.begin() as connection:
        connection.execute(text(schema_sql))
    with engine.begin() as connection:
        connection.execute(text(seed_sql))


def main() -> None:
    """CLI entry point for `poetry run init-db`.

    Time complexity: O(s + d).
    Space complexity: O(s + d).
    """
    # Resolve project root by walking up from this source file location.
    project_root = Path(__file__).resolve().parents[2]
    initialize_database(project_root)
    print("Database initialization complete.")
