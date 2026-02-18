# Tech Stack Decision Record (TSDR)

## TSDR 001: Selection of Tech Stack for Defect Trend Analysis
**Status:** Accepted

**Context:**
The project architecture is defined as a client-server, monolithic, single-database (simulated), synchronous, and layered system. The primary objective is to transform legacy Excel exports into a functional, clean dashboard for defect trend identification. Given that this is a data-heavy project involving "fuzzy" mapping and pattern recognition, the stack must excel at data manipulation and rapid deployment.

**Decision:**
We will use **Stack A: Python + Streamlit + SQLAlchemy + Postgres**, managed with **Poetry** for dependency management, virtual environment isolation, and reproducible lockfiles.

### Evaluation Dimensions:

1. **AI Support Strength:** **High.** Python is the industry standard for AI and data science. This choice future-proofs the project for "In-Scope" expansion into advanced defect classification or "Out-of-Scope" predictive analysis.
2. **Popularity & Community Answers:** **Very High.** Streamlit and SQLAlchemy have massive communities. Finding solutions for specific Excel parsing challenges or specialized data visualizations is significantly faster than in Spring or Node-based views.
3. **Ecosystem Maturity:** **Strong.** Python’s data ecosystem (specifically libraries like Pandas or Polars) is the most mature for the "relational mapping of disparate files" required by our project assumptions.
4. **Deployment Simplicity:** **Superior.** Streamlit allows the UI and backend to exist in the same execution context, eliminating the need to manage separate frontend/backend deployments. This fits our requirement for a portable, functional tool.
5. **Path to Next Architecture:** **Flexible.** While starting as a monolith, Python modules can be easily wrapped into FastAPI services or containerized if the project evolves toward a microservices or cloud-native architecture.
6. **Build/Dependency Reliability:** **High with Poetry.** Poetry gives deterministic dependency resolution (`poetry.lock`), consistent virtual environments, and a single command surface for running app/tests/scripts.

---

**Alternatives Considered:**

* **Stack B: Spring Boot (MVC) + Thymeleaf + JPA:** Rejected. While highly mature, the development overhead for simple data visualization is too high. It lacks the "data-first" speed required for quick Excel-to-Dashboard transformations.
* **Stack C: Node.js + Express + EJS/Pug:** Rejected. Node is excellent for asynchronous I/O, but its data processing ecosystem is less intuitive for complex relational mapping compared to Python's data-centric libraries.

---

**Consequences:**

* **Positive:**
    * **Rapid Prototyping:** Streamlit turns data scripts into UI components in minutes, fitting the "clean but not pixel-perfect" requirement.
    * **Data-Centric:** Python’s handling of Excel inconsistencies and relational mapping is best-in-class.
    * **Simplified Maintenance:** The synchronous, layered approach is highly readable for teams with a data science or general engineering background.
    * **Reproducible Environments:** Poetry standardizes setup across local machines and CI with lockfile-backed installs.
* **Negative:**
    * **UI Constraints:** Streamlit's layout options are more rigid than custom HTML/CSS frameworks used in Stacks B or C.
    * **Resource Consumption:** Python can be more memory-intensive during batch processing of large Excel files compared to compiled alternatives.
    * **Tooling Requirement:** Contributors must install Poetry before first run.

---
