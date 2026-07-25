# Pipeline Flow — ERA5 Pollution Risk Pipeline

This document explains how data moves through the ERA5 Pollution Risk Pipeline.
It provides a stage‑by‑stage walkthrough of the execution flow, the artifacts produced, and how each stage depends on the previous one.

---

## 1. Overview

The pipeline processes ERA5 + pollution data through eight stages:

```text
Stage 01 → Stage 02 → Stage 03 → Stage 04 → Stage 05 → Stage 06 → Stage 07 → Stage 08
```

Each stage is deterministic, diagnosable, and produces well‑defined IR artifacts.

---

## 2. End‑to‑End Flow Diagram

```text
                ┌──────────────────────────────┐
                │           Raw ERA5           │
                └───────────────┬──────────────┘
                                │
                                ▼
        ┌────────────────────────────────────────────────┐
        │         Stage 01 — ERA5 Download               │
        │  - Fetch ERA5 variables                        │
        │  - Store raw NetCDF/GRIB/parquet               │
        └───────────────┬────────────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────────────────────┐
        │        Stage 02 — Preprocessing                │
        │  - Clean + harmonize ERA5 + pollution          │
        │  - Normalize variables                         │
        └───────────────┬────────────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────────────────────┐
        │        Stage 03 — Chunk Engine                 │
        │  - Build spatial/temporal chunks               │
        │  - Generate chunk metadata                     │
        └───────────────┬────────────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────────────────────┐
        │   Stage 04 — Spatiotemporal Compiler (IR₄)     │
        │  - Compile canonical tensors                   │
        │  - Apply grid/mask logic                       │
        └───────────────┬────────────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────────────────────┐
        │     Stage 05 — Feature Engineering (IR₅)       │
        │  - Derived features + composites               │
        │  - Aggregations + transforms                   │
        └───────────────┬────────────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────────────────────┐
        │       Stage 06 — Modeling (IR₆)                │
        │  - Train/val/test splits                       │
        │  - Normalization + dataset assembly            │
        └───────────────┬────────────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────────────────────┐
        │       Stage 07 — Evaluation (IR₇)              │
        │  - Metrics + residuals + predictions           │
        │  - Evaluation reports                          │
        └───────────────┬────────────────────────────────┘
                        │
                        ▼
        ┌────────────────────────────────────────────────┐
        │       Stage 08 — Deployment (IR₈)              │
        │  - Package model + normalization               │
        │  - Build inference artifacts                   │
        └────────────────────────────────────────────────┘
```

---

## 3. Stage‑by‑Stage Flow

### Stage 01 → Stage 02

Stage 02 depends on Stage 01:

- Stage 01 downloads raw ERA5 variables.
- Stage 02 cleans, harmonizes, and normalizes them.

This ensures preprocessing always reflects real downloaded data.

### Stage 02 → Stage 03

Stage 03 uses:

- intermediate artifacts from Stage 02
- normalized variables
- pollution + ERA5 harmonized fields

Chunking requires consistent spatial/temporal alignment.

### Stage 03 → Stage 04

Stage 04 consumes Stage 03’s chunk outputs:

- chunked tensors
- chunk metadata
- spatial/temporal boundaries

These artifacts drive the spatiotemporal compiler.

### Stage 04 → Stage 05

Stage 05 uses IR₄ canonical tensors to generate IR₅ features:

- composites
- derived features
- aggregations
- transforms

Feature engineering depends on IR₄ consistency.

### Stage 05 → Stage 06

Stage 06 consumes IR₅ feature tensors:

- builds IR₆ model‑ready datasets
- applies normalization
- creates train/val/test splits

### Stage 06 → Stage 07

Stage 07 uses IR₆ datasets + trained model:

- metrics
- residuals
- predictions
- evaluation reports

### Stage 07 → Stage 08

Stage 08 packages IR₇ evaluation + trained model into IR₈ deployment artifacts:

- model weights
- normalization rules
- inference config
- metadata

These artifacts power the API server.

---

## 4. Artifact Flow Summary

| Stage | Input | Output |
|-------|-------|--------|
| Stage 01 | ERA5 API | `raw/era5/` |
| Stage 02 | Raw ERA5 + pollution | `intermediate/` |
| Stage 03 | Intermediate | `chunks/`, `chunks_metadata/` |
| Stage 04 | Chunks | `spatiotemporal/` (IR₄) |
| Stage 05 | IR₄ | `features/` (IR₅) |
| Stage 06 | IR₅ | `model_ready/` (IR₆) |
| Stage 07 | IR₆ + model | `evaluation/` (IR₇), `predictions/` (IR₇) |
| Stage 08 | IR₇ + model | `deployment/` (IR₈) |

---

## 5. Diagnostics Flow

Diagnostics run in parallel with the pipeline:

```code
Stage 01 → diag-stage01
Stage 02 → diag-stage02
Stage 03 → diag-stage03
Stage 04 → diag-stage04
Stage 05 → diag-stage05
Stage 06 → diag-stage06
Stage 07 → diag-stage07
Stage 08 → diag-stage08
```

Running:

```bash
make diagnostics
```

executes all of them in order.

---

## 6. Logging Flow

Logs are stage‑specific:

```code
data/logs/stage01.log
data/logs/stage02.log
data/logs/stage03.log
data/logs/stage04.log
data/logs/stage05.log
data/logs/stage06.log
data/logs/stage07.log
data/logs/stage08.log
```

Each log captures:

- stage execution order
- success/failure
- timestamps
- diagnostic results

---

## 7. Final Output

The final deliverables of the pipeline are IR₈ deployment artifacts:

```code
data/deployment/
```

These artifacts include:

- model weights
- normalization rules
- inference configuration
- metadata
- versioning information

They are consumed by the API server for production inference.

---

## 8. Contact

Maintainer: Brian Deng <br>
Email: <bdeng.data.pipelines@gmail.com> <br>
GitHub: <https://github.com/bdeng1018>
