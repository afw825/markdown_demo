"""Unit test stubs for recurring defect analyzer acceptance criteria."""

from datetime import datetime
from pathlib import Path
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from steelworks_defect.analysis import RecurringDefectAnalyzer
from steelworks_defect.models import InspectionEvent, TrendClassification


def test_ac1_definition_of_recurring_multi_lot_multi_week() -> None:
    analyzer = RecurringDefectAnalyzer()

    events = [
        InspectionEvent(
            defect_id="WELD",
            severity="Critical",
            normalized_lot_id="LOT-20260101-001",
            inspection_timestamp=datetime(2026, 1, 1, 8, 0, 0),
            qty_checked=20,
            qty_defects=2,
            disposition="Rework",
            notes="Weld bead issue",
            inspector_name="M. Patel",
        ),
        InspectionEvent(
            defect_id="WELD",
            severity="Critical",
            normalized_lot_id="LOT-20260115-001",
            inspection_timestamp=datetime(2026, 1, 15, 9, 0, 0),
            qty_checked=25,
            qty_defects=1,
            disposition="Hold for MRB",
            notes="Repeat weld issue",
            inspector_name="M. Patel",
        ),
    ]

    summaries = analyzer.classify_defect_trends(events)

    assert len(summaries) == 1
    assert summaries[0].defect_id == "WELD"
    assert summaries[0].impacted_lot_count == 2
    assert summaries[0].weeks_with_defects >= 2
    assert summaries[0].trend_classification == TrendClassification.RECURRING_CRITICAL


def test_ac2_single_lot_not_recurring() -> None:
    pytest.skip("Stub only: implement analyzer unit test for AC2.")


def test_ac3_exclude_zero_qty_defects() -> None:
    pytest.skip("Stub only: implement analyzer unit test for AC3.")


def test_ac4_incomplete_data_marked_insufficient() -> None:
    pytest.skip("Stub only: implement analyzer unit test for AC4.")


def test_ac9_default_sorting_prioritization() -> None:
    pytest.skip("Stub only: implement analyzer unit test for AC9.")
