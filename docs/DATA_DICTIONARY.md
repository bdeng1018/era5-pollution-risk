# Data Dictionary — ERA5 Pollution‑Risk Pipeline (Branch 1)

This document defines all columns produced by the Branch 1 ERA5 Pollution‑Risk Pipeline.
These fields represent the canonical outputs of:

- Stage 02 — GRIB → Parquet
- Stage 03 — Feature Engineering
- Stage 05 — Evaluation

Branch 1 is **single‑variable**, **deterministic**, and **environment‑agnostic**.

---

## 1. Raw GRIB (Stage 01 Input)

Raw ERA5 GRIB files contain ECMWF‑defined fields.
Branch 1 does not modify GRIB metadata.

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `t2m` | float | 2‑meter temperature (Kelvin) | Single variable used in Branch 1 |
| `latitude` | float | Grid latitude | From ERA5 GRIB |
| `longitude` | float | Grid longitude | From ERA5 GRIB |
| `time` | datetime | Timestamp of reanalysis slice | Converted by cfgrib/xarray |

---

## 2. Intermediate Parquet (Stage 02 Output)

Flattened tabular representation of GRIB.

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `latitude` | float | Grid latitude | Derived from GRIB |
| `longitude` | float | Grid longitude | Derived fromGRIB |
| `time` | datetime | Timestamp | Converted to pandas datetime |
| `value` | float | ERA5 variable value (`t2m`) | Kelvin |
| `year` | int | Year extracted from `time` | Convenience field |
| `month` | int | Month extracted from `time` | Convenience field |

---

## 3. Features Parquet (Stage 03 Output)

Branch 1 applies an identity transformation.

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `latitude` | float | Same as intermediate | - |
| `longitude` | float | Same as intermediate | - |
| `time` | datetime | Same as intermediate | - |
| `value` | float | Same as intermediate | - |
| `year` | int | Same as intermediate | - |
| `month` | int | Same as intermediate | - |

No additional features are generated in Branch 1.

---

## 4. Model Artifact (Stage 04 Output)

Baseline deterministic model.

| Artifact | Type | Description | Notes |
|----------|------|-------------|-------|
| `model.pkl` | pickle | Stores the global mean of `value` | Deterministic MeanPredictor |

---

## 5. Predictions Parquet (Stage 05 Output)

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `latitude` | float | Grid latitude | From features |
| `longitude` | float | Grid longitude | From features |
| `time` | datetime | Timestamp | From features |
| `value` | float | Actual ERA5 value | Kelvin |
| `prediction` | float | Global mean prediction | Deterministic |
| `error` | float | `value - prediction` | Signed error |
| `mae` | float | Mean Absolute Error | Constant per file |
| `rmse` | float | Root Mean Square Error | Constant per file |

---

## 6. Notes on Data Types

- **Datetime** uses ISO-8601 format
- **Floats** use decimal notation (no scientific notation)
- **Latitude/longitude** follow ECMWF grid conventions
- **Prediction metrics** are scalar values repeated per row

---

## 7. Relationship to Branch 2

Branch 2 will expand this dictionary to include:

- multi‑variable ingestion
- metadata fields
- derived meteorological features
- transformation graphs
- model provenance fields

Branch 1 remains intentionally minimal.

---

## 8. Contact

Maintainer: Brian Deng <br>
Email: <bdeng.data.pipelines@gmail.com> <br>
GitHub: <https://github.com/bdeng1018>
