# Architecture Overview - ERA5 Pollution-Risk Pipeline (Branch 1 MVP)

The ERA5 Pollution‑Risk Pipeline (Branch 1) is a deterministic, single‑variable processing pipeline designed to ingest monthly ERA5 reanalysis data, convert GRIB files into analysis‑ready Parquet tables, generate baseline features, train a simple statistical model, and produce evaluation metrics and predictions.

Branch 1 establishes the foundational structure for future multi‑variable, multi‑region, and ML‑driven expansions in Branch 2.

---

## 1. Pipeline Structure

The pipeline consists of **five sequential stages**, each implemented as a dedicated module under `src/` and orchestrated via the project Makefile.

| Stage | Directory | Description |
|-------|-----------|-------------|
| **01 — Download** | `src/download_01/` | Retrieve monthly ERA5 GRIB files using `cdsapi`. |
| **02 — Preprocessing** | `src/preprocessing_02/` | Unzip GRIB archives, inspect metadata, and convert GRIB → Parquet. |
| **03 — Feature Engineering** | `src/features_03/` | Build ML‑ready features from intermediate Parquet files. |
| **04 — Modeling** | `src/modeling_04/` | Train the baseline deterministic MeanPredictor model. |
| **05 — Evaluation** | `src/evaluation_05/` | Compute evaluation metrics and generate predictions. |

Each stage is deterministic and produces well‑defined artifacts under `data/`.

---

## 2. Data Flow

The pipeline transforms ERA5 data through a linear sequence of artifacts:

### 1. Raw GRIB

- Downloaded monthly via `cdsapi`
- Stored under `data/raw/era5/`

### 2. Intermediate Parquet

- Flattened tabular representation
- Stored under `data/intermediate/`

### 3. Features

- Identity transformation (Branch 1)
- Stored under `data/features/`

### 4. Model Artifact

- Baseline MeanPredictor
- Stored under `models/`

### 5. Predictions

- Deterministic predictions + errors
- Stored under `data/predictions/`

This flow is illustrated in `diagrams/data_flow_overview.md`.

---

## 3. Execution Model

The pipeline is executed via the Makefile:

- `make env` — environment validation
- `make download` — Stage 01
- `make preprocess` — Stage 02
- `make features` — Stage 03
- `make train` — Stage 04
- `make evaluate` — Stage 05
- `make all` — full pipeline

All stages are idempotent and safe to re‑run.

---

## 4. Environment Requirements (Branch 1)

Branch 1 must be run inside the project virtual environment:

```bash
source .venv/bin/activate
```

Do **NOT** activate Conda for pipeline execution.
Conda is optional and only required for GRIB CLI tools (`grib_ls`, `grib_dump`).
All pipeline stages use Python packages installed in `.venv` and do not rely on Conda environments.

Branch 1 is designed to be fast, deterministic, and environment‑agnostic.
Running inside `.venv` ensures consistent behavior across machines.

---

## 5. Directory Layout

```text
src/
  download_01/
  preprocessing_02/
  features_03/
  modeling_04/
  evaluation_05/
data/
  raw/era5/
  intermediate/
  features/
  predictions/
models/
diagrams/
docs/
```

This structure ensures consistency across pipelines.

---

## 6. Configuration Architecture

Branch 1 uses **minimal configuration**, stored under:

```text
configs/
```

Typical files include:

- `variables.yml` — ERA5 variable definitions
- `paths.yml` — directory and artifact paths
- `region.yml` — bounding box configuration

Configuration is intentionally simple and declarative, reflecting Branch 1’s MVP scope.

---

## 7. Logging Architecture

Branch 1 uses **lightweight console logging only** through shared utilities in
`src/utils/`. No stage writes logs to disk, and the directory:

```text
data/logs/
```

is **not used** in Branch 1.

Examples such as `download.log`, `preprocess.log`, `features.log`, `model.log`,
and `evaluation.log` will be introduced in **Branch 2**, along with structured
logging, run metadata, and pipeline‑level summary reports.

Branch 1 does **not** include a pipeline‑level summary report or orchestrator.

---

## 8. Testing Architecture

All tests live under:

```text
tests/
```

Branch 1 tests cover:

- module import stability
- minimal execution correctness
- deterministic model behavior
- basic artifact existence

Run via:

```bash
make test
```

Branch 1 intentionally avoids:

- schema validation
- metadata extraction
- skip‑logic correctness
- multi‑variable ingestion tests

These arrive in Branch 2.

---

## 9. Makefile Architecture

The Makefile provides the primary developer interface:

- Stage runners (`make download` → `make evaluate`)
- Full pipeline (`make all`)
- Linting (`make lint`)
- Formatting (`make format`)
- Testing (`make test`)
- Cache cleanup (`make clean-cache`)
- Artifact reset (`make reset`)
- Environment validation (`make env`)
- Diagnostics (`make diagnostics`)

This ensures reproducible execution across machines.

---

## 10. Extensibility

Branch 1 is intentionally minimal but designed for expansion:

- Additional ERA5 variables
- Multi‑region ingestion
- Transformation graphs
- Advanced ML models
- Diagnostics and reporting layers
- Containerization
- Experiment tracking (MLflow)

Branch 2 will introduce these capabilities.

---

## 11. Maintainer

**Brian Deng** <br>
Email: **<bdeng.data.pipelines@gmail.com>** <br>
GitHub: **<https://github.com/bdeng1018>**
