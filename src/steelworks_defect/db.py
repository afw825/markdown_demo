"""Database access helpers.

The functions in this module isolate SQL details from analysis and UI code,
making the project easier to test and reason about.
"""

from __future__ import annotations

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def create_db_engine(database_url: str) -> Engine:
    """Create a SQLAlchemy engine.

    Time complexity: O(1) for object construction.
    Space complexity: O(1).
    """
    # pool_pre_ping helps detect stale connections proactively.
    return create_engine(database_url, pool_pre_ping=True)


def fetch_inspection_events(engine: Engine) -> pd.DataFrame:
    """Fetch normalized inspection-event records for analysis.

    The query intentionally uses LEFT JOIN for defect_type because defect-free
    inspections may contain NULL defect references.

    Time complexity: O(n) where n is number of inspection rows returned.
    Space complexity: O(n) for the resulting DataFrame.
    """
    query = text(
        """
        SELECT
            dt.defect_id,
            dt.severity,
            l.normalized_lot_id,
            ie.inspection_timestamp,
            ie.qty_checked,
            ie.qty_defects,
            ie.disposition,
            ie.notes,
            i.inspector_name
        FROM operations.inspection_event ie
        JOIN operations.lot l ON l.id = ie.lot_id
        JOIN operations.inspector i ON i.id = ie.inspector_id
        LEFT JOIN operations.defect_type dt ON dt.id = ie.defect_type_id
        """
    )

    # The context manager guarantees the DB connection is closed promptly,
    # preventing leaked connections in long-running UI sessions.
    with engine.connect() as connection:
        frame = pd.read_sql_query(query, connection)

    # Parse timestamps once so all downstream logic can rely on datetime dtype.
    frame["inspection_timestamp"] = pd.to_datetime(frame["inspection_timestamp"], errors="coerce")
    # Enforce numeric defects to prevent string comparisons during filtering.
    frame["qty_defects"] = pd.to_numeric(frame["qty_defects"], errors="coerce").fillna(0).astype(int)
    return frame
