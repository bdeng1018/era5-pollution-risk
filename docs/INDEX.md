# Documentation Index — ERA5 Pollution‑Risk Pipeline (Branch 1)

This index provides a structured overview of all documentation for the ERA5 Pollution‑Risk Pipeline (Branch 1).
Use this as the entry point to navigate architecture, onboarding, data contracts, pipeline flow, and stage‑specific design docs.

Branch 1 is a **deterministic, single‑variable ERA5 ingestion, preprocessing, feature‑engineering, modeling, and evaluation pipeline**.
It establishes the foundation for multi‑variable, metadata‑rich, ML‑driven expansions arriving in Branch 2.

---

## 1. High‑Level Documentation

### [README.md](../README.md)

Project overview, goals, quickstart, and repository structure.

### [ONBOARDING.md](ONBOARDING.md)

Developer setup, `.venv` environment configuration, VS Code workspace, Makefile workflow, debugging, testing, and artifact reset instructions.

### [ARCHITECTURE.md](ARCHITECTURE.md)

High‑level system design, stage responsibilities (01–05), directory layout, logging architecture, configuration structure, and testing model.

### [PIPELINE_FLOW.md](PIPELINE_FLOW.md)

End‑to‑end ERA5 data flow, artifact transitions, stage dependencies, diagnostics flow, and final output description.

---

## 2. Data Contract Documentation

### [DATA_DICTIONARY.md](DATA_DICTIONARY.md)

Definitions for all fields produced in Branch 1:

- Intermediate Parquet (Stage 02)
- Features Parquet (Stage 03)
- Predictions Parquet (Stage 05)

Includes types, descriptions, and semantic meaning.

### [SCHEMA_REFERENCE.md](SCHEMA_REFERENCE.md)

Formal schema reference for Branch 1 artifacts:

- Stage 02 schema
- Stage 03 schema
- Stage 05 schema

Includes data types, required fields, and schema evolution rules.

---

## 3. Stage‑Specific Design Documentation

### [STAGE05_DESIGN.md](STAGE05_DESIGN.md)

Deep dive into the Stage 05 evaluation engine:

- evaluation logic
- metric computation
- error handling
- determinism guarantees
- output schema
- logging
- relationship to Branch 2

Stages 01–04 are intentionally simple and do not require design documents.

---

## 4. Additional Project Documentation

### [CONTRIBUTING.md](../CONTRIBUTING.md)

Contribution guidelines, PR workflow, coding standards, branching strategy, and Makefile conventions.

### [CHANGELOG.md](../CHANGELOG.md)

Version history and release notes for Branch 1 and Branch 2.

### [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)

Community and contributor behavior guidelines.

### [SECURITY.md](../SECURITY.md)

Security reporting process and vulnerability disclosure guidelines.

---

## 5. Visual Diagrams

### `diagrams/data_flow_overview.png`

High‑level ERA5 pipeline data‑flow diagram showing:

- GRIB ingestion
- GRIB → Parquet conversion
- feature generation
- modeling
- evaluation
- artifact transitions across `data/` and `models/`

### `diagrams/pipeline_architecture.png`

Architecture diagram illustrating:

- stage layout (`src/download_01` → `src/evaluation_05`)
- directory structure (`data/`, `models/`, `configs/`, `scripts/diagnostics/`)
- Makefile execution flow
- logging and diagnostics placement

---

## 6. Where to Go Next

If you're evaluating the pipeline:

- Start with **README.md**
- Then read **ARCHITECTURE.md**
- Follow with **PIPELINE_FLOW.md**
- Review **DATA_DICTIONARY.md** and **SCHEMA_REFERENCE.md**
- Finish with **STAGE05_DESIGN.md**

If you're onboarding as a developer:

- Start with **ONBOARDING.md**
- Then explore the `src/` stage folders
- Use diagnostics under `scripts/diagnostics/`
- Run tests under `tests/`
- Use Makefile targets for stage execution

---

## 7. Maintainer

Maintainer: **Brian Deng** <br>
Email: **<bdeng.data.pipelines@gmail.com>** <br>
GitHub: **<https://github.com/bdeng1018>**
