"""Domain models for recurring defect analysis scaffolding."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TrendClassification(str, Enum):
    """Allowed trend classifications from the user story and schema view."""

    RECURRING_CRITICAL = "Recurring - Critical"
    RECURRING_HIGH_FREQUENCY = "Recurring - High Frequency"
    ISOLATED_INCIDENT = "Isolated Incident"
    INSUFFICIENT_DATA = "Insufficient Data"


@dataclass(frozen=True)
class InspectionEvent:
    """Inspection event input model aligned with operations schema."""

    defect_id: str | None
    severity: str | None
    normalized_lot_id: str
    inspection_timestamp: datetime
    qty_checked: int
    qty_defects: int
    disposition: str | None
    notes: str | None
    inspector_name: str


@dataclass(frozen=True)
class DefectTrendSummary:
    """Summary row for recurring defects list/table view."""

    defect_id: str
    severity: str
    impacted_lot_count: int
    weeks_with_defects: int
    first_detected: datetime
    last_detected: datetime
    total_defects: int
    days_span: int
    trend_classification: TrendClassification


@dataclass(frozen=True)
class DefectDrillDown:
    """Drill-down payload for a single defect code."""

    defect_id: str
    events: list[InspectionEvent]
    insufficient_data_message: str | None
    missing_periods: list[str]
