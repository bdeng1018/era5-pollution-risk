# Developer Onboarding — ERA5 Pollution‑Risk Pipeline (Branch 1)

Welcome to the ERA5 Pollution‑Risk Pipeline (Branch 1).
This document provides everything you need to set up your environment, run the pipeline, debug issues, and contribute code.

---

## 1. Prerequisites

Install the following:

- Python 3.10
- VS Code
- Git
- Conda *(optional - only needed for GRIB CLI tools)*

Clone the repository:

```bash
git clone https://github.com/bdeng1018/era5-pollution-risk
cd era5-pollution-risk
```

---

## 2. VS Code Workspace Setup

Open the workspace file at the repo root:

```code
era5-pollution-risk.code-workspace
```

This loads:

- `.vscode/settings.json` (formatting, linting, Python path)
- `.vscode/tasks.json` (pipeline tasks)
- `.vscode/launch.json` (debug configurations)
- `.vscode/extensions.json` (recommended extensions)

### Recommended Extensions

These are auto-loaded:

- Python + Pylance
- Black
- Ruff
- Pytest
- YAML Support
- Makefile Tools
- GitLens
- Jupyter

These ensure consistent formatting, linting, debugging, and test execution.

---

## 3. Environment Setup

### Create the project virtual environment

```bash
python3 -m venv .venv --copies
```

### Activate it

```bash
source .venv/bin/activate
```

### Install required Python packages

```bash
pip install xarray cfgrib pyarrow pandas numpy
```

### Validate the environment

```bash
make env
```

### Important Notes

- **Do NOT activate Conda for normal pipeline runs.**
Conda is optional and only needed for GRIB CLI tools (`grib_ls`, `grib_dump`).
The pipeline must run inside `.venv` to avoid conflicts with Conda’s `eccodes` and GRIB indexing.

- Branch 1 is **environment-agnostic** - smoke tests do not require CDS API credentials, network access, or real GRIB files.

### Environment Summary

- Always activate `.venv` **before** running any pipeline stage.
- Do **NOT** activate Conda unless using GRIB CLI tools.
- Branch 1 smoke tests do **not** require CDS API credentials or network access.

---

## 4. Running the Pipeline (Stages 01–05)

Branch 1 consists of **five deterministic, minimal stages**.
These stages run end‑to‑end but intentionally avoid full ingestion logic.

### Stage 01 — Download ERA5 GRIB (minimal ingestion)

```bash
make download
```

### Stage 02 — Preprocessing (GRIB → Parquet)

```bash
make preprocess
```

### Stage 03 — Feature Engineering

```bash
make features
```

### Stage 04 — Modeling

```bash
make train
```

### Stage 05 - Evaluation

```bash
make evaluate
```

### Full Pipeline

```bash
make all
```

Branch 1 runs quickly and does not require real GRIB/Parquet validation.

---

## 5. Debugging (VS Code Launchers)

Use the built‑in VS Code launch configurations defined in:

```code
.vscode/launch.json
```

Available launchers:

- Debug Stage 01 (download)
- Debug Stage 02 (preprocess — unzip / inspect / convert)
- Debug Stage 03 (features)
- Debug Stage 04 (modeling)
- Debug Stage 05 (evaluation)
- Debug current Python file

These allow step‑through debugging of each pipeline stage.

---

## 6. Testing & Linting

### Run smoke tests

```bash
make test
```

### Run linting

```bash
make lint
```

### Run formatting

```bash
make format
```

### Run full developer check (lint + tests)

```bash
make check
```

### Recommended workflow

1. Run tests
2. Run formatting
3. Run lint
4. Run check

This ensures fuctional correctness before style enforcement.

---

## 7. Resetting Pipeline Artifacts

### Safe cleanup (recommended)

```bash
make clean-cache
```

Removes caches and temporary logs.

### Full artifact reset (destructive)

```bash
make reset
```

Removes:

- intermediate Parquet
- features
- predictions
- model artifacts

Raw ERA5 GRIB files are preserved.

---

## 8. Folder Structure Overview

```code
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
configs/
diagrams/
docs/
tests/
```

This structure ensures consistency across pipelines.

---

## 9. Contributing Code

### Formatting

Black + Ruff are enforced:

```bash
make format
make lint
```

### Testing

All new code must include tests:

```bash
make test
```

### Documentation

New modules should include:

- top-level docstring headers
- clear function docstrings
- comments explaining *why*, not just *what*
- updates to `docs/` if needed

### Pull Requests

Include:

- a clear description of changes
- test coverage
- updates to diagrams or docs if relevant

Branch 1 PRs should remain minimal and deterministic.

---

## 10. Debugging Tips

### Common Issues

- **Missing GRIB files** → run Stage 01
- **Missing intermediate Parquet** → run Stage 02
- **Missing `features.parquet`** → run Stage 03
- **Missing `model.pkl`** → run Stage 04
- **Missing `predictions.parquet`** → run Stage 05

### Useful Commands

Inspect GRIB metadata:

```bash
python -m src.preprocessing_02.inspect_grib
```

Inspect intermediate Parquet:

```bash
python -m src.features_03.build_features --dry-run
```

---

## 11. Diagnostics (CDS API Connectivity)

Branch 1 includes a minimal CDS API diagnostic:

```bash
make diagnostics
```

This verifies:

- `~/.cdsapirc` authentication
- network connectivity
- cdsapi client functionality

It downloads a small NetCDF file (`test.nc`) to confirm connectivity.

---

## 12. Contact

Maintainer: **Brian Deng** <br>
Email: **<bdeng.data.pipelines@gmail.com>** <br>
GitHub: **<https://github.com/bdeng1018>**
