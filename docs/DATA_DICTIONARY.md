# Data Dictionary — ERA5 Pollution Risk Pipeline

This document defines all variables used throughout the ERA5 Pollution Risk Pipeline.
It covers the 21 raw ERA5 GRIB variables, spatial/temporal metadata, IR‑aligned tensors, and Stage 05 pollution + derived features.

## 1. Overview

The pipeline processes multiple data domains:

- 21 ERA5 meteorological variables (GRIB)
- Spatial metadata (lat/lon grid)
- Temporal metadata (timestamps, hours, days)
- IR₄ spatiotemporal tensors
- IR₅ feature tensors (including pollution variables)
- IR₆ model‑ready datasets
- IR₇ evaluation artifacts
- IR₈ deployment artifacts

This dictionary ensures **schema clarity**, **traceability**, and **reproducibility** across all stages.

## 2. Raw ERA5 GRIB Variables (21 Variables)

These variables come directly from your `data/raw/era5/<year>/<month>/` directory.

| Variable | Description | Units | Notes |
| --------- | ------------- | ------- | ------- |
| `blh` | Boundary layer height | m | Critical for pollution mixing |
| `cape` | Convective available potential energy | J/kg | Atmospheric instability |
| `cin` | Convective inhibition | J/kg | Atmospheric stability |
| `d2m` | 2‑meter dewpoint temperature | K | Used for humidity |
| `e` | Evaporation | m | Surface flux |
| `lsm` | Land‑sea mask | 0/1 | Used for coastal logic |
| `msl` | Mean sea level pressure | Pa | Optional |
| `slhf` | Surface latent heat flux | J/m² | Moisture flux |
| `sp` | Surface pressure | Pa | Normalized |
| `sshf` | Surface sensible heat flux | J/m² | Thermal flux |
| `ssr` | Surface solar radiation | J/m² | Radiation |
| `ssrd` | Surface solar radiation downwards | J/m² | Photochemistry |
| `ssrdc` | Clear‑sky solar radiation downwards | J/m² | Radiation baseline |
| `str` | Surface thermal radiation | J/m² | Longwave radiation |
| `t2m` | 2‑meter temperature | K | Converted to °C |
| `tcc` | Total cloud cover | % | Radiation effects |
| `tco3` | Total column ozone | kg/m² | Photochemical relevance |
| `tcwv` | Total column water vapor | kg/m² | Moisture content |
| `tp` | Total precipitation | m | Aggregated |
| `u10` | 10‑meter eastward wind | m/s | Dispersion |
| `v10` | 10‑meter northward wind | m/s | Dispersion |

All 21 variables are stored under:

```code
data/raw/era5/<year>/<month>/
```

## 3. Spatial Metadata (Stage 03)

Chunk engine produces spatial metadata stored under `data/chunks_metadata/`.

| Field | Description |
| ------- | ------------- |
| `lat` | Latitude coordinate |
| `lon` | Longitude coordinate |
| `grid_id` | Unique grid cell identifier |
| `chunk_id` | Spatial chunk identifier |
| `region` | Optional region label |

## 4. Temporal Metadata (Stage 03)

| Field | Description |
| ------- | ------------- |
| `timestamp` | UTC timestamp |
| `year` | Year |
| `month` | Month |
| `day` | Day |
| `hour` | Hour |
| `dayofweek` | Day of week |
| `weekofyear` | Week number |

## 5. IR₄ — Spatiotemporal Tensor Fields (Stage 04)

IR₄ tensors live under `data/spatiotemporal/`.

| Field | Description |
| ------- | ------------- |
| `era5_vars` | All normalized ERA5 variables (21 fields) |
| `mask` | Validity mask for missing data |
| `chunk_id` | Spatial chunk reference |
| `time_index` | Temporal index within chunk |
| `metadata` | Spatial + temporal metadata |

## 6. IR₅ — Feature Tensor Fields (Stage 05)

Feature engineering produces deterministic, registry‑driven derived features stored under `data/features/`.

