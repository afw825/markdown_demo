"""Presentation component scaffold for recurring defect user interactions."""

from __future__ import annotations

from steelworks_defect.models import DefectDrillDown, DefectTrendSummary


class RecurringDefectListPresenter:
    """List/table presentation contract for AC5, AC6, and AC9."""

    def render_list_view(self, summaries: list[DefectTrendSummary]) -> None:
        """Render required list/table fields for defect trends (AC5)."""
        raise NotImplementedError

    def apply_recurring_highlight(self, summaries: list[DefectTrendSummary]) -> None:
        """Apply visual highlighting for recurring defects (AC6)."""
        raise NotImplementedError

    def apply_recurring_filter(
        self,
        summaries: list[DefectTrendSummary],
        recurring_only: bool,
    ) -> list[DefectTrendSummary]:
        """Filter list view to recurring-only rows when requested (AC6)."""
        raise NotImplementedError


class DefectDrillDownPresenter:
    """Drill-down presentation contract for AC7 and AC8."""

    def render_drilldown_view(self, drilldown: DefectDrillDown) -> None:
        """Render defect-specific detail rows and explainability messaging."""
        raise NotImplementedError
