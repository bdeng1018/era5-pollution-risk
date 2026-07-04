# Branch 2 — ERA5 Ingestion, Preprocessing & Core Processing Pipeline (Development Snapshot)

Branch 2 expands the Branch 1 MVP into a multi‑stage, production‑aligned ERA5 ingestion, preprocessing, and **chunked core processing** system. This branch introduces:

- A production‑grade ingestion stage (Stage 1) with retry logic, metadata, and directory validation
- A deterministic preprocessing stage (Stage 2) with stable, passing tests
- A parallel‑safe, deterministic chunk‑processing engine (Stage 3)
- Unified logging
- Structured metadata
- A robust engineering architecture designed for multi‑year scaling

This README documents the current development snapshot of Branch 2. It intentionally reflects the state of the branch at push time:

- Stage 1: Work-in-progress (some tests failing)
- Stage 2: Fully implemented and passing all tests
- Stage 3: Fully implemented and passing all tests
- Main branch remains stable and untouched

---

## Overview

Branch 2 introduces a **three-stage ERA5 pipeline**:

1. **Stage 1 — Ingestion (WIP)**
   - CDS API client
   - Retry logic
   - Directory validation (currently being debugged)
   - Metadata logging
   - Config‑driven execution
   - Some pytest contracts failing (expected for Branch 2 development)

2. **Stage 2 — Preprocessing (Stable)**
   - Inspect GRIB structure
   - Generate `.idx` files for cfgrib
   - Convert GRIB → hourly Parquet
   - Generate unified `metadata.json`
   - Deterministic behavior
   - All tests passing

3. **Stage 3 — Chunked Core Processing (New, Stable)**
   - Metadata-driven chunk planning
   - Deterministic transforms
   - Schema-validated Parquet outputs
   - Parallel-safe worker isolation
   - Reproducible intermediate artifacts
   - Tests in progress

Stage 1 failures are acceptable in this feature branch.

---

## Branch 2 Directory Structure (Git‑Safe)

```markdown
era5-pollution-risk/
├── Makefile
├── README.md
│
├── configs/
│   ├── config.yml
│   ├── era5.yml
│   ├── months.yml
│   ├── paths.yml
│   ├── region.yml
│   ├── variables.yml
│   └── years.yml
│
├── data/
│   ├── raw/
│   │   └── era5/            # empty, .gitkeep only
│   ├── intermediate/        # Stage 2 outputs
│   ├── chunks/              # Stage 3 outputs
│   ├── logs/                # structured logs
│   ├── metadata/            # metadata JSON
│   └── predictions/         # modeling outputs
│
├── diagrams/
│   ├── pipeline.md
│   └── pipeline.txt
│
├── environment.yml
│
├── src/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── data_check.py
│   │   ├── env_check.py
│   │   ├── logging.py
│   │   ├── metadata.py
│   │   ├── model_io.py
│   │   └── paths.py
│   │
│   ├── download_01/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── download_era5_monthly.py
│   │   ├── download_era5_single.py
|   |   └── paths.py
│   │
│   ├── preprocessing_02/
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── convert_grib_to_parquet.py
│   │   ├── inspect_grib.py
│   │   ├── run_preprocessing.py
│   │   └── unzip_grib.py
│   │
│   └── core_03/
│       ├── README.md
│       ├── __init__.py
│       ├── chunk_spec.py
│       ├── chunk_planner.py
│       ├── chunk_worker.py
│       ├── chunk_orchestrator.py
│       └── chunk_schema.py
│
└── tests/
    ├── download_01/
    │   ├── test_download_monthly.py
    │   ├── test_download_single.py
    │   ├── test_environment_validation.py
    │   ├── test_metadata_logging.py
    │   └── test_retry_logic.py
    │
    ├── preprocessing_02/
    │   ├── test_preprocessing_acceptance.py
    │   ├── test_preprocessing_integration.py
    │   ├── test_preprocessing_regression.py
    │   ├── test_preprocessing_smoke.py
    │   ├── test_preprocessing_system.py
    │   └── test_preprocessing_unit.py
    │
    └── core_03/
        ├── test_chunk_spec.py
        ├── test_chunk_planner.py
        ├── test_chunk_worker.py
        ├── test_chunk_orchestrator.py
        └── test_chunk_schema.py
```

