# Architecture Overview — ERA5 Pollution Risk Pipeline

This document describes the high‑level architecture of the ERA5 Pollution Risk Pipeline.
It explains how the system is structured, how each stage interacts, and how data flows from raw ERA5 ingestion to final deployment artifacts and API inference.

---

## 1. Architectural Goals

The pipeline is designed to:

- Download ERA5 + pollution datasets reliably
- Apply deterministic preprocessing and harmonization
- Build spatial and temporal chunk metadata
- Compile canonical IR₄ spatiotemporal tensors
- Generate reproducible IR₅ feature tensors
- Assemble IR₆ model‑ready datasets
- Produce IR₇ evaluation artifacts and predictions
- Build IR₈ deployment artifacts for inference
- Provide diagnostics at every stage
- Maintain strict separation between code, configs, data, diagrams, and tests

The architecture emphasizes **clarity**, **traceability**, **reproducibility**, and **stage isolation**.

---

## 2. High‑Level Pipeline Flow

```text
Raw ERA5 → Stage 02 → Intermediate → Stage 03 → Chunks → Stage 04 → IR₄ → Stage 05 → IR₅ → Stage 06 → IR₆ → Stage 07 → IR₇ → Stage 08 → IR₈ Deployment
```

Each stage is independent, testable, diagnosable, and produces a well‑defined IR artifact.

---

## 3. Stage Architecture

### Stage 01 — ERA5 Download

- Downloads ERA5 variables defined in `configs/era5.yml`.
- Stores raw NetCDF/GRIB/parquet files.
- Includes diagnostics verifying file availability and integrity.

**Inputs:** ERA5 API
**Outputs:** `data/raw/`

---

### Stage 02 — Preprocessing

- Cleans, harmonizes, and normalizes raw ERA5 + pollution data.
- Applies deterministic preprocessing rules.
- Produces canonical intermediate artifacts.

**Inputs:** `data/raw/`
**Outputs:** `data/intermediate/`

---

### Stage 03 — Chunk Engine

- Builds spatial and temporal chunk metadata.
- Generates chunked datasets for efficient compilation.
- Includes diagnostics validating chunk completeness and boundaries.

**Inputs:** Intermediate artifacts
**Outputs:**

- `data/chunks/`
- `data/chunks_metadata/`

---

### Stage 04 — Spatiotemporal Compiler

- Compiles IR₄ canonical spatiotemporal tensors.
- Applies grid logic, masks, and chunk stitching.
- Includes diagnostics verifying tensor shape, completeness, and metadata.

**Inputs:** Chunk engine outputs
**Outputs:** `data/spatiotemporal/` (IR₄)

---

### Stage 05 — Feature Engineering

- Generates IR₅ feature tensors.
- Applies derived features, composites, aggregations.
- Includes diagnostics validating feature completeness and schema.

**Inputs:** IR₄ tensors
**Outputs:** `data/features/` (IR₅)

---

### Stage 06 — Modeling

- Builds IR₆ model‑ready datasets.
- Applies normalization, train/val/test splits.
- Includes diagnostics verifying dataset integrity.

**Inputs:** IR₅ features
**Outputs:** `data/model_ready/` (IR₆)

---

### Stage 07 — Evaluation

- Runs evaluation metrics, residuals, calibration curves.
- Generates predictions and evaluation reports.
- Includes diagnostics validating metrics and prediction outputs.

**Inputs:** IR₆ datasets + trained model
**Outputs:**

- `data/evaluation/` (IR₇)
- `data/predictions/` (IR₇)

---

### Stage 08 — Deployment

- Builds IR₈ deployment artifacts.
- Packages model, normalization, metadata, and inference config.
- Includes diagnostics verifying deployment readiness.

**Inputs:** IR₇ evaluation + trained model
**Outputs:** `data/deployment/` (IR₈)

---

## 4. Directory Structure

```text
src/
  download_01/
  preprocessing_02/
  core_03/
  spatiotemporal_04/
  features_05/
  modeling_06/
  evaluation_07/
  deployment_08/
  api/
  utils/

scripts/
  diagnostics/

data/
  raw/
  intermediate/
  chunks/
  chunks_metadata/
  spatiotemporal/
  features/
  model_ready/
  evaluation/
  predictions/
  deployment/
  logs/
  metadata/

configs/
diagrams/
tests/
docs/
.vscode/
Makefile
```

This structure enforces strict separation of:

- **Code** (`src/`)
- **Diagnostics** (`scripts/diagnostics/`)
- **Configuration** (`configs/`)
- **Artifacts** (`data/`)
- **Developer documentation** (`docs/`)
- **Tooling** (`.vscode/`)
- **Build orchestration** (`Makefile`)

---

## 5. Configuration Architecture

All pipeline configuration lives in:

```code
configs/*.yml
```

Key responsibilities:

- Define ERA5 variables and years
- Configure paths and output directories
- Provide stage‑specific parameters
- Support full pipeline orchestration

Configuration is intentionally minimal and declarative.

---

## 6. Diagnostics Architecture

Every stage includes a dedicated diagnostics module:

```code
scripts/diagnostics/<stage>/
```

Diagnostics validate:

- Input availability
- Output correctness
- Schema consistency
- Artifact completeness
- Logical invariants

Diagnostics are runnable independently or via:

```bash
make diagnostics
```

This ensures the pipeline is always in a valid state.

---

## 7. Makefile Architecture

The Makefile provides:

- Stage runners (`make stage01` → `make stage08`)
- Full diagnostics (`make diagnostics`)
- Testing (`make test`)
- Linting (`make lint`)
- Safe cleanup (`make clean-cache`)
- Artifact reset (`make reset`)
- Environment setup (`make env`)

It is the primary developer interface for running the pipeline.

---

## 8. Logging Architecture

The pipeline uses stage‑specific log files under:

```text
data/logs/
```

Logs capture:

- stage execution order
- success/failure status
- timestamps
- diagnostic results

Logging remains stage‑scoped to preserve clarity and traceability.

---

## 9. Testing Architecture

All tests live in:

```code
tests/
```

Tests cover:

- Stage logic
- Diagnostics behavior
- Schema consistency
- Tensor correctness
- Feature generation
- Modeling and evaluation
- Deployment artifact integrity

Run via:

```bash
make test
```

---

## 10. Extensibility

The architecture supports:

- Adding new ERA5 variables
- Adding new derived features
- Adding new model families
- Adding new diagnostics
- Adding new deployment targets
- Adding new pipeline configurations

Each stage is isolated, making extension straightforward.

---

## 11. Contact

Maintainer: Brian Deng <br>
Email: <bdeng.data.pipelines@gmail.com> <br>
GitHub: <https://github.com/bdeng1018>
