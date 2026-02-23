"""Analysis component scaffold for recurring defect behavior."""

from __future__ import annotations

from collections import defaultdict

from steelworks_defect.models import (
    DefectDrillDown,
    DefectTrendSummary,
    InspectionEvent,
    TrendClassification,
)


class RecurringDefectAnalyzer:
    """Encapsulates classification logic required by AC1-AC4 and AC9."""

    def classify_defect_trends(
        self, events: list[InspectionEvent]
    ) -> list[DefectTrendSummary]:
        """Build summary rows for the recurring defects list view (AC5)."""
        grouped_events: dict[tuple[str, str], list[InspectionEvent]] = defaultdict(list)

        for event in events:
            if event.qty_defects <= 0:
                continue
            if event.defect_id is None or event.severity is None:
                continue
            grouped_events[(event.defect_id, event.severity)].append(event)

        summaries: list[DefectTrendSummary] = []

        for (defect_id, severity), defect_events in grouped_events.items():
            timestamps = [event.inspection_timestamp for event in defect_events]
            lots = {event.normalized_lot_id for event in defect_events}
            weeks = {
                event.inspection_timestamp.isocalendar()[:2] for event in defect_events
            }

            first_detected = min(timestamps)
            last_detected = max(timestamps)
            days_span = (last_detected - first_detected).days
            total_defects = sum(event.qty_defects for event in defect_events)

            if len(lots) >= 2 and len(weeks) >= 2:
                trend = (
                    TrendClassification.RECURRING_CRITICAL
                    if severity == "Critical"
                    else TrendClassification.RECURRING_HIGH_FREQUENCY
                )
            elif len(lots) == 1:
                trend = TrendClassification.ISOLATED_INCIDENT
            else:
                trend = TrendClassification.INSUFFICIENT_DATA

            summaries.append(
                DefectTrendSummary(
                    defect_id=defect_id,
                    severity=severity,
                    impacted_lot_count=len(lots),
                    weeks_with_defects=len(weeks),
                    first_detected=first_detected,
                    last_detected=last_detected,
                    total_defects=total_defects,
                    days_span=days_span,
                    trend_classification=trend,
                )
            )

        return summaries

    def filter_recurring_defects(
        self, summaries: list[DefectTrendSummary]
    ) -> list[DefectTrendSummary]:
        """Return only recurring rows for recurring-only filter behavior (AC6)."""
        raise NotImplementedError

    def prioritize_defect_trends(
        self, summaries: list[DefectTrendSummary]
    ) -> list[DefectTrendSummary]:
        """Apply default sorting and prioritization required by AC9."""
        raise NotImplementedError

    def build_defect_drilldown(
        self, defect_id: str, events: list[InspectionEvent]
    ) -> DefectDrillDown:
        """Build defect-code detail payload and missing-period messaging (AC7, AC8)."""
        raise NotImplementedError
