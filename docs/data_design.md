# Data Design: Operations Data Platform

## Overview
This data model consolidates disparate logs from Production, Quality, and Shipping. 
**Critical Design Note:** Because the source spreadsheets contain inconsistent Lot IDs (e.g., "L0T", "Lot", "LOT_"), this model uses a **`normalized_lot_id`** as the primary key. All incoming data must be cleaned to generate this key before being stored, while preserving the `raw_lot_id` for audit purposes.

## 1. Master Data Entities

### Lot (The Central Anchor)
The single source of truth for a batch of steel. Aggregates data from all three departments.
* **`normalized_lot_id`** (PK, String): The cleaned, standardized ID (e.g., `LOT-20260101-001`).
* **`part_number`** (String): The SKU manufactured (e.g., `SW-9925-C`).
* **`production_date`** (Date): Derived from the earliest log entry.

### Defect_Type (Reference)
Standardized list of possible defects to enable trend analysis.
* **`defect_code`** (PK, String): Short code (e.g., `BURR`, `POR`, `WELD`).
* **`description`** (String): Full readable name (e.g., "Porosity").
* **`severity`** (String): Default severity (Minor, Major, Critical).

### Inspector (Reference)
List of authorized quality control personnel.
* **`inspector_name`** (PK, String): Name as it appears in logs (e.g., "A. Nguyen").
* **`shift_preference`** (String): Optional context (e.g., "Day Shift").

---

## 2. Transactional Entities (The Logs)

### Production_Run
Records the creation of the Lot. Sourced from `Ops_Production_Log`.
* **`run_id`** (PK, Auto-Increment)
* **`normalized_lot_id`** (FK): Links to `Lot`.
* **`raw_lot_id`** (String): Original typo-filled ID from Excel for debugging.
* **`line_id`** (String): Physical line used (e.g., "Line 1").
* **`shift`** (String): Day, Swing, Night.
* **`units_planned`** (Int): Target output.
* **`units_actual`** (Int): Actual output.
* **`downtime_minutes`** (Int): Duration of line stops.
* **`primary_issue`** (String): Reason for downtime (e.g., "Changeover delay").

### Inspection_Event
Records specific quality checks. Sourced from `QE_Inspector_Logs`.
* **`inspection_id`** (PK, Auto-Increment)
* **`normalized_lot_id`** (FK): Links to `Lot`.
* **`inspector_name`** (FK): Links to `Inspector`.
* **`inspection_timestamp`** (DateTime): Date and Time of check.
* **`defect_code`** (FK, Nullable): Links to `Defect_Type`. Null if passed.
* **`qty_checked`** (Int): Sample size.
* **`qty_defects`** (Int): Failures found.
* **`disposition`** (String): Outcome (Pass, Rework, Scrap, MRB).
* **`notes`** (String): Specific context from the inspector.

### Shipment
Records the logistics out the door. Sourced from `Ops_Shipping_Log`.
* **`shipment_id`** (PK, Auto-Increment)
* **`normalized_lot_id`** (FK): Links to `Lot`.
* **`sales_order`** (String): SO Number.
* **`customer`** (String): Client Name.
* **`ship_date`** (Date): Date shipped.
* **`carrier`** (String): Trucking co (e.g., XPO).
* **`bol_number`** (String): Bill of Lading.
* **`qty_shipped`** (Int): Amount in this specific shipment.
* **`ship_status`** (String): e.g., "Shipped", "Held".

---

## 3. Relationships

1.  **Lot 1:1 Production_Run**: A production run defines the lot.
2.  **Lot 1:Many Inspection_Event**: A lot may be inspected multiple times (e.g., initial check + re-check after rework).
3.  **Lot 1:Many Shipment**: A large lot might be split into two shipments, or multiple lots combined onto one truck.
4.  **Inspection_Event > Defect_Type**: Allows reporting on "Which defects are trending?"
5.  **Inspection_Event > Inspector**: Allows reporting on "Who is finding the most defects?"

---

## 4. Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    %% Master Data
    LOT {
        string normalized_lot_id PK
        string part_number
        date production_date
    }
    
    DEFECT_TYPE {
        string defect_code PK
        string description
        string severity
    }

    INSPECTOR {
        string inspector_name PK
    }

    %% Transactions
    PRODUCTION_RUN {
        int run_id PK
        string normalized_lot_id FK
        string raw_lot_id
        string line_id
        int units_actual
        int downtime_minutes
        string primary_issue
    }

    INSPECTION_EVENT {
        int inspection_id PK
        string normalized_lot_id FK
        string inspector_name FK
        string defect_code FK
        datetime inspection_timestamp
        int qty_defects
        string disposition
    }

    SHIPMENT {
        int shipment_id PK
        string normalized_lot_id FK
        string sales_order
        string customer
        string ship_status
        int qty_shipped
    }

    %% Relationship Lines
    LOT ||--|| PRODUCTION_RUN : created_via
    LOT ||--o{ INSPECTION_EVENT : undergoes
    LOT ||--o{ SHIPMENT : contains
    INSPECTOR ||--o{ INSPECTION_EVENT : performs
    DEFECT_TYPE ||--o{ INSPECTION_EVENT : identified_as
