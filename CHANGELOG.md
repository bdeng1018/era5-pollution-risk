# Changelog

All notable changes to this project will be documented in this file.
This project follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and semantic versioning.

---

## [Unreleased] — Branch 2 (Stages 01–08)

### In Progress — Multi‑Stage ERA5 Pipeline (Deterministic, No AI)

Branch 2 expands the ERA5 pipeline beyond the single‑variable MVP.
The following components are currently in development:

#### Stage 01 — Multi‑Variable ERA5 Ingestion

- Support for multiple ERA5 variables (meteorology relevant to pollution risk)
- Config‑driven variable selection
- Parallelized monthly downloads
- Improved skip logic and artifact tracking
- GRIB metadata extraction (units, long_name, standard_name)

#### Stage 02 — GRIB Metadata + Multi‑File Preprocessing

- Multi‑variable GRIB → Parquet conversion
- Structured intermediate directories (`intermediate/<year>/<month>/<var>`)
- Validation of GRIB coordinate consistency (lat/lon grids, time indexing)
- Enhanced inspection utilities and metadata parquet generation

#### Stage 03 — Feature Engineering Expansion

- Multi‑variable feature registry
- Spatial + temporal aggregations
- Rolling windows, lagged features, derived meteorological indicators
- Feature metadata (units, description, provenance)
- Transformation graphs and dependency tracking

#### Stage 04 — Modeling Expansion

- Multiple model families (linear, tree‑based, ensemble)
- Config‑driven model selection
- Train/validation/test splits
- Deterministic training workflows
- Versioned model artifacts
- Model metadata + provenance

#### Stage 05 — Evaluation Expansion

- Full regression metrics (MAE, RMSE, R², MAPE)
- Residual analysis
- Diagnostic plots
- Error distributions
- Model comparison utilities

#### Stage 06 — Reporting Layer

- Model performance reports
- Feature importance summaries
- Dataset‑level diagnostics
- Run metadata artifacts
- Unified reporting outputs

#### Stage 07 — Pipeline Runner

- Unified orchestration of Stages 01–06
- Run manifests
- Deterministic execution guarantees
- Multi‑stage validation

#### Stage 08 — Deployment Scaffolding

- Model registry integration
- Artifact versioning
- Packaging for downstream apps or dashboards
- Deployment hooks reserved for Branch 3

### Notes

- Branch 2 introduces multi‑variable ingestion, metadata tracking, expanded modeling, and evaluation.
- Pipeline execution remains `.venv`‑based and deterministic.
- No AI/RAG/LLM/agentic inference is planned for Branch 2.
- Stages 05–08 are planned but not yet implemented.

---

## [0.2.0] — Branch 2 MVP — Stages 01–04 Complete

### Added

- Stage 01: Multi‑variable ERA5 download (monthly GRIB ingestion)
- Stage 02: GRIB unzip, inspect, convert, metadata parquet
- Stage 03: Chunk planner, orchestrator, worker, merge
- Stage 04: Spatiotemporal compiler (grid → mask → align → interpolate → qc → tensor builder)
- Deterministic Makefile workflow (`make stage01` → `make stage04`)
- VS Code workspace (tasks, launch, settings, extensions)
- Unified logging across ingestion, preprocessing, chunking, and compiler
- Environment validator (`env_check`)
- Mermaid diagrams for pipeline architecture
- Smoke tests for Stages 01–04

### Changed

- Standardized directory structure (`raw`, `intermediate`, `chunks`, `spatiotemporal`)
- Improved skip logic for ingestion
- Refined preprocessing logs and error messages
- Updated root README to reflect Branch 2 architecture
- Enhanced Makefile cleanup targets

### Fixed

- GRIB → Parquet edge cases for empty or malformed files
- Chunk merge stability for multi‑variable datasets
- Logging inconsistencies across stages
- Minor Makefile invocation issues

### Notes

- Branch 2 is deterministic and multi‑variable.
- Stages 05–08 will be introduced in future releases.
- No AI/RAG/LLM components are included in Branch 2.

---

## [0.1.0] — Branch 1 MVP — Stages 01–05 Complete

### Added

- Stage 01: Single‑variable ERA5 ingestion (2m_temperature)
- Stage 02: GRIB unzip, inspect, convert
- Stage 03: Minimal feature registry
- Stage 04: Baseline MeanPredictor model
- Stage 05: Evaluation (MAE, RMSE)
- Deterministic predictions + unified logging
- Makefile orchestration (download → preprocess → features → train → evaluate)
- Smoke‑test suite
- Repository‑wide `.gitignore`
- Mermaid diagrams

### Changed

- Standardized directory structure
- Improved skip logic
- Refined preprocessing logs
- Updated root README

### Fixed

- GRIB → Parquet edge cases
- Pickle import‑path stability
- Logging inconsistencies
- Minor Makefile issues

### Notes

- Branch 1 is fully deterministic and intentionally minimal.
- Branch 2 introduces multi‑variable ingestion and expanded modeling.
