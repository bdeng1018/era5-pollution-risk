# ERA5 Pollution‑Risk Pipeline — Branch 1

## Release Notes — v1.0.0 (August 2026)

---

## Overview

ERA5 Pollution‑Risk Pipeline v1.0.0 delivers a fully deterministic, reproducible,
and minimal‑ingestion workflow for smoke‑testing ERA5 ingestion, preprocessing,
feature engineering, baseline modeling, and evaluation. Branch 1 intentionally
focuses on speed, simplicity, and environment‑agnostic execution. It mirrors the
CMS ingestion pipeline’s architecture while avoiding heavy validation logic,
schema enforcement, multi‑variable ingestion, and GRIB/Parquet correctness checks.

This release establishes the foundation for Branch 2, which will introduce full
ingestion validation, fixtures, schema checks, metadata extraction, skip‑logic
correctness, and multi‑variable ingestion.

---

## Key Features (Branch 1)

### Minimal ERA5 Ingestion

- Monthly ERA5 GRIB download (mock‑friendly)
- No multi‑variable ingestion
- No schema or metadata validation

### Deterministic Preprocessing

- GRIB unzip + inspection
- GRIB → Parquet conversion (no correctness checks)
- Fast smoke‑testing for ingestion flow

### Feature Engineering

- Lightweight feature construction
- No deterministic feature validation
- No multi‑variable feature dependencies

### Baseline Modeling

- MeanPredictor baseline model
- Deterministic training and evaluation
- Minimal artifact generation

### Evaluation + Predictions

- Simple evaluation metrics
- Prediction artifact generation
- No artifact validation or lineage checks

---

## Developer Ergonomics

- Makefile‑driven pipeline (CMS‑style)
- Black + Ruff formatting and linting
- pytest smoke tests
- CDS API diagnostics
- Interactive `make reset` (y/n confirmation)
- Deterministic `.venv` environment

---

## Deployment

- Single‑container deterministic Dockerfile
- GitHub Actions CI/CD workflow
- Environment validation on container startup
- Reproducible build using `environment.yml`

---

## Known Limitations (Intentional for Branch 1)

- No real CDS ingestion logic
- No schema validation or metadata extraction
- No GRIB/Parquet correctness checks
- No skip‑logic correctness
- No multi‑variable ingestion
- No distributed chunking or parallel ingestion

These will be addressed in Branch 2.

---

## Roadmap

### Branch 2 (v2.0.0)

- Full ingestion validation
- Schema enforcement
- Metadata extraction
- Multi‑variable ingestion
- Skip‑logic correctness
- Deterministic feature validation
- Artifact lineage + provenance

### Branch 3 (v3.0.0)

- Distributed ingestion
- Chunked GRIB processing
- Multi‑model evaluation
- Agentic inference modules (optional)

---

## Versioning

ERA5 Pollution‑Risk Pipeline follows semantic versioning:

- **MAJOR**: Branch‑level architectural changes
- **MINOR**: New ingestion or modeling capabilities
- **PATCH**: Deterministic fixes, formatting, diagnostics

v1.0.0 is the first stable release of Branch 1.

---

## Authors

Brian Deng <br>
ERA5 Pollution‑Risk Pipeline Maintainer <br>
August 2026
