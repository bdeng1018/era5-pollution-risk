# Branch 2 — ERA5 Ingestion & Preprocessing Pipeline (Development Snapshot)

Branch 2 expands the Branch 1 MVP into a multi-stage, production-aligned ERA5 ingestion and preprocessing system. This branch introduces:

- A full ingestion stage (Stage 1) with retry logic, directory validation, and config-driven execution
- A deterministic preprocessing stage (Stage 2) with stable, passing tests
- Unified logging
- Metadata generation
- Structured directory layout
- A more robust engineering architecture designed for multi-year scaling

This README documents the current development snapshot of Branch 2. It intentionally reflects the state of the branch at push time:

- Stage 1: Work-in-progress (some tests failing)
- Stage 2: Fully implemented and passing all tests
- Main branch remains stable and untouched

---

## Overview

Branch 2 introduces a two-stage ERA5 pipeline:

1. **Stage 1 — Ingestion (WIP)**
   - CDS API client
   - Retry logic
   - Directory validation (currently being debugged)
   - Config path resolution (currently being debugged)
   - Partial pytest contract coverage (some failing tests expected)

2. **Stage 2 — Preprocessing (Stable)**
   - Unzip raw ERA5 archives
   - Inspect NetCDF structure
   - Convert variables into deterministic intermediate formats
   - Generate metadata JSON
   - Validate intermediate outputs
   - All tests passing

This branch is not intended for production yet. It is a development branch where Stage 1 failures are acceptable.

---

## Branch 2 - Push 1 Directory Structure (Git-Safe)

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
│   ├── intermediate/        # empty, .gitkeep only
│   ├── logs/                # empty, .gitkeep only
│   ├── metadata/            # empty, .gitkeep only
│   └── predictions/         # empty, .gitkeep only
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
│   │   └── download_era5_single.py
│   │
│   └── preprocessing_02/
│       ├── README.md
│       ├── __init__.py
│       ├── convert_grib_to_parquet.py
│       ├── inspect_grib.py
│       ├── run_preprocessing.py
│       └── unzip_grib.py
│
└── tests/
    ├── download_01/
    │   ├── test_download_monthly.py
    │   ├── test_download_single.py
    │   ├── test_environment_validation.py
    │   ├── test_metadata_logging.py
    │   └── test_retry_logic.py
    │
    └── preprocessing_02/
        ├── test_preprocessing_acceptance.py
        ├── test_preprocessing_integration.py
        ├── test_preprocessing_regression.py
        ├── test_preprocessing_smoke.py
        ├── test_preprocessing_system.py
        └── test_preprocessing_unit.py
```

---

## Pipeline Stages

### Stage 1 — Ingestion (WIP)

Status: Partially implemented, some tests failing.

Current capabilities:

- CDS API client
- Retry logic
- Basic ingestion flow
- Initial directory validation
- Initial config path resolution

Known issues:

- Directory validation fails under certain nested layouts
- Config path resolution fails when relative paths are used
- Some pytest contracts fail due to nondeterministic external API behavior

This is expected for a feature branch.

---

### Stage 2 — Preprocessing (Stable)

Status: Fully implemented, all tests passing.

Capabilities:

- Unzip raw ERA5 archives
- Inspect NetCDF structure
- Convert variables into deterministic intermediate formats
- Generate metadata JSON
- Validate intermediate outputs
- Structured logging
- Deterministic behavior across runs

This stage is ready for production once Stage 1 stabilizes.

---

## Testing Status

| Stage     | Status | Notes |
|-----------|--------|-------|
| Stage 1   | ❌ Some failing tests | Expected during Branch 2 development |
| Stage 2   | ✅ All tests passing  | Deterministic and stable |

---

## Running the Pipeline

### 1. Configure the pipeline

Edit `config/paths.yml`:

```yaml
paths:
  raw_dir: "data/raw"
  intermediate_dir: "data/intermediate"
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

### 4. Makefile

```makefile
download:
    python -m src.download_01.download_era5_monthly --config configs/config.yml

preprocess:
    python -m src.preprocessing_02.run_preprocessing --config configs/config.yml

branch2:
    make download
    make preprocess
```

---

## Branch Policy

This README applies only to Branch 2.

At this moment:

- Stage 1 is allowed to fail
- Stage 2 must pass
- `main` must remain stable
- This branch is safe to push
- This README documents the exact state of the branch at push time

---

## What’s Different From Branch 1 (Branch 2 Snapshot)

Branch 2 is the first major expansion of the Branch 1 MVP. It introduces real ingestion, real preprocessing, and real engineering scaffolding that Branch 1 intentionally deferred.

### Key differences

- **Multi-stage pipeline**
Branch 1 had a single download + preprocess flow. Branch 2 introduces Stage 1 ingestion and Stage 2 preprocessing as separate, testable modules.

- **CDS API client + retry logic**
Branch 1 used simple download scripts. Branch 2 adds a robust ingestion client with retries, error handling, and structured logging.

- **Config-driven ingestion**
Branch 1 configs controlled only variable/year/month. Branch 2 configs control paths, logging, intermediate directories, and execution behavior.

- **Directory validation + path resolution**
Branch 2 introduces production-grade directory validation and path resolution (currently being debugged).

- **Metadata generation**
Branch 1 produced minimal metadata. Branch 2 generates structured metadata JSON for every preprocessing run.

- **Deterministic preprocessing**
Branch 2’s Stage 2 is fully deterministic and passes all tests.

- **Pytest contract suite**
Branch 1 had smoke tests only. Branch 2 introduces contract tests for ingestion and preprocessing.

- **Structured logging**
Branch 2 logs ingestion and preprocessing events to `logs/`.

### Why this matters

This section makes it clear that:

- Branch 1 = MVP
- Branch 2 = real pipeline engineering
- Branch 3 = parallelization + multi-year scaling

It shows progression, maturity, and intentional design.

---

## Summary

This push represents:

- A stable Stage 2
- A partially complete Stage 1
- A correct feature-branch workflow
- A clean snapshot for engineering review and recruiter visibility
