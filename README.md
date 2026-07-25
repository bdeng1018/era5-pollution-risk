# ERA5 Pollution‑Risk Pipeline (Branch 1 MVP)

A modular, reproducible, and production‑aligned pipeline for transforming ERA5 reanalysis data into pollution‑risk insights. Branch 1 delivers a minimal but fully operational foundation: single‑variable ingestion, preprocessing, feature engineering, baseline modeling, and evaluation. The architecture is designed for clarity today and scalability tomorrow.

---

## Overview

This repository implements a **config‑driven, stage‑based pipeline** for ERA5 data processing. Branch 1 focuses on a **single month** and **one key variable**, validating the end‑to‑end engineering workflow used in climate analytics, environmental risk modeling, and geospatial ML systems.

The pipeline is orchestrated via a Makefile, structured into isolated stages, and built for deterministic execution. Detailed documentation for each stage lives in `docs/` and in the stage‑specific READMEs under `src/`.

---

## Key Capabilities (Branch 1)

- ERA5 single‑variable GRIB ingestion
- GRIB inspection and conversion to Parquet
- Lightweight feature engineering
- Baseline model training and prediction
- Basic evaluation metrics
- Smoke‑test validation
- Notebook‑based exploratory analysis

These components establish the core architecture that Branch 2 will scale into a multi‑year, multi‑variable, production‑grade system.

---

## Project structure

```code
configs/               YAML configuration (paths, variables, years, months, region)
data/                  Raw ERA5, intermediate Parquet, features, predictions
diagrams/              Pipeline diagrams
models/                Baseline model artifacts
notebooks/             Exploratory analysis (Branch 1)
scripts/diagnostics/   Developer environment checks
src/                   Pipeline source code (stages 01–05 + utils)
tests/                 Smoke tests
```

---

## Running the Pipeline

### 1. Download the single‑variable ERA5 GRIB

```bash
python -m src.download_01.download_era5_single
```

### 2. Execute all stages

```bash
make all
```

### 3. Run smoke tests

```bash
make test
```

### 4. Explore outputs

```code
notebooks/branch1_eda.ipynb
```

---

## Configuration

All settings live in `configs/`:

- **[paths](configs/paths.yml)**
- **[variables](configs/variables.yml)**
- **[years](configs/years.yml)**
- **[months](configs/months.yml)**
- **[region](configs/region.yml)**

Branch 1 ships with working defaults. Editing configs is optional.

---

## Branch 2 Preview

Branch 2 will introduce:

- Multi‑year, multi‑variable ingestion
- Advanced feature engineering
- Real ML models + tuning
- Residual analysis and diagnostics
- Dashboards and reporting
- MLflow experiment tracking
- Docker + CI/CD
- Structured logging and metadata

Branch 1 intentionally keeps the foundation minimal and focused.

---

## 📬 Maintainer

**Brian Deng**
Los Angeles, CA

**Focus:**

- Climate analytics
- Hazard‑risk modeling
- ERA5‑based pipelines and geospatial workflows
- Scalable ML/data engineering for environmental systems
- Pollution‑risk analytics for environmental and health exposure
