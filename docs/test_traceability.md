# Test Traceability Matrix (AC Coverage)

This matrix documents which automated tests verify each acceptance criterion.

| Acceptance Criterion | Test(s) Covering AC | Coverage Notes |
|---|---|---|
| AC1: recurring = multi-lot + multi-week | `test_ac1_ac2_ac3_ac4_classification_logic` | Verifies `WELD` is recurring only when both thresholds are met. |
| AC2: single-lot defects are not recurring | `test_ac1_ac2_ac3_ac4_classification_logic` | Verifies `BURR` is classified as `Isolated Incident`. |
| AC3: exclude `qty_defects = 0` | `test_ac1_ac2_ac3_ac4_classification_logic` | Verifies `POR` is excluded from grouped defect output. |
| AC4: incomplete data => insufficient status | `test_ac1_ac2_ac3_ac4_classification_logic` | Verifies multi-lot, single-week `CRACK` is `Insufficient Data`. |
| AC5: list/table with required fields | `test_ac5_output_contains_required_fields` | Verifies output schema fields consumed by list view. |
| AC6: highlight + recurring filter | `test_ac6_filter_recurring_defects` | Verifies recurring-only filtering logic. Highlighting is implemented in UI helper `_highlight_recurring`. |
| AC7: drill-down by defect code | `test_ac7_ac8_drill_down_with_missing_period_message` | Verifies defect-specific event detail rows are returned. |
| AC8: insufficient/missing periods messaging | `test_ac7_ac8_drill_down_with_missing_period_message` | Verifies missing-week explainability appears in drill-down message. |
| AC9: default sorting/prioritization | `test_ac9_default_sorting_prioritizes_recurring` | Verifies recurring classes are sorted to the top. |

All ACs are covered by at least one automated test.