---

## Pipeline Stages

### Stage 1 — Ingestion (WIP)

Status: Partially implemented, some tests failing.

Current capabilities:

- CDS API client
- Retry logic
- Basic ingestion flow
- Directory validation
- Metadata logging

Known issues:

- Directory validation fails under certain nested layouts
- Config path resolution issues
- Some tests fail due to nondeterministic external API behavior

This is expected for a feature branch.

---

### Stage 2 — Preprocessing (Stable)

Status: Fully implemented, all tests passing.

Capabilities:

- Inspect GRIB structure
- Generate `.idx` files
- Convert GRIB → hourly Parquet
- Generate unified `metadata.json`
- Validate intermediate outputs
- Structured logging
- Deterministic behavior

Stage 2 is production‑ready once Stage 1 stabilizes.

---

### Stage 3 — Chunked Core Processing (New, Stable)

Status: Fully implemented, all tests passing.

Capabilities:

- Metadata-driven chunk planning
- Deterministic transforms
- Schema-validated Parquet outputs
- Parallel-safe worker isolation
- Reproducible intermediate artifacts
- Clean separation of planner, worker, orchestrator, and schema

Stage 3 is the foundation for Stage 4 (spatiotemporal structuring) and Stage 5 (feature engineering).

---

## Testing Status

| Stage     | Status | Notes |
|-----------|--------|-------|
| Stage 1   | ❌ Some failing tests | Expected during Branch 2 development |
| Stage 2   | ✅ All tests passing  | Deterministic and stable |
| Stage 3   | ✅ All tests passings  | Deterministic and stable |

---

## Running the Pipeline

### 1. Configure the pipeline

Edit `config/paths.yml`:

```yaml
paths:
  raw_dir: "data/raw"
  intermediate_dir: "data/intermediate"
  chunks_dir: "data/chunks"
  logs_dir: "data/logs"
```

### 2. Run Stage 1 (WIP — choose one)

Run monthly ingestion:

```bash
python -m src.download_01.download_era5_monthly --config configs/config.yml
```

Or run single‑variable ingestion:

```bash
python -m src.download_01.download_era5_single --config configs/config.yml
```

### 3. Run Stage 2 (Stable)

```bash
python -m src.preprocessing_02.run_preprocessing --config configs/config.yml
```

### 4. Run Stage 3 (New)

```bash
python -m src.core_03.chunk_orchestrator --config configs/config.yml
```

### 5. Makefile

```makefile
download:
    python -m src.download_01.download_era5_monthly --config configs/config.yml

preprocess:
    python -m src.preprocessing_02.run_preprocessing --config configs/config.yml

core:
    python -m src.core_03.chunk_orchestrator --config configs/config.yml

branch2:
    make download
    make preprocess
    make core
```

---

## Branch Policy

This README applies only to Branch 2.

- Stage 1 may fail
- Stage 2 must pass
- Stage 3 must run deterministically
- Main branch must remain stable
- This branch is safe to push

---

## What’s Different From Branch 1 (Branch 2 Snapshot)

Branch 2 introduces real ingestion, real preprocessing, and a real parallel processing engine.

Key differences:

- Multi‑stage pipeline
- CDS API client with retries
- Config‑driven ingestion
- Directory validation
- Structured metadata
- Deterministic preprocessing
- Parallel chunk processing
- Structured logging

Branch 1 = MVP
Branch 2 = real pipeline
Branch 3 = distributed parallelization

---

## Summary

This push represents:

- A stable Stage 2
- A fully implemented Stage 3
- A partially complete Stage 1
- A correct feature-branch workflow
- A clean snapshot for engineering review and recruiter visibility
