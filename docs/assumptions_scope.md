## 📋 Project Definition: Scope & Assumptions

### 🔍 Assumptions
The following assumptions form the foundation of the data processing and architectural approach:

* **Relational Mapping:** We assume all Excel files contain a common key (e.g., `Lot_ID`) that allows for relational mapping, even if column names and key formats differ slightly across files.
* **Data Source:** Instead of a live database connection, the Excel files represent the **"Source of Truth,"** simulating an export from a legacy ERP system.

---

### 🎯 Project Scope

#### **In-Scope (What we are doing)**
* **Trend Identification:** Tracking if the same defect type appears across multiple lots over time.
* **Pattern Recognition:** Distinguishing recurring defect issues from one-off incidents.
* **Data Aggregation:** Consolidating inspection data across disparate daily and weekly inspection logs.
* **Defect Filtering:** Excluding non-defect records (e.g., `Qty Defects = 0`) from occurrence counts to ensure accuracy.
* **Data Integrity Signaling:** Indicating when available data is insufficient to determine a recurrence pattern.

#### **Out-of-Scope (What we are NOT doing)**
* **Root Cause Analysis:** Investigating the physical or process-based "why" behind defects.
* **Advanced Analytics:** Predictive modeling or AI-based quality analysis.
* **Real-time Monitoring:** Live inspection or production line monitoring.
* **Source Data Enforcement:** Preventing or correcting "bad" entries at the Excel source level.
* **Security & Access:** User authentication, authorization, or role-based access control (RBAC).
* **High-Fidelity UI:** Delivering a "pixel-perfect" consumer-grade design (the focus is on a functional, clean dashboard).
