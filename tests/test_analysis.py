"""Tests for recurring defect analysis acceptance criteria.

Each test name references one or more AC IDs from the user story.
"""

from __future__ import annotations

import pandas as pd

from steelworks_defect.analysis import classify_defects, drill_down_defect, filter_recurring_only


def _build_events() -> pd.DataFrame:
    """Create synthetic but schema-shaped events for deterministic tests.

    Time complexity: O(n), where n is number of literal rows.
    Space complexity: O(n).
    """
    return pd.DataFrame(
        [
            {
                "defect_id": "WELD",
                "severity": "Critical",
                "normalized_lot_id": "LOT-1",
                "inspection_timestamp": "2026-01-01 08:00:00",
                "qty_checked": 20,
                "qty_defects": 3,
                "disposition": "Rework",
                "notes": "Weld bead issue",
                "inspector_name": "M. Patel",
            },
            {
                "defect_id": "WELD",
                "severity": "Critical",
                "normalized_lot_id": "LOT-2",
                "inspection_timestamp": "2026-01-15 09:00:00",
                "qty_checked": 25,
                "qty_defects": 2,
                "disposition": "Hold for MRB",
                "notes": "Weld bead issue",
                "inspector_name": "M. Patel",
            },
            {
                "defect_id": "BURR",
                "severity": "Major",
                "normalized_lot_id": "LOT-3",
                "inspection_timestamp": "2026-01-08 07:30:00",
                "qty_checked": 30,
                "qty_defects": 1,
                "disposition": "Use-as-is",
                "notes": "Excess burr",
                "inspector_name": "A. Nguyen",
            },
            {
                "defect_id": "CRACK",
                "severity": "Major",
                "normalized_lot_id": "LOT-4",
                "inspection_timestamp": "2026-01-08 10:00:00",
                "qty_checked": 25,
                "qty_defects": 2,
                "disposition": "Rework",
                "notes": "Surface crack",
                "inspector_name": "A. Nguyen",
            },
            {
                "defect_id": "CRACK",
                "severity": "Major",
                "normalized_lot_id": "LOT-5",
                "inspection_timestamp": "2026-01-09 10:00:00",
                "qty_checked": 25,
                "qty_defects": 4,
                "disposition": "Scrap",
                "notes": "Surface crack",
                "inspector_name": "M. Patel",
            },
            {
                "defect_id": "POR",
                "severity": "Minor",
                "normalized_lot_id": "LOT-6",
                "inspection_timestamp": "2026-01-12 10:00:00",
                "qty_checked": 25,
                "qty_defects": 0,
                "disposition": "",
                "notes": "",
                "inspector_name": "A. Nguyen",
            },
        ]
    )


def test_ac1_ac2_ac3_ac4_classification_logic() -> None:
    """AC1/AC2/AC3/AC4: validate recurring vs isolated vs insufficient behavior."""
    summary = classify_defects(_build_events())

    weld = summary[summary["defect_id"] == "WELD"].iloc[0]
    # AC1: WELD appears in multiple lots and weeks, so it is recurring.
    assert weld["trend_classification"] == "Recurring - Critical"

    burr = summary[summary["defect_id"] == "BURR"].iloc[0]
    # AC2: BURR appears in one lot only, so it is isolated.
    assert burr["trend_classification"] == "Isolated Incident"

    crack = summary[summary["defect_id"] == "CRACK"].iloc[0]
    # AC4: CRACK appears in multiple lots but only one week, so insufficient.
    assert crack["trend_classification"] == "Insufficient Data"

    # AC3: POR has zero defects only; it must not appear in grouped output.
    assert "POR" not in summary["defect_id"].tolist()


def test_ac5_output_contains_required_fields() -> None:
    """AC5: list view output includes required columns."""
    summary = classify_defects(_build_events())
    required = {
        "defect_id",
        "severity",
        "impacted_lot_count",
        "weeks_with_defects",
        "first_detected",
        "last_detected",
        "total_defects",
        "days_span",
        "trend_classification",
        "missing_periods",
    }
    assert required.issubset(set(summary.columns))


def test_ac6_filter_recurring_defects() -> None:
    """AC6: recurring-only filter returns recurring classes only."""
    summary = classify_defects(_build_events())
    recurring = filter_recurring_only(summary)
    assert not recurring.empty
    assert set(recurring["trend_classification"].unique()) <= {
        "Recurring - Critical",
        "Recurring - High Frequency",
    }


def test_ac7_ac8_drill_down_with_missing_period_message() -> None:
    """AC7/AC8: drill-down returns detail rows and missing period explainability."""
    events = _build_events()
    detail = drill_down_defect(events, "WELD")
    # AC7: detail records are returned for selected defect code.
    assert len(detail.records) == 2
    assert all(detail.records["defect_id"] == "WELD")
    # AC8: week gap should be surfaced in message and explicit week list.
    assert detail.missing_weeks
    assert "missing periods" in detail.message.lower()


def test_ac9_default_sorting_prioritizes_recurring() -> None:
    """AC9: recurring defects are sorted ahead of isolated/insufficient rows."""
    summary = classify_defects(_build_events())
    # First row should be recurring due to explicit status priority ranking.
    assert summary.iloc[0]["trend_classification"] in {
        "Recurring - Critical",
        "Recurring - High Frequency",
    }
