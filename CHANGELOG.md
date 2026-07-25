# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and semantic versioning.

---

## [Unreleased]

### In Progress — Branch 2 (Stages 01–04 Implemented, Stages 05–08 Planned)

Branch 2 expands the ERA5 pipeline beyond the single‑variable MVP.
The following components are **in progress**:

#### Multi‑Variable ERA5 Ingestion (Stage 01)

- Support for multiple ERA5 variables (e.g., PM‑related meteorology, humidity, wind, boundary‑layer height)
- Config‑driven variable selection
- Parallelized monthly downloads
- Improved skip logic and artifact tracking

#### GRIB Metadata + Multi‑File Preprocessing (Stage 02)

- GRIB metadata extraction (units, long_name, standard_name)
- Multi‑variable GRIB → Parquet conversion
- Structured intermediate directories (`intermediate/grib/<var>/<year>/<month>/`)
- Validation of GRIB coordinate consistency (lat/lon grids, time indexing)

#### Feature Engineering Expansion (Stage 03)

- Multi‑variable feature registry
- Spatial + temporal aggregations
- Rolling windows, lagged features, and derived meteorological indicators
- Feature metadata (units, description, provenance)
- Transformation graphs and dependency tracking

#### Modeling Expansion (Stage 04)

- Multiple model families (linear, tree‑based, ensemble)
- Config‑driven model selection
- Train/validation/test splits
- Deterministic training workflows
- Model metadata + provenance
- Versioned model artifacts

### Planned — Branch 2 (Stages 05–08)

The following components are **planned but not yet implemented**:

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

#### Stage 07 — Pipeline Runner

- Unified orchestration of Stages 01–06
- Run manifests
- Deterministic execution guarantees
- Multi‑stage validation

#### Stage 08 — Deployment Scaffolding

- Model registry integration
- Artifact versioning
- Packaging for downstream apps or dashboards

#### Notes

- Branch 2 introduces multi-variable ingestion, metadata tracking, and expanded modeling; pipeline execution remains `.venv`-based.
- Branch 2 retains the Branch 1 directory structure; multi-variable artifacts extend existing folders.
- Branch 2 is **not complete**; only Stages 01–04 are implemented.
- Stages 05–08 will be introduced in future releases.
- No AI/RAG/agentic inference is planned for ERA5 Branch 2.

---

## [0.1.0] —  Branch 1 MVP — Stages 01-05 Complete

### Added

#### Stage 01 — ERA5 Download

- Single‑variable ERA5 ingestion (2m_temperature)
- Monthly downloader with skip logic
- CDS API diagnostics (`test_cds.py`)
- Config‑driven year/month/variable selection

#### Stage 02 — Preprocessing

- GRIB unzip utility
- GRIB metadata inspection
- GRIB → Parquet conversion (single variable)
- Lightweight validation (file exists, non‑empty)

#### Stage 03 — Feature Engineering

- Minimal feature registry
- Identity transformation placeholder
- Deterministic `features.parquet` output

#### Stage 04 — Modeling

- Baseline `MeanPredictor` model
- Deterministic training workflow
- Pickle‑based model artifact (`model.pkl`)
- Config‑driven target selection

#### Stage 05 — Evaluation

- MAE + RMSE metrics
- Deterministic predictions
- `predictions.parquet` output
- Unified logging across all stages

#### Infrastructure

- Makefile orchestration (`download`, `preprocess`, `features`, `train`, `evaluate`)
- Unified Rich logging utilities
- Centralized path manager (`Paths`)
- Lightweight environment validator
- Smoke‑test suite for all stages
- Repository‑wide `.gitignore` for climate data pipelines
- Mermaid diagrams for pipeline architecture

### Changed

- Standardized directory structure (`raw`, `intermediate`, `features`, `models`, `predictions`)
- Improved skip logic for ingestion
- Refined preprocessing logs and error messages
- Updated root README to reflect Branch 1 completion

### Fixed

- GRIB → Parquet edge cases for empty files
- Pickle import‑path stability for baseline model
- Logging inconsistencies across stages
- Minor Makefile invocation issues

### Notes

- Branch 1 is **fully deterministic** and intentionally minimal.
- Branch 1 uses a project-local `.venv` environment; Conda is optional and only needed for GRIB CLI tools.
- Branch 2 introduces multi-variable ingestion, metadata tracking, and expanded modeling; pipeline execution remains `.venv`-based.
