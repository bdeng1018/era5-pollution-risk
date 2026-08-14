# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and semantic versioning.

---

## [Unreleased]

### In Progress — Branch 2 (Stages 01–04 Implemented, Stages 05–08 Planned)

Branch 2 expands the ERA5 pipeline from the single‑variable MVP into a
multi‑variable, multi‑year, production‑aligned system. The pipeline now follows
the full **8‑stage architecture**:

1. Download
2. Preprocessing
3. Core Chunks
4. Spatiotemporal Tensor
5. Feature Engineering
6. Modeling
7. Evaluation
8. Deployment / AI Harnesses

### Stage 01 — Multi‑Variable ERA5 Download (In Progress)

- Multi‑variable ERA5 ingestion (meteorology + pollution‑related indicators)
- Config‑driven variable registry
- Parallelized monthly downloads
- Improved skip‑logic and artifact tracking
- Structured raw directory layout (`raw/<var>/<year>/<month>/`)

### Stage 02 — Preprocessing (In Progress)

- GRIB metadata extraction (units, long_name, standard_name)
- Multi‑file GRIB → Parquet conversion
- Coordinate consistency validation (lat/lon grids, time indexing)
- Structured intermediate directories (`intermediate/grib/<var>/<year>/<month>/`)
- Deterministic preprocessing logs

### Stage 03 — Core Chunks (In Progress)

- Chunk‑level Parquet assembly
- Temporal slicing and chunk metadata
- Deterministic chunk IDs + provenance
- Chunk merging utilities
- Output: `data/chunks/` and `data/chunks_metadata/`

### Stage 04 — Spatiotemporal Tensor (In Progress)

- Multi‑variable tensor assembly
- Spatial alignment across variables
- Time‑indexed tensor construction
- QC metadata (`merged_qc.json`)
- Output: `data/spatiotemporal/spatiotemporal_tensor.nc`

### Stage 05 — Feature Engineering (Planned)

- Multi‑variable feature registry
- Spatial + temporal aggregations
- Rolling windows, lagged features, derived meteorological indicators
- Feature metadata (units, description, provenance)
- Output: `data/features/`

### Stage 06 — Modeling (Planned)

- Multiple model families (linear, tree‑based, ensemble, time‑series)
- Config‑driven model selection
- Train/validation/test splits
- Deterministic training workflows
- Versioned model artifacts
- Output: `data/models/`

### Stage 07 — Evaluation (Planned)

- Full regression metrics (MAE, RMSE, R², MAPE)
- Residual analysis + diagnostic plots
- Error distributions
- Model comparison utilities
- Output: `data/predictions/`

### Stage 08 — Deployment + AI Harnesses (Planned)

- Model registry integration
- Artifact versioning
- Packaging for downstream apps or dashboards
- Optional AI harnesses for:
  - automated diagnostics
  - metadata extraction
  - model‑drift monitoring
  - inference orchestration

### Notes

- Branch 2 introduces multi‑variable ingestion, metadata tracking, chunking, and
  spatiotemporal tensor assembly.
- Stages 01–04 are implemented; Stages 05–08 are planned.
- Execution remains `.venv`‑based; Docker is optional.
- No RAG/LLM inference is planned for core ERA5 modeling; AI harnesses are
  optional utilities for diagnostics and metadata.

---

## [1.0.0] — Branch 1 MVP — Stages 01–05 Complete

### Added

#### Stage 01 — ERA5 Download

- Optional single‑variable ERA5 ingestion (2m_temperature)
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
- Deterministic smoke‑test suite (CDS API fully mocked)
- Repository‑wide `.gitignore` for climate data pipelines
- Mermaid diagrams for pipeline architecture
- GitHub Actions CI workflow (`.github/workflows/ci.yml`)
- Deployment scaffolding (`deployment/` directory)

### Changed

- Standardized directory structure (`raw`, `intermediate`, `features`, `models`, `predictions`)
- Improved skip logic for ingestion
- Refined preprocessing logs and error messages
- Updated root README to reflect Branch 1 completion
- Updated deployment docs for v1.0.0

### Fixed

- GRIB → Parquet edge cases for empty files
- Pickle import‑path stability for baseline model
- Logging inconsistencies across stages
- Minor Makefile invocation issues
- Deterministic `.venv` execution across CI/CD

### Notes

- Branch 1 is **fully deterministic**, **offline**, and intentionally minimal.
- Branch 1 uses a project‑local `.venv` environment; Conda is optional and only needed for GRIB CLI tools.
- Branch 2 introduces multi‑variable ingestion, metadata tracking, chunking, and expanded modeling; pipeline execution remains `.venv`‑based.

---

## [0.1.0] — Prototype / Early Pipeline Skeleton

### Added

- Initial repository structure
- Early Makefile with placeholder targets
- Prototype GRIB → Parquet converter (non‑deterministic)
- Basic logging utilities
- Initial configs (`paths.yml`, `variables.yml`)
- First draft of pipeline diagrams
- Minimal test harness (non‑mocked ingestion)

### Changed

- Refactored directory layout to prepare for Branch 1
- Improved logging consistency
- Reorganized `src/` into stage‑based modules

### Notes

- v0.1.0 was an **internal prototype**, not a public release.
- Branch 1 replaced all ingestion, preprocessing, modeling, and evaluation logic with deterministic implementations.
