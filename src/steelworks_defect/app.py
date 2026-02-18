"""Streamlit dashboard for recurring defect analysis.

Run with:
    poetry run streamlit run src/steelworks_defect/app.py
"""

from __future__ import annotations

import streamlit as st

from steelworks_defect.analysis import classify_defects, drill_down_defect, filter_recurring_only
from steelworks_defect.config import get_database_url, get_default_recurring_filter
from steelworks_defect.db import create_db_engine, fetch_inspection_events


def _render_header() -> None:
    """Render the dashboard title and context.

    Time complexity: O(1).
    Space complexity: O(1).
    """
    st.title("Recurring Defect Analysis")
    st.caption(
        "Classifies defect trends across lots and weeks to distinguish recurring "
        "quality issues from isolated incidents."
    )


def _highlight_recurring(row: dict) -> list[str]:
    """Apply visual highlighting for recurring defects (AC6).

    Time complexity: O(1).
    Space complexity: O(1).
    """
    classification = row.get("trend_classification", "")
    if classification in {"Recurring - Critical", "Recurring - High Frequency"}:
        return ["background-color: rgba(255, 215, 0, 0.25)"] * len(row)
    return [""] * len(row)


def main() -> None:
    """Entry point for dashboard execution.

    Time complexity: O(n + g log g) dominated by classification in analysis.
    Space complexity: O(n + g).
    """
    _render_header()

    # Build engine once per rerun; Streamlit reruns script on interaction.
    database_url = get_database_url()
    engine = create_db_engine(database_url)

    # Close DB resources promptly after loading data by using helper function
    # that internally employs context-managed connections.
    events = fetch_inspection_events(engine)
    summary = classify_defects(events)

    # AC6: User control to filter recurring defects in list view.
    recurring_only = st.checkbox("Show recurring defects only", value=get_default_recurring_filter())
    visible = filter_recurring_only(summary) if recurring_only else summary

    st.subheader("Defect Trend List")
    st.dataframe(
        visible.style.apply(_highlight_recurring, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Drill-down by Defect Code")
    available_defects = sorted([value for value in summary["defect_id"].dropna().astype(str).unique().tolist()])
    selected_defect = st.selectbox("Defect code", options=available_defects)

    if selected_defect:
        detail = drill_down_defect(events, selected_defect)
        st.info(detail.message)
        st.dataframe(detail.records, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
