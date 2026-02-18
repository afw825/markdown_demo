"""Recurring defect analysis logic.

This module contains pure-data functions so behavior can be unit-tested without
requiring a database or UI runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


# Ranking used by default sorting (AC9).
_STATUS_PRIORITY = {
    "Recurring - Critical": 0,
    "Recurring - High Frequency": 1,
    "Isolated Incident": 2,
    "Insufficient Data": 3,
}


@dataclass(frozen=True)
class DefectDrillDownResult:
    """Container for drill-down records and explainability metadata.

    Attributes:
        records: Event-level rows for the selected defect.
        message: Human-readable explanation, including missing periods.
        missing_weeks: ISO-like year-week labels absent between min and max week.

    Space complexity: O(k), where k is number of events for one defect.
    """

    records: pd.DataFrame
    message: str
    missing_weeks: list[str]


def _normalize_analysis_frame(events: pd.DataFrame) -> pd.DataFrame:
    """Return a normalized DataFrame with guaranteed required columns.

    Time complexity: O(n), where n is input row count.
    Space complexity: O(n), because a copy is created for safe transformation.
    """
    required_columns = {
        "defect_id",
        "severity",
        "normalized_lot_id",
        "inspection_timestamp",
        "qty_defects",
    }
    missing_columns = required_columns.difference(events.columns)
    if missing_columns:
        missing_str = ", ".join(sorted(missing_columns))
        raise ValueError(f"Input events are missing required columns: {missing_str}")

    frame = events.copy()
    frame["inspection_timestamp"] = pd.to_datetime(frame["inspection_timestamp"], errors="coerce")
    frame["qty_defects"] = pd.to_numeric(frame["qty_defects"], errors="coerce").fillna(0).astype(int)
    frame["defect_id"] = frame["defect_id"].astype("string")
    frame["severity"] = frame["severity"].astype("string")
    frame["normalized_lot_id"] = frame["normalized_lot_id"].astype("string")
    return frame


def _to_year_week_labels(weeks: Iterable[pd.Timestamp]) -> list[str]:
    """Convert week timestamps to deterministic year-week string labels.

    Time complexity: O(w), where w is number of weeks.
    Space complexity: O(w).
    """
    labels: list[str] = []
    for week_start in weeks:
        iso = week_start.isocalendar()
        labels.append(f"{iso.year}-W{iso.week:02d}")
    return labels


def _compute_missing_weeks(timestamps: pd.Series) -> list[str]:
    """Find missing week buckets between first and last observation.

    Time complexity: O(w) where w is number of weeks in the covered range.
    Space complexity: O(w).
    """
    # Remove null timestamps because they cannot be assigned to a calendar week.
    valid_ts = timestamps.dropna()
    if valid_ts.empty:
        return []

    # Normalize to week-start timestamps to compare periods consistently.
    observed_weeks = pd.to_datetime(valid_ts.dt.to_period("W-MON").dt.start_time).drop_duplicates().sort_values()
    # Build complete week range from first to last observed week.
    all_weeks = pd.date_range(start=observed_weeks.iloc[0], end=observed_weeks.iloc[-1], freq="W-MON")
    # Use set difference to identify gaps in temporal coverage.
    missing = [week for week in all_weeks if week not in set(observed_weeks.tolist())]
    return _to_year_week_labels(missing)


def classify_defects(events: pd.DataFrame) -> pd.DataFrame:
    """Classify defects into recurring, isolated, or insufficient-data statuses.

    Acceptance criteria mapping:
      - AC1: recurring requires multi-lot and multi-week evidence.
      - AC2: single-lot defects are isolated, not recurring.
      - AC3: qty_defects == 0 rows are excluded from defect occurrence counts.
      - AC4: incomplete time evidence is labeled "Insufficient Data".
      - AC5: output schema includes required list/table fields.
      - AC9: output is default-sorted with recurring defects prioritized.

    Time complexity: O(n + g log g), where n is event count and g is number of
    grouped defect buckets (sorting dominates on grouped output).
    Space complexity: O(g).
    """
    frame = _normalize_analysis_frame(events)

    # AC3: Exclude non-defect rows from trend counting.
    non_zero = frame[(frame["qty_defects"] > 0) & (frame["defect_id"].notna())]

    # If no qualifying defects exist, return an empty frame with stable columns.
    if non_zero.empty:
        return pd.DataFrame(
            columns=[
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
            ]
        )

    enriched = non_zero.copy()
    # Store week-start buckets for multi-week logic in AC1.
    enriched["week_start"] = pd.to_datetime(
        enriched["inspection_timestamp"].dt.to_period("W-MON").dt.start_time,
        errors="coerce",
    )

    grouped = (
        enriched.groupby(["defect_id", "severity"], dropna=False)
        .agg(
            impacted_lot_count=("normalized_lot_id", "nunique"),
            weeks_with_defects=("week_start", "nunique"),
            first_detected=("inspection_timestamp", "min"),
            last_detected=("inspection_timestamp", "max"),
            total_defects=("qty_defects", "sum"),
        )
        .reset_index()
    )

    # Days span helps distinguish long-running defects from short-lived spikes.
    grouped["days_span"] = (grouped["last_detected"] - grouped["first_detected"]).dt.days

    missing_periods_map: dict[tuple[str, str], list[str]] = {}
    for (defect_id, severity), defect_events in enriched.groupby(["defect_id", "severity"], dropna=False):
        missing_periods_map[(str(defect_id), str(severity))] = _compute_missing_weeks(defect_events["inspection_timestamp"])

    def classify_row(row: pd.Series) -> str:
        """Classify one grouped defect record.

        Time complexity: O(1).
        Space complexity: O(1).
        """
        if pd.isna(row["first_detected"]) or pd.isna(row["last_detected"]):
            return "Insufficient Data"
        if row["impacted_lot_count"] >= 2 and row["weeks_with_defects"] >= 2:
            if str(row["severity"]) == "Critical":
                return "Recurring - Critical"
            return "Recurring - High Frequency"
        if row["impacted_lot_count"] == 1:
            return "Isolated Incident"
        return "Insufficient Data"

    grouped["trend_classification"] = grouped.apply(classify_row, axis=1)
    grouped["missing_periods"] = grouped.apply(
        lambda row: missing_periods_map.get((str(row["defect_id"]), str(row["severity"])), []),
        axis=1,
    )

    # AC4: Mark sparse temporal evidence as insufficient.
    sparse_mask = (grouped["impacted_lot_count"] >= 2) & (grouped["weeks_with_defects"] < 2)
    grouped.loc[sparse_mask, "trend_classification"] = "Insufficient Data"

    # AC9: deterministic default sorting and prioritization.
    grouped["_priority"] = grouped["trend_classification"].map(_STATUS_PRIORITY).fillna(99)
    grouped = grouped.sort_values(
        by=["_priority", "impacted_lot_count", "last_detected", "total_defects"],
        ascending=[True, False, False, False],
        kind="mergesort",
    ).drop(columns=["_priority"])

    return grouped.reset_index(drop=True)


def filter_recurring_only(summary: pd.DataFrame) -> pd.DataFrame:
    """Return only recurring rows for list-view filtering (AC6).

    Time complexity: O(g), where g is grouped row count.
    Space complexity: O(g) in the worst case.
    """
    recurring_values = {"Recurring - Critical", "Recurring - High Frequency"}
    return summary[summary["trend_classification"].isin(recurring_values)].reset_index(drop=True)


def drill_down_defect(events: pd.DataFrame, defect_id: str) -> DefectDrillDownResult:
    """Return event-level details and explainability for one defect code.

    Acceptance criteria mapping:
      - AC7: returns detailed records for the selected defect code.
      - AC8: includes missing-period messaging when week coverage has gaps.

    Time complexity: O(n + k log k), where n is all events and k is selected rows.
    Space complexity: O(k).
    """
    frame = _normalize_analysis_frame(events)
    # AC3 consistency: drill-down view reflects true defect occurrences only.
    filtered = frame[(frame["qty_defects"] > 0) & (frame["defect_id"] == defect_id)].copy()

    if filtered.empty:
        empty_message = (
            "Insufficient data: no defect events with qty_defects > 0 were found "
            f"for defect code {defect_id}."
        )
        return DefectDrillDownResult(records=filtered, message=empty_message, missing_weeks=[])

    filtered = filtered.sort_values(by=["inspection_timestamp", "normalized_lot_id"], ascending=[False, True]).reset_index(drop=True)
    missing_weeks = _compute_missing_weeks(filtered["inspection_timestamp"])

    distinct_lots = int(filtered["normalized_lot_id"].nunique())
    distinct_weeks = int(filtered["inspection_timestamp"].dt.to_period("W-MON").nunique())

    if distinct_lots < 2 or distinct_weeks < 2:
        message = (
            "Insufficient data: recurring classification requires at least 2 lots "
            "and 2 weeks with non-zero defects."
        )
    elif missing_weeks:
        joined = ", ".join(missing_weeks)
        message = f"Recurring signal detected with missing periods: {joined}."
    else:
        message = "Recurring signal detected with continuous weekly coverage in observed range."

    return DefectDrillDownResult(records=filtered, message=message, missing_weeks=missing_weeks)
