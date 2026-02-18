# 🏭 SteelWorks - Recurring Defects Analysis Tool

Quality engineering tool for identifying and analyzing defects that appear across multiple manufacturing lots over time.

## Table of Contents

- [Project Description](#project-description)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [How to Run / Build](#how-to-run--build)
- [Usage Examples](#usage-examples)
- [Running Tests](#running-tests)
- [Configuration](#configuration)
- [Key Design Decisions](#key-design-decisions)
- [What to Change for Production](#what-to-change-for-production)

---

## Project Description

### Problem Statement

As a quality engineer, you need to distinguish between:
- **Recurring Issues**: Defects that appear across multiple lots over time
- **One-off Incidents**: Defects that happen in only one lot/time window

This distinction helps prioritize systemic process improvements over isolated corrective actions.

### Solution Overview

This branch currently provides a **scaffold-first implementation** for the recurring defect user story.

Current state:

1. **Scaffolded Architecture**: Domain, ingestion, analysis, presentation, and use-case layers are defined.
2. **Incremental Delivery**: First unit test and related business logic are implemented.
3. **Future-safe Contracts**: Remaining ACs are represented as stubs for controlled step-by-step implementation.

### Key Features (Current Branch Status)

✅ **Implemented Now**
- AC1 core path: recurring defect classification for multi-lot + multi-week in analyzer.
- First unit test passing for AC1 scenario.

🚧 **Scaffolded (Not Implemented Yet)**
- AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9 logic paths.
- Non-first unit tests (stubs only).
- Integration tests (intentionally not added yet).

---

## Architecture

### Layered Architecture (Scaffold)

```
┌─────────────────────────────────────────────┐
│      Presentation Layer                     │
│  - List view and drill-down contracts       │
└─────────────────┬───────────────────────────┘
									│
┌─────────────────▼───────────────────────────┐
│      Analysis Layer                         │
│  - Recurring defect classification rules    │
└─────────────────┬───────────────────────────┘
									│
┌─────────────────▼───────────────────────────┐
│      Ingestion Layer                        │
│  - Inspection event gateway contract        │
└─────────────────┬───────────────────────────┘
									│
┌─────────────────▼───────────────────────────┐
│      Data Layer (Reference SQL)             │
│  - operations schema and seed scripts       │
└─────────────────────────────────────────────┘
```

### Directory Structure (Current)

```
src/
└── steelworks_defect/
		├── __init__.py
		├── models.py
		├── ingestion.py
		├── analysis.py
		├── presentation.py
		└── use_cases.py

tests/
└── unit/
		├── test_recurring_defect_analyzer.py
		├── test_recurring_defect_list_view.py
		└── test_defect_drilldown_view.py

db/
├── schema.sql
├── seed.sql
└── sample_queries.sql

docs/
├── architecture_decision_records.md
├── assumptions_scope.md
├── data_design.md
└── tech_stack_decision_records.md
```

---

## Tech Stack

| Component | Technology | Status |
|-----------|-----------|--------|
| Language | Python | Scaffold + partial implementation |
| Testing | pytest | Unit stubs + first implemented unit test |
| Data Model Reference | PostgreSQL schema (SQL) | Defined in `db/schema.sql` |
| Architecture Source | ADR + Data Design docs | In `docs/` |

> Note: This branch is intentionally scaffold-focused and may not include full runtime/dependency wiring.

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- pytest installed in your environment

### Step 1: Open Project

```bash
cd markdown_demo
```

### Step 2: Ensure pytest is available

```bash
python -m pip install pytest
```

---

## How to Run / Build

This branch does not yet provide a complete runnable app build.

Current executable scope:
- Unit tests (first implemented test and scaffold stubs)

---

## Usage Examples

### Example 1: Validate Implemented AC1 Path

Run only AC1 test:

```bash
python -m pytest tests/unit/test_recurring_defect_analyzer.py -k ac1 -q
```

Expected result:
- `1 passed` for AC1 test.

### Example 2: View Full Current Unit Scaffold Status

```bash
python -m pytest tests/unit -q
```

Expected result:
- First analyzer test passes.
- Remaining tests are skipped (stub markers).

---

## Running Tests

### Run Implemented Test Only

```bash
python -m pytest tests/unit/test_recurring_defect_analyzer.py::test_ac1_definition_of_recurring_multi_lot_multi_week -q
```

### Run Analyzer Test File

```bash
python -m pytest tests/unit/test_recurring_defect_analyzer.py -q
```

### Acceptance Criteria Coverage (Current Branch)

| AC | Status | Evidence |
|----|--------|----------|
| AC1 | ✅ Implemented | `RecurringDefectAnalyzer.classify_defect_trends` + first unit test |
| AC2 | 🚧 Stub only | test stub present |
| AC3 | 🚧 Stub only | test stub present |
| AC4 | 🚧 Stub only | test stub present |
| AC5 | 🚧 Stub only | presenter/list stubs + test stub |
| AC6 | 🚧 Stub only | presenter/filter stubs + test stub |
| AC7 | 🚧 Stub only | drill-down stubs + test stub |
| AC8 | 🚧 Stub only | messaging stubs + test stub |
| AC9 | 🚧 Stub only | prioritization stubs + test stub |

---

## Configuration

Current branch does not require environment variables for scaffold validation.

When runtime/data adapters are implemented later, configuration is expected to include:
- Database connection URL
- Optional UI/runtime toggles

---

## Key Design Decisions

The implementation and scaffolding align to the project documents:

1. **Stateless Modular Monolith**
	 - Separation of ingestion, analysis, and presentation concerns.
2. **Fail-Soft Direction**
	 - Contracts are designed to support indeterminate/incomplete data handling.
3. **User-story-first Incremental Delivery**
	 - Implement one AC path at a time with matching unit tests.

Reference docs:
- `docs/architecture_decision_records.md`
- `docs/assumptions_scope.md`
- `docs/data_design.md`
- `docs/tech_stack_decision_records.md`

---

## What to Change for Production

When progressing from this scaffold branch to production-ready implementation:

1. Implement remaining AC business logic (AC2-AC9).
2. Replace all unit test stubs with real assertions.
3. Add dependency management and reproducible environment config.
4. Add integration tests and CI checks.
5. Add runtime configuration (database, logging, deployment settings).

---

**Last Updated**: February 2026