### Temporal Features

| Feature | Description |
| --------- | ------------- |
| `t2m_roll_mean_6h` | 6‑hour rolling mean of t2m |
| `t2m_roll_mean_24h` | 24‑hour rolling mean of t2m |
| `t2m_delta_24h` | 24‑hour difference of t2m |
| `d2m_roll_mean_6h` | 6‑hour rolling mean of d2m |
| `d2m_roll_mean_24h` | 24‑hour rolling mean of d2m |
| `d2m_delta_24h` | 24‑hour difference of d2m |
| `u10_roll_mean_6h` | 6‑hour rolling mean of u10 |
| `u10_roll_mean_24h` | 24‑hour rolling mean of u10 |
| `u10_delta_24h` | 24‑hour difference of u10 |
| `v10_roll_mean_6h` | 6‑hour rolling mean of v10 |
| `v10_roll_mean_24h` | 24‑hour rolling mean of v10 |
| `v10_delta_24h` | 24‑hour difference of v10 |
| `msl_roll_mean_6h` | 6‑hour rolling mean of msl |
| `msl_roll_mean_24h` | 24‑hour rolling mean of msl |
| `msl_delta_24h` | 24‑hour difference of msl |

### Spatial Features

| Feature | Description |
| --------- | ------------- |
| `t2m_mean_3x3` | 3×3 neighborhood mean of t2m |
| `t2m_laplacian` | Laplacian of t2m |
| `d2m_mean_3x3` | 3×3 neighborhood mean of d2m |
| `d2m_laplacian` | Laplacian of d2m |
| `u10_mean_3x3` | 3×3 neighborhood mean of u10 |
| `u10_laplacian` | Laplacian of u10 |
| `v10_mean_3x3` | 3×3 neighborhood mean of v10 |
| `v10_laplacian` | Laplacian of v10 |
| `msl_mean_3x3` | 3×3 neighborhood mean of msl |
| `msl_laplacian` | Laplacian of msl |

### Composite Features

| Feature | Description |
| --------- | ------------- |
| instability_index | `t2m_delta_24h * t2m_laplacian` |
| moisture_temp_index | `(d2m_roll_mean_6h + t2m_roll_mean_6h) * d2m_mean_3x3` |
| pressure_context_index | `msl_roll_mean_24h * msl_mean_3x3` |
| wind_shear_index | `(u10_roll_mean_6h - v10_roll_mean_6h) * (u10_laplacian + v10_laplacian)` |

## 7. IR₆ — Model‑Ready Dataset Fields (Stage 06)

Stored under `data/model_ready/`.

| Field | Description |
| ------- | ------------- |
| `X` | Feature matrix |
| `y` | Target variable (pm25 or other) |
| `split` | Train/val/test label |
| `norm_params` | Normalization parameters |
| `feature_list` | Ordered list of features |

## 8. IR₇ — Evaluation Fields (Stage 07)

Stored under `data/evaluation/` and `data/predictions/`.

### Metrics

| Metric | Description |
| -------- | ------------- |
| `mae` | Mean absolute error |
| `rmse` | Root mean squared error |
| `r2` | Coefficient of determination |
| `mape` | Mean absolute percentage error |

### Residuals

| Field | Description |
| ------- | ------------- |
| `y_true` | Ground truth |
| `y_pred` | Model prediction |
| `residual` | `y_true - y_pred` |

## 9. IR₈ — Deployment Artifact Fields (Stage 08)

Stored under `data/deployment/`.

| Field | Description |
| ------- | ------------- |
| `model.pkl` | Serialized model |
| `norm.json` | Normalization parameters |
| `metadata.json` | Model metadata + lineage |
| `inference_config.yml` | API inference configuration |
| `version.txt` | Model version |

## 10. Contact

Maintainer: Brian Deng <br>
Email: <bdeng.data.pipelines@gmail.com> <br>
GitHub: <https://github.com/bdeng1018>
