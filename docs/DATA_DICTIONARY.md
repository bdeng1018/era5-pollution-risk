# Data Dictionary — ERA5 Pollution Risk Pipeline

This document defines all variables used throughout the ERA5 Pollution Risk Pipeline.
It covers the 21 raw ERA5 GRIB variables, spatial/temporal metadata, IR‑aligned tensors, and Stage 05 pollution + derived features.

---

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

---

## 2. Raw ERA5 GRIB Variables (21 Variables)

These variables come directly from your `data/raw/era5/<year>/<month>/` directory.

| Variable | Description | Units | Notes |
|---------|-------------|-------|-------|
| `blh`   | Boundary layer height | m | Critical for pollution mixing |
| `cape`  | Convective available potential energy | J/kg | Atmospheric instability |
| `cin`   | Convective inhibition | J/kg | Atmospheric stability |
| `d2m`   | 2‑meter dewpoint temperature | K | Used for humidity |
| `e`     | Evaporation | m | Surface flux |
| `lsm`   | Land‑sea mask | 0/1 | Used for coastal logic |
| `msl`   | Mean sea level pressure | Pa | Optional |
| `slhf`  | Surface latent heat flux | J/m² | Moisture flux |
| `sp`    | Surface pressure | Pa | Normalized |
| `sshf`  | Surface sensible heat flux | J/m² | Thermal flux |
| `ssr`   | Surface solar radiation | J/m² | Radiation |
| `ssrd`  | Surface solar radiation downwards | J/m² | Photochemistry |
| `ssrdc` | Clear‑sky solar radiation downwards | J/m² | Radiation baseline |
| `str`   | Surface thermal radiation | J/m² | Longwave radiation |
| `t2m`   | 2‑meter temperature | K | Converted to °C |
| `tcc`   | Total cloud cover | % | Radiation effects |
| `tco3`  | Total column ozone | kg/m² | Photochemical relevance |
| `tcwv`  | Total column water vapor | kg/m² | Moisture content |
| `tp`    | Total precipitation | m | Aggregated |
| `u10`   | 10‑meter eastward wind | m/s | Dispersion |
| `v10`   | 10‑meter northward wind | m/s | Dispersion |

All 21 variables are stored under:

```code
data/raw/era5/<year>/<month>/
```

---

## 3. Spatial Metadata (Stage 03)

Chunk engine produces spatial metadata stored under `data/chunks_metadata/`.

| Field | Description |
|-------|-------------|
| `lat` | Latitude coordinate |
| `lon` | Longitude coordinate |
| `grid_id` | Unique grid cell identifier |
| `chunk_id` | Spatial chunk identifier |
| `region` | Optional region label |

---

## 4. Temporal Metadata (Stage 03)

| Field | Description |
|-------|-------------|
| `timestamp` | UTC timestamp |
| `year` | Year |
| `month` | Month |
| `day` | Day |
| `hour` | Hour |
| `dayofweek` | Day of week |
| `weekofyear` | Week number |

---

## 5. IR₄ — Spatiotemporal Tensor Fields (Stage 04)

IR₄ tensors live under `data/spatiotemporal/`.

| Field | Description |
|-------|-------------|
| `era5_vars` | All normalized ERA5 variables (21 fields) |
| `mask` | Validity mask for missing data |
| `chunk_id` | Spatial chunk reference |
| `time_index` | Temporal index within chunk |
| `metadata` | Spatial + temporal metadata |

---

## 6. IR₅ — Feature Tensor Fields (Stage 05)

Feature engineering produces derived features stored under `data/features/`.

### Meteorological Features

| Feature | Description |
|---------|-------------|
| `temp_celsius` | `t2m - 273.15` |
| `dewpoint_celsius` | `d2m - 273.15` |
| `wind_speed_10m` | `sqrt(u10² + v10²)` |
| `wind_direction_10m` | `atan2(v10, u10)` |
| `humidity_ratio` | Derived from dewpoint + temperature |
| `precip_rate` | Hourly precipitation rate |
| `solar_flux` | Normalized SSRD |
| `cloud_cover` | Normalized TCC |
| `boundary_layer_height` | Normalized BLH |

### Pollution Variables (Stage 05 Only)

Pollution variables enter the pipeline **only during feature engineering**, not as raw inputs.

| Variable | Description | Units |
|---------|-------------|-------|
| `pm25` | Fine particulate matter | µg/m³ |
| `o3` | Ozone | ppb |
| `no2` | Nitrogen dioxide | ppb |
| `so2` | Sulfur dioxide | ppb |
| `co` | Carbon monoxide | ppm |

### Pollution‑Driven Features

| Feature | Description |
|---------|-------------|
| `pm25_lag_1h` | 1‑hour lag |
| `pm25_lag_24h` | 24‑hour lag |
| `pm25_rolling_mean_24h` | Rolling mean |
| `pm25_rolling_std_24h` | Rolling std |
| `o3_photochemical_index` | Derived from solar flux + humidity |

### Composite Features

| Feature | Description |
|---------|-------------|
| `dispersion_index` | `wind_speed_10m * blh` |
| `stagnation_index` | `1 / (wind_speed_10m * blh)` |
| `mixing_potential` | `blh * temp_celsius` |

---

## 7. IR₆ — Model‑Ready Dataset Fields (Stage 06)

Stored under `data/model_ready/`.

| Field | Description |
|-------|-------------|
| `X` | Feature matrix |
| `y` | Target variable (pm25 or other) |
| `split` | Train/val/test label |
| `norm_params` | Normalization parameters |
| `feature_list` | Ordered list of features |

---

## 8. IR₇ — Evaluation Fields (Stage 07)

Stored under `data/evaluation/` and `data/predictions/`.

### Metrics

| Metric | Description |
|--------|-------------|
| `mae` | Mean absolute error |
| `rmse` | Root mean squared error |
| `r2` | Coefficient of determination |
| `mape` | Mean absolute percentage error |

### Residuals

| Field | Description |
|-------|-------------|
| `y_true` | Ground truth |
| `y_pred` | Model prediction |
| `residual` | `y_true - y_pred` |

---

## 9. IR₈ — Deployment Artifact Fields (Stage 08)

Stored under `data/deployment/`.

| Field | Description |
|-------|-------------|
| `model.pkl` | Serialized model |
| `norm.json` | Normalization parameters |
| `metadata.json` | Model metadata + lineage |
| `inference_config.yml` | API inference configuration |
| `version.txt` | Model version |

---

## 10. Contact

Maintainer: Brian Deng <br>
Email: <bdeng.data.pipelines@gmail.com> <br>
GitHub: <https://github.com/bdeng1018>
