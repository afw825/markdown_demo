"""Ingestion component scaffold for loading inspection data."""

from __future__ import annotations

from typing import Protocol

from steelworks_defect.models import InspectionEvent


class InspectionEventGateway(Protocol):
    """Protocol for reading inspection events from a data source."""

    def fetch_inspection_events(self) -> list[InspectionEvent]:
        """Return inspection events required for recurring defect analysis."""
        ...
