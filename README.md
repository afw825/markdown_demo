# Steelworks Recurring Defect Analysis

This project implements a quality-engineering dashboard that detects whether the same defect type appears across multiple lots over time, helping distinguish recurring issues from one-off incidents.

## Implemented Scope

- **Recurring classification logic** (multi-lot + multi-week).
- **List/table view** with prioritized sorting and recurring filter behavior.
- **Drill-down by defect code** with explainability messaging for missing periods.
- **Postgres-backed data access** using the schema in [db/schema.sql](db/schema.sql).
- **Seed dataset** in [db/seed.sql](db/seed.sql) aligned to your sample spreadsheets.

## Tech Stack

- Python 3.11+
- Streamlit
- SQLAlchemy + Psycopg (Postgres)
- Pandas
- Pytest
- **Poetry** (dependency management + virtualenv + scripts)

See architecture/design decisions in:
- [docs/architecture_decision_records.md](docs/architecture_decision_records.md)
- [docs/assumptions_scope.md](docs/assumptions_scope.md)
- [docs/data_design.md](docs/data_design.md)
- [docs/tech_stack_decision_records.md](docs/tech_stack_decision_records.md)

## Project Structure

- [src/steelworks_defect/config.py](src/steelworks_defect/config.py): environment-driven runtime configuration.
- [src/steelworks_defect/db.py](src/steelworks_defect/db.py): DB engine and query access.
- [src/steelworks_defect/analysis.py](src/steelworks_defect/analysis.py): classification, filtering, drill-down logic.
- [src/steelworks_defect/app.py](src/steelworks_defect/app.py): Streamlit user interface.
- [src/steelworks_defect/bootstrap.py](src/steelworks_defect/bootstrap.py): initialize schema + seed data.
- [tests/test_analysis.py](tests/test_analysis.py): automated AC coverage tests.
- [docs/test_traceability.md](docs/test_traceability.md): AC-to-test mapping.

## Setup (Poetry)

1. Install Poetry.
2. Install dependencies:

```bash
poetry install
```

3. Configure environment variables (PowerShell example):

```powershell
$env:DATABASE_URL = "postgresql+psycopg://localhost:5432/steelworks"
$env:SHOW_RECURRING_ONLY = "true"
```

4. Initialize DB schema + seed data:

```bash
poetry run init-db
```

5. Run app:

```bash
poetry run streamlit run src/steelworks_defect/app.py
```

## Tests

Run test suite:

```bash
poetry run pytest
```

Detailed AC coverage matrix:
- [docs/test_traceability.md](docs/test_traceability.md)

## Acceptance Criteria Coverage Summary

- **AC1, AC2, AC3, AC4**: implemented in classification logic and validated by tests.
- **AC5**: implemented via list/table output fields from `classify_defects`.
- **AC6**: implemented via recurring-only filter and recurring row highlight in UI.
- **AC7**: implemented via defect-specific drill-down selector and detail table.
- **AC8**: implemented via missing-periods message in drill-down results.
- **AC9**: implemented via default priority sorting (recurring first).

## Developer Notes for Junior Engineers

- Each Python module and function includes explanatory docstrings.
- Non-trivial logic paths include inline comments and Big-O notes.
- Database connections are managed with context managers to avoid leaks.

## What You Must Change Before Production Use

- `pyproject.toml` author metadata:
	- Replace `Your Name <you@example.com>`.
- `DATABASE_URL` environment variable:
	- Set to your real Postgres host/port/database/user/password.
- Optional `SHOW_RECURRING_ONLY` environment variable:
	- Set UI default for recurring-only filter.

No API keys are required by this implementation.