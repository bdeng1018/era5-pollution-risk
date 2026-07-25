# Stage 05 Design — Evaluation (Branch 1)

Stage 05 is the final stage of the ERA5 Pollution‑Risk Pipeline (Branch 1).
It evaluates the baseline deterministic model, computes regression metrics, generates predictions, and writes the final authoritative artifact of the pipeline.

This document describes the design, responsibilities, execution model, and error‑handling strategy of Stage 05.

---

## 1. Purpose of Stage 05

Stage 05 provides:

- **Deterministic evaluation** of the MeanPredictor model
- MAE and RMSE computation
- Per‑row error values
- Final predictions artifact
- Unified evaluation logging

Unlike Stages 01–04, which are linear and self‑contained, Stage 05 coordinates multiple upstream artifacts and produces the final output of Branch 1.

---

## 2. Inputs and Outputs

### Inputs

Stage 05 consumes:

| Artifact | Description |
|----------|-------------|
| `models/model.pkl` | Global mean predictor produced by Stage04 |
| `data/features/features.parquet` | Identify-transformed ERA5 features from Stage03 |

Both artifacts are required for evaluation.

### Outputs

Stage 05 produces:

```code
data/predictions/predictions.parquet
```

This file contains:

- predictions
- errors
- MAE
- RMSE
- timestamps and metadata

It is the authoritative output of Branch 1.

---

## 3. Execution Model

Stage 05 executes the following steps:

```text
Load model.pkl
↓
Load features.parquet
↓
Compute predictions
↓
Compute errors
↓
Compute MAE and RMSE
↓
Write predictions.parquet
↓
Log evaluation summary
```

All operations are deterministic and require no external services.

---

## 4. Evaluation Logic

### 4.1 Load Model

- Deserialize `model.pkl`
- Extract the global mean value (the only parameter of the MeanPredictor)

### 4.2 Load Features

- Read `features.parquet`
- Validate presence of required columns:

  - `latitude`
  - `longitude`
  - `time`
  - `value`

### 4.3 Compute Predictions

```code
prediction = global_mean
error = value - prediction
```

### 4.4 Compute Metrics

```code
mae = mean(abs(error))
rmse = sqrt(mean(error^2))
```

Metrics are stored as scalar columns repeated per row.

### 4.5 Write Output

Write `predictions.parquet` containing:

- original feature columns
- prediction
- error
- mae
- rmse

---

## 5. Output Schema

| Column | Type | Description |
|--------|------|-------------|
| `latitude` | float | Grid latitude |
| `longitude` | float | Grid longitude |
| `time` | datetime | Timestamp |
| `value` | float | Actual ERA5 value |
| `prediction` | float | Global mean prediction |
| `error` | float | Signed error |
| `mae` | float | Mean Absolute Error |
| `rmse` | float | Root Mean Square Error |

This schema defines the Branch 1 evaluation contract.

---

## 6. Determinism Guarantees

Stage 05 is fully deterministic:

- no randomness
- no parallelization
- no external dependencies
- no multi‑variable logic
- no configuration branching

Given the same inputs, Stage 05 always produces identical outputs.

---

## 7. Logging

Branch 1 uses lightweight console logging only.
File‑based logs will be introduced in Branch 2.

For Branch 2, logged events will include:

- model load success
- feature load success
- metric computation
- artifact write completion

Stage 05 does not create a separate summary artifact beyond `predictions.parquet`.

---

## 8. Failure Modes

| Failure | Cause | Resolution |
|---------|-------|------------|
| Missing model | Stage 04 not run | Run `make train` |
| Missing features | Stage 03 not run | Run `make features` |
| Missing columns | Corrupted Parquet | Re-run Stage 02/03 |
| Write failure | Permission or path issue | Validate `data/` directory |

Stage 05 uses a **fail‑fast** strategy: evaluation stops immediately on error.

---

## 9. Relationship to Branch 2

Branch 2 will expand Stage 05 to include:

- multiple regression metrics
- residual plots
- diagnostic reports
- model comparison utilities
- metadata artifacts
- multi‑variable evaluation logic

Branch 1 remains intentionally minimal.

---

## 10. Contact

Maintainer: Brian Deng <br>
Email: <bdeng.data.pipelines@gmail.com> <br>
GitHub: <https://github.com/bdeng1018>
