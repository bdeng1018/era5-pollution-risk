# Roadmap — ERA5 Pollution Risk Pipeline

This roadmap outlines the development trajectory for the ERA5 Pollution Risk Pipeline across Branch 1, Branch 2, and the upcoming Branch 3, which introduces optional AI/LLM/RAG capabilities for advanced analytics and downstream applications.

---

## 1. Branch Overview

### Branch 1 — MVP (Complete)

- Single‑variable ERA5 ingestion
- Minimal feature engineering
- Baseline model + evaluation
- Deterministic Makefile workflow

### Branch 2 — Multi‑Variable Expansion (In Progress)

- Multi‑variable ingestion
- GRIB metadata extraction
- Chunk engine + IR₄ compiler
- Expanded feature engineering (IR₅)
- Modeling + evaluation upgrades
- Reporting + runner scaffolding
- Fully deterministic, **no AI/LLM/RAG**

### Branch 3 — AI/LLM/RAG + Intelligent Analytics (Planned)

Branch 3 introduces **new AI capabilities** layered *on top* of the deterministic pipeline:

- LLM‑assisted reporting and summaries
- RAG‑based metadata search (configs, features, model lineage)
- Agentic diagnostics (auto‑explain anomalies, auto‑suggest fixes)
- Natural‑language querying of ERA5 datasets
- Model‑aware assistants for feature exploration
- Optional AI‑enhanced dashboards or notebooks

Branch 3 does **not** replace deterministic Stages 01–08.
It augments them with intelligent tooling.

---

## 2. Stage Roadmap

### Stage 01 — Multi‑Variable ERA5 Ingestion

**Status:** Complete
**Next:** Additional meteorological variables as needed.

### Stage 02 — GRIB Metadata + Preprocessing

**Status:** Complete
**Next:** Expand metadata parquet (units, long_name, standard_name).

### Stage 03 — Chunk Engine

**Status:** Complete
**Next:** Region‑specific chunking + multi‑resolution support.

### Stage 04 — Spatiotemporal Compiler (IR₄)

**Status:** Complete
**Next:** IR₄ schema freeze + diagnostics.

### Stage 05 — Feature Engineering (IR₅)

**Status:** In Progress
**Next:**

- Feature registry
- Pollution integration
- Composite features
- Rolling windows + lags
- Feature metadata

### Stage 06 — Modeling

**Status:** Planned
**Next:**

- Multiple model families
- Deterministic training
- Model metadata + provenance

### Stage 07 — Evaluation

**Status:** Planned
**Next:**

- Full regression metrics
- Residual analysis
- Diagnostic plots
- Model comparison utilities

### Stage 08 — Reporting + Runner

**Status:** Planned
**Next:**

- Unified reporting layer
- Run manifests
- Multi‑stage orchestration

---

## 3. Branch 3 — AI/LLM/RAG Enhancements

Branch 3 introduces intelligent tooling built on top of deterministic artifacts:

### AI‑Enhanced Reporting

- LLM‑generated model summaries
- Natural‑language explanations of feature importance
- Automated “What changed?” reports across versions

### RAG‑Powered Metadata Search

- Query configs (`era5.yml`, `variables.yml`, `paths.yml`)
- Query feature registry
- Query model lineage
- Query evaluation artifacts

### Agentic Diagnostics

- Auto‑detect anomalies in IR₄/IR₅
- Auto‑suggest fixes (missing variables, shape mismatches, metadata gaps)
- Auto‑generate debugging steps

### Natural‑Language Dataset Exploration

- “Show me wind patterns for July 2019”
- “Explain why PM2.5 spiked on this day”
- “Compare dispersion index across regions”

### AI‑Assisted Development Tools

- Code scaffolding for new features
- Auto‑generated diagrams
- Auto‑generated documentation updates

Branch 3 is **optional** and does not affect deterministic execution.

---

## 4. Milestones

### ✔️ Milestone A — Multi‑Variable Ingestion

Completed in Branch 2.

### ✔️ Milestone B — IR₄ Compiler

Completed in Branch 2.

### 🔄 Milestone C — IR₅ Feature Engineering

In progress.

### ⏳ Milestone D — Modeling + Evaluation

Planned for Branch 2 late stage.

### ⏳ Milestone E — Reporting + Runner

Planned for Branch 2 late stage.

### ⏳ Milestone F — AI/LLM/RAG Layer

Planned for Branch 3.

---

## 5. Stability Levels

| Component | Stability |
|----------|-----------|
| Raw ERA5 ingestion | Stable |
| GRIB preprocessing | Stable |
| Chunk engine | Stable |
| IR₄ compiler | Stable |
| IR₅ features | Evolving |
| Modeling | Planned |
| Evaluation | Planned |
| Reporting | Planned |
| Deployment | Planned |
| AI/LLM/RAG | Future |

---

## 6. Documentation Roadmap

### Completed

- **[Architecture](ca://s?q=Explain_ARCHITECTURE_md)**
- **[Pipeline Flow](ca://s?q=Explain_PIPELINE_FLOW_md)**
- **[Data Dictionary](ca://s?q=Explain_DATA_DICTIONARY_md)**
- **[Schema Reference](ca://s?q=Explain_SCHEMA_REFERENCE_md)**
- **[Onboarding](ca://s?q=Explain_ONBOARDING_md)**
- **[Index](ca://s?q=Explain_INDEX_md)**
- CHANGELOG.md
- ROADMAP.md

### Planned

- STAGE04_DESIGN.md (after IR₄ freeze)
- STAGE05_DESIGN.md (after IR₅ freeze)
- FEATURE_REGISTRY.md
- MODEL_READY_SCHEMA.md
- API_REFERENCE.md (Branch 3)
- AI_LAYER_OVERVIEW.md (Branch 3)

---

## 7. Guiding Principles

- Deterministic core pipeline
- Config‑driven architecture
- Reproducible artifacts
- Clear IR boundaries
- AI/LLM/RAG optional and additive
- Branch‑based development
- No AI inference in Branch 2
- AI tooling introduced in Branch 3

---

## 8. Contact

Maintainer: Brian Deng
Email: <bdeng.data.pipelines@gmail.com>
GitHub: <https://github.com/bdeng1018>
