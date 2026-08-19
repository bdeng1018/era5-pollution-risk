# Changelog

All notable changes to this project will be documented in this file.
This project follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and semantic versioning.

---

## [Unreleased] — Branch 2 (Stages 05–08)

### Overview

The Unreleased section tracks ongoing development for Branch 2, which extends the pipeline beyond ingestion and tensor compilation into feature engineering, modeling, evaluation, and deployment.
Stages 01–04 are now frozen in v2.0.0; the remaining part of Branch 2 focuses on Stages 05–08.

### Planned — Multi‑Stage ERA5 Pipeline (Deterministic, No AI)

#### Stage 05 — Feature Engineering

- Multi‑variable feature registry (meteorology + pollution‑risk indicators)
- Spatial aggregations (grid‑cell neighborhoods, lat/lon windows)
- Temporal aggregations (rolling windows, lags, diurnal cycles)
- Derived meteorological indicators (humidity, wind shear, stability indices)
- Feature metadata (units, description, provenance)
- Transformation graphs and dependency tracking

#### Stage 06 — Modeling

- Multiple model families (linear, tree‑based, ensemble)
- Config‑driven model selection
- Train/validation/test splits
- Deterministic training workflows
- Versioned model artifacts
- Model metadata + provenance
- Hyperparameter search scaffolding (deterministic, no AI)

#### Stage 07 — Evaluation

- Full regression metrics (MAE, RMSE, R², MAPE)
- Residual analysis
- Diagnostic plots
- Error distributions
- Model comparison utilities
- Dataset‑level diagnostics

#### Stage 08 — Deployment / Reporting / Runner

- Model registry integration
- Artifact versioning
- Packaging for downstream apps or dashboards
- Unified reporting outputs
- Pipeline runner for Stages 01–08
- Deterministic execution guarantees
- Deployment hooks reserved for Branch 3

### Notes

- The remaining part of Branch 2 introduces feature engineering, modeling, evaluation, and deployment.
- Pipeline execution remains `.venv`‑based and deterministic.
- No AI/RAG/LLM/agentic inference is planned for Branch 3.
- Stages 05–08 are planned but not yet implemented.

---

## [2.0.0] — Branch 2 Artifact‑Frozen Release (Stages 01–04)

### Overview

v2.0.0 is the first fully reproducible, artifact‑frozen release of the ERA5 Pollution‑Risk ingestion engine.
This version finalizes Stages 01–04 (Download → Preprocessing → Core Chunking → Spatiotemporal), introduces deterministic tensor compilation, and adds a scientific manifest documenting provenance, QC, and artifact lineage.

### Added

- Full artifact freezing under `artifacts/v2.0.0/`:
  - **Stage 01 — Download:** monthly + single‑level GRIBs
  - **Stage 02 — Preprocessing:** parquet + metadata
  - **Stage 03 — Core Chunking:** merged.nc + chunk plan + chunk schema
  - **Stage 04 — Spatiotemporal:** tensor.nc + metadata + QC + grid + mask + temporal diagnostics
- Scientific `manifest.yml` including:
  - commit SHA
  - pipeline stages
  - artifact paths
  - tensor/grid shapes
  - region bounding box
  - requested vs. produced variables
  - compiler contract
  - QC status
- Deterministic Stage 04 tensor compiler (hourly alignment, no interpolation)
- Complete diagnostics suite for Stages 01–04
- Tight LA Basin bounding box (33°–35°N, 116°–120°W)
- Reproducible Makefile workflow for ingestion → preprocessing → merge → tensor

### Changed

- Updated pipeline architecture to modular 8‑stage design (Stages 01–08)
- Standardized artifact directory structure for reproducibility
- Improved GRIB metadata extraction and parquet normalization
- Refined coordinate alignment and chunk merging logic
- Updated README and documentation to reflect new architecture

### Fixed

- GRIB → Parquet inconsistencies for multi‑variable datasets
- Timestamp normalization issues in Stage 02
- Mask/grid mismatch in Stage 04 compiler
- QC edge cases for missing hours
- Makefile dependency ordering

### Notes

- v2.0.0 is the first version with complete scientific reproducibility guarantees.
- Stages 05–08 (Features, Modeling, Evaluation, Deployment) will be introduced in Branch 3.
- No AI/RAG/LLM components are included in Branch 2.

---

## [1.0.0] — Branch 2 Stabilization Release (Pre‑Freeze)

### Overview

v1.0.0 stabilizes Stages 01–04 before artifact freezing.
This release finalizes multi‑variable ingestion, deterministic preprocessing, and core chunking, preparing the system for the v2.0.0 artifact freeze.

### Added

- Stable multi‑variable ERA5 ingestion (Stage 01 — Download)
- Deterministic GRIB → Parquet preprocessing (Stage 02)
- Structured intermediate directories (`intermediate/<year>/<month>/<var>`)
- GRIB metadata parquet generation
- Initial chunk planner + merge logic (Stage 03)
- Early spatiotemporal compiler prototype (Stage 04)

### Changed

- Refined directory structure for ingestion + preprocessing
- Improved skip logic and metadata extraction
- Updated Makefile orchestration for deterministic execution

### Fixed

- GRIB coordinate consistency issues
- Early merge instability for multi‑variable datasets
- Logging inconsistencies across ingestion and preprocessing

### Notes

- v1.0.0 is the final “working pipeline” release before artifact freezing.
- v2.0.0 introduces full reproducibility and scientific manifesting.

---

## [0.2.0] — Branch 2 MVP — Stages 01–04 Complete

### Added

- **Stage 01 — Download:** Multi‑variable ERA5 ingestion
- **Stage 02 — Preprocessing:** GRIB unzip, inspect, convert, metadata parquet
- **Stage 03 — Core Chunking:** chunk planner, orchestrator, worker, merge
- **Stage 04 — Spatiotemporal:** compiler (grid → mask → align → interpolate → qc → tensor builder)
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

- **Stage 01 — Download:** Single‑variable ERA5 ingestion (2m_temperature)
- **Stage 02 — Preprocessing:** GRIB unzip, inspect, convert
- **Stage 03 — Core Chunking:** Minimal feature registry
- **Stage 04 — Spatiotemporal:** Baseline MeanPredictor model
- **Stage 05 — Features/Evaluation:** MAE, RMSE
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
