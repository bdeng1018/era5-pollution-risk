# Pipeline Flow — ERA5 Pollution‑Risk Pipeline (Branch 1)

This document explains how data moves through the ERA5 Pollution‑Risk Pipeline (Branch 1).
It provides a stage‑by‑stage walkthrough of the execution flow, the artifacts produced, and how each stage depends on the previous one.

---

## 1. Overview

The pipeline processes monthly ERA5 reanalysis data through five deterministic stages:

```text
Stage 01 → Stage 02 → Stage 03 → Stage 04 → Stage 05
```

Each stage is reproducible, diagnosable, and produces well‑defined artifacts under `data/`.

---

## 2. End‑to‑End Flow Diagram

```text
                ┌──────────────────────────────┐
                │         Raw ERA5 GRIB        │
                └───────────────┬──────────────┘
                                │
                                ▼
        ┌────────────────────────────────────────────────┐
        │         Stage 01 — Download ERA5 GRIB          │
        │  - Fetch monthly ERA5 GRIB files               │
        │  - Skip existing artifacts                     │
        │  - Store under data/raw/era5/<year>/<month>/   │
        └───────────────┬────────────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────────────────────┐
        │     Stage 02 — Preprocessing (GRIB → Parquet)  │
        │  - Unzip GRIB archives                         │
        │  - Inspect GRIB metadata                       │
        │  - Convert GRIB → Parquet                      │
        │  - Store under data/intermediate/<year>/<month>│
        └───────────────┬────────────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────────────────────┐
        │       Stage 03 — Feature Engineering           │
        │  - Identity transformation (Branch 1)          │
        │  - Store features.parquet                      │
        │  - data/features/features.parquet              │
        └───────────────┬────────────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────────────────────┐
        │         Stage 04 — Modeling (MeanPredictor)    │
        │  - Train deterministic baseline model          │
        │  - Save model.pkl under models/                │
        └───────────────┬────────────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────────────────────┐
        │         Stage 05 — Evaluation                  │
        │  - Compute MAE + RMSE                          │
        │  - Generate predictions.parquet                │
        │  - Store under data/predictions/               │
        └────────────────────────────────────────────────┘
```

---

## 3. Stage‑by‑Stage Flow

### Stage 01 → Stage 02

Stage 01 downloads monthly ERA5 GRIB files.
Stage 02 depends on these raw GRIB artifacts:

- GRIB archives are unzipped.
- GRIB metadata is inspected.
- GRIB is converted to Parquet.

If Stage 01 is skipped or incomplete, Stage 02 cannot run.

### Stage 02 → Stage 03

Stage 03 consumes the intermediate Parquet files produced by Stage 02:

- Flattened tabular representation of ERA5 GRIB
- Deterministic column structure
- No multi‑variable logic in Branch 1

Stage 03 applies an identity transformation and produces:

```code
data/features/features.parquet
```

### Stage 03 → Stage 04

Stage 04 trains the baseline **MeanPredictor** model using:

- `features.parquet` from Stage 03
- target variable defined in `configs/variables.yml`

Outputs:

```code
models/model.pkl
```

The model is deterministic and contains no learned parameters beyond the mean.

### Stage 04 → Stage 05

Stage 05 evaluates the model using:

- `model.pkl`
- `features.parquet`

It produces:

```code
data/predictions/predictions.parquet
```

Containing:

- deterministic predictions
- MAE
- RMSE
- error columns

This is the final artifact of Branch 1.

---

## 4. Artifact Flow Summary

| Stage | Input | Output |
|-------|-------|--------|
| Stage 01 | ERA5 API (cdsapi) | `data/raw/era5/<year>/<month>/*.grib` |
| Stage 02 | Raw GRIB | `data/intermediate/<year>/<month>/*.parquet` |
| Stage 03 | Intermediate Parquet | `data/features/features.parquet` |
| Stage 04 | Features | `models/model.pkl` |
| Stage 05 | Model + Features | `data/predictions/predictions.parquet` |

---

## 5. Diagnostics Flow

Diagnostics run independently of the pipeline:

```text
Stage 01 → diagnose CDS API
```

Running:

```bash
make diagnostics
```

executes all diagnostics in order.

---

## 6. Logging Flow

Branch 1 uses **lightweight console logging only**.

No stage writes logs to disk, and the directory:

```text
data/logs/
```

is **not used** in Branch 1.

Pipeline‑level summary reports and structured log files will be introduced in **Branch 2**.

---

## 7. Final Output

The final deliverable of the Branch 1 pipeline is:

```text
data/predictions/predictions.parquet
```

This file contains:

- deterministic predictions
- MAE and RMSE
- error columns
- timestamps and metadata

It is the authoritative record of the Branch 1 run.

---

## 8. Contact

Maintainer: Brian Deng <br>
Email: <bdeng.data.pipelines@gmail.com> <br>
GitHub: <https://github.com/bdeng1018>
