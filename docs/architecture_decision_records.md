# Architecture Decision Records (ADR)

This document records the architectural design choices for the Defect Trend Analysis project. These decisions prioritize system resilience and analytical accuracy over infrastructure complexity.

---

## ADR 001: Use of a Stateless Modular Monolith
**Status:** Accepted

**Context:**
The system must analyze legacy data exports that are non-uniform. The project scope excludes real-time monitoring and complex user access controls. We require a design that is easily portable and does not rely on a persistent external server environment to function.

**Decision:**
We will implement a **Stateless Modular Monolith**. 
* **Stateless:** The application will not persist data internally. It will re-process the external "Source of Truth" upon every session initialization or refresh.
* **Modular:** Code logic will be strictly partitioned into `Ingestion`, `Analysis Logic`, and `Presentation` components to allow for independent updates to the logic without affecting the data handling.

**Alternatives Considered:**
* **Microservices:** Rejected as the overhead of inter-service communication adds unnecessary complexity for a localized analysis tool.
* **Persistent Database (Stateful):** Rejected to eliminate the risk of "Data Drift," ensuring the tool always reflects the current state of the manual file exports.

**Consequences:**
* **Positive:** Zero database maintenance; simplified deployment; ensures the "Source of Truth" remains external and authoritative.
* **Negative:** Processing time scales linearly with the volume of history logs, as data is re-calculated on every launch.

---

## ADR 002: External File-Based "Source of Truth"
**Status:** Accepted

**Context:**
The legacy ERP system provides data via manual exports. There is no viable path for a direct live connection to the ERP backend. The architecture must accommodate files as the primary data input.

**Decision:**
The architecture will treat the file directory as a **Virtual Database**. All relational mapping between disparate logs will be handled in-memory at runtime rather than through a pre-defined database schema.

**Alternatives Considered:**
* **Intermediary Database:** Rejected; creating a middle-man database adds a failure point and requires a synchronization strategy that the current scope does not support.

**Consequences:**
* **Positive:** Leverages existing business workflows; eliminates the need for IT-managed database credentials.
* **Negative:** The system's relational integrity is vulnerable to manual file deletions or significant naming changes in the source directory.

---

## ADR 003: Unidirectional Batch Processing Model
**Status:** Accepted

**Context:**
To distinguish "recurring" defects from "one-off" incidents, the system must evaluate individual records against the entire historical dataset. This requires a holistic view of data rather than an incremental or stream-based approach.

**Decision:**
We will utilize a **Batch Interaction Model**. Data flows in one direction: from the raw source through a centralized analysis engine to the presentation layer. No data is written back to the source files.



**Alternatives Considered:**
* **Event-Driven/Stream Processing:** Rejected; the "Source of Truth" is updated in daily/weekly chunks (exports), making a real-time event model incompatible with the data arrival rate.

**Consequences:**
* **Positive:** High accuracy in pattern recognition; simpler logic for calculating multi-lot trends.
* **Negative:** The system is "static" between refreshes and cannot provide active feedback during the user's data entry process.

---

## ADR 004: Fail-Soft Data Integrity Policy
**Status:** Accepted

**Context:**
Per project assumptions, `Lot_ID` formats and column headers may vary slightly. A "Fail-Fast" approach (crashing on error) would render the tool unusable given the expected variance in legacy data.

**Decision:**
Implement a **Fail-Soft Logic**. The architecture will include an "Indeterminate" state for records that do not meet mapping criteria. These records are caught and flagged rather than allowing them to break the processing pipeline.



**Alternatives Considered:**
* **Strict Schema Validation:** Rejected; the lack of control over the source ERP export formatting makes strict validation a barrier to system utility.

**Consequences:**
* **Positive:** Robustness against "messy" data; allows the user to see partial results even if some files are poorly formatted.
* **Negative:** The Analysis engine must include additional logic to track and report "Indeterminate" counts to the user to avoid silent data loss.